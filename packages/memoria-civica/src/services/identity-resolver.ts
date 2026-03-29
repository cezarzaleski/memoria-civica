import type {
  IdentityQuery,
  IdentityResolution,
  ResolvedCandidate
} from "@/domain/models";
import type { OfficialIdentitySource } from "@/source-connectors/mcp-brasil";

export interface IdentityResolver {
  resolve(query: IdentityQuery): Promise<IdentityResolution>;
}

interface InMemoryIdentityResolverOptions {
  readonly catalog?: readonly ResolvedCandidate[];
  readonly sources?: readonly OfficialIdentitySource[];
}

function normalizeToken(value: string): string {
  return value
    .normalize("NFD")
    .replace(/\p{Diacritic}/gu, "")
    .toLowerCase()
    .replace(/\s+/g, " ")
    .trim();
}

function candidateNames(candidate: ResolvedCandidate): readonly string[] {
  return [candidate.canonical_name, ...(candidate.aliases ?? [])];
}

function matchesName(candidate: ResolvedCandidate, queryName: string): boolean {
  return candidateNames(candidate).some((name) => normalizeToken(name) === queryName);
}

function filterByHints(
  candidates: readonly ResolvedCandidate[],
  query: IdentityQuery
): readonly ResolvedCandidate[] {
  return candidates.filter((candidate) => {
    const sameOffice = candidate.office === query.office;
    const sameUf =
      query.uf === undefined ||
      normalizeToken(candidate.uf ?? "") === normalizeToken(query.uf);
    const sameParty =
      query.party === undefined ||
      normalizeToken(candidate.party ?? "") === normalizeToken(query.party);

    return sameOffice && sameUf && sameParty;
  });
}

async function collectFromSources(
  sources: readonly OfficialIdentitySource[],
  query: IdentityQuery
): Promise<readonly ResolvedCandidate[]> {
  const allCandidates = await Promise.all(
    sources.map((source) => source.searchCandidates(query))
  );

  return allCandidates.flat();
}

export class InMemoryIdentityResolver implements IdentityResolver {
  private readonly catalog: readonly ResolvedCandidate[];

  private readonly sources: readonly OfficialIdentitySource[];

  public constructor(options: InMemoryIdentityResolverOptions = {}) {
    this.catalog = options.catalog ?? [];
    this.sources = options.sources ?? [];
  }

  public async resolve(query: IdentityQuery): Promise<IdentityResolution> {
    const normalizedName = normalizeToken(query.name);
    const sourcedCandidates = await collectFromSources(this.sources, query);
    const combinedCatalog = [...this.catalog, ...sourcedCandidates];
    const namedMatches = combinedCatalog.filter((candidate) =>
      matchesName(candidate, normalizedName)
    );
    const narrowedMatches = filterByHints(namedMatches, query);

    if (narrowedMatches.length === 1) {
      return {
        ambiguity_level: "none",
        candidate: narrowedMatches[0],
        kind: "resolved",
        match_count: 1
      };
    }

    if (narrowedMatches.length > 1) {
      return {
        ambiguity_level: "strong",
        candidates: narrowedMatches,
        kind: "ambiguous",
        match_count: narrowedMatches.length,
        requires: [
          ...(query.uf === undefined ? (["uf"] as const) : []),
          ...(query.party === undefined ? (["party"] as const) : [])
        ]
      };
    }

    if (namedMatches.length > 1) {
      return {
        ambiguity_level: "strong",
        candidates: namedMatches,
        kind: "ambiguous",
        match_count: namedMatches.length,
        requires: [
          ...(query.uf === undefined ? (["uf"] as const) : []),
          ...(query.party === undefined ? (["party"] as const) : [])
        ]
      };
    }

    return {
      ambiguity_level: "strong",
      kind: "not_found",
      match_count: 0
    };
  }
}
