import type {
  CacheEntryRecord,
  IdentityQuery,
  IdentityResolution,
  ResolvedCandidate
} from "@/domain/models";
import {
  InMemoryCacheStore,
  type CacheStore
} from "@/services/cache-store";
import type { OfficialIdentitySource } from "@/source-connectors/mcp-brasil";

export interface IdentityResolver {
  resolve(query: IdentityQuery): Promise<IdentityResolution>;
}

interface InMemoryIdentityResolverOptions {
  readonly cacheStore?: CacheStore;
  readonly cacheTtlMs?: number;
  readonly catalog?: readonly ResolvedCandidate[];
  readonly sources?: readonly OfficialIdentitySource[];
}

function normalizeOptionalToken(value?: string): string | undefined {
  if (value === undefined) {
    return undefined;
  }

  const normalized = normalizeToken(value);
  return normalized === "" ? undefined : normalized;
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

function haveSameOfficialId(
  left: ResolvedCandidate,
  right: ResolvedCandidate
): boolean {
  return (
    (left.official_ids.camara_id !== undefined &&
      left.official_ids.camara_id === right.official_ids.camara_id) ||
    (left.official_ids.tse_id !== undefined &&
      left.official_ids.tse_id === right.official_ids.tse_id) ||
    (left.official_ids.mcp_brasil_id !== undefined &&
      left.official_ids.mcp_brasil_id === right.official_ids.mcp_brasil_id)
  );
}

function isSameCandidate(
  left: ResolvedCandidate,
  right: ResolvedCandidate
): boolean {
  if (haveSameOfficialId(left, right)) {
    return true;
  }

  return (
    normalizeToken(left.canonical_name) === normalizeToken(right.canonical_name) &&
    left.office === right.office &&
    normalizeOptionalToken(left.uf) === normalizeOptionalToken(right.uf) &&
    normalizeOptionalToken(left.party) === normalizeOptionalToken(right.party)
  );
}

function mergeStatus(
  left: ResolvedCandidate["status"],
  right: ResolvedCandidate["status"]
): ResolvedCandidate["status"] {
  if (left === "incumbent" || right === "incumbent") {
    return "incumbent";
  }

  if (left === "challenger" || right === "challenger") {
    return "challenger";
  }

  return "former";
}

function mergeCandidates(
  candidates: readonly ResolvedCandidate[]
): readonly ResolvedCandidate[] {
  return candidates.reduce<ResolvedCandidate[]>((merged, candidate) => {
    const existingIndex = merged.findIndex((entry) => isSameCandidate(entry, candidate));

    if (existingIndex === -1) {
      merged.push(candidate);
      return merged;
    }

    const existing = merged[existingIndex];
    const aliases = [...new Set([...(existing.aliases ?? []), ...(candidate.aliases ?? [])])];

    merged[existingIndex] = {
      ambiguity_level: existing.ambiguity_level === "none" ? candidate.ambiguity_level : existing.ambiguity_level,
      aliases: aliases.length > 0 ? aliases : undefined,
      canonical_name:
        existing.status === "incumbent" ? existing.canonical_name : candidate.canonical_name,
      office: existing.office,
      official_ids: {
        ...existing.official_ids,
        ...candidate.official_ids
      },
      party: existing.party ?? candidate.party,
      status: mergeStatus(existing.status, candidate.status),
      uf: existing.uf ?? candidate.uf
    };

    return merged;
  }, []);
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

function buildIdentityCacheKey(query: IdentityQuery): string {
  return JSON.stringify({
    name: normalizeToken(query.name),
    office: query.office,
    party: normalizeOptionalToken(query.party) ?? null,
    uf: normalizeOptionalToken(query.uf) ?? null
  });
}

function cloneIdentityResolution(resolution: IdentityResolution): IdentityResolution {
  return JSON.parse(JSON.stringify(resolution)) as IdentityResolution;
}

export class InMemoryIdentityResolver implements IdentityResolver {
  private readonly cacheStore: CacheStore;

  private readonly cacheTtlMs: number;

  private readonly catalog: readonly ResolvedCandidate[];

  private readonly sources: readonly OfficialIdentitySource[];

  public constructor(options: InMemoryIdentityResolverOptions = {}) {
    this.cacheStore = options.cacheStore ?? new InMemoryCacheStore();
    this.cacheTtlMs = options.cacheTtlMs ?? 5 * 60 * 1000;
    this.catalog = options.catalog ?? [];
    this.sources = options.sources ?? [];
  }

  public async resolve(query: IdentityQuery): Promise<IdentityResolution> {
    const cacheKey = buildIdentityCacheKey(query);
    const cached = this.cacheStore.get("identity", cacheKey);

    if (cached !== null) {
      return cloneIdentityResolution(cached.payload.resolution as IdentityResolution);
    }

    const normalizedName = normalizeToken(query.name);
    const sourcedCandidates = await collectFromSources(this.sources, query);
    const combinedCatalog = [...this.catalog, ...sourcedCandidates];
    const namedMatches = mergeCandidates(
      combinedCatalog.filter((candidate) => matchesName(candidate, normalizedName))
    );
    const narrowedMatches = filterByHints(namedMatches, query);

    if (narrowedMatches.length === 1) {
      const resolution: IdentityResolution = {
        ambiguity_level: "none",
        candidate: narrowedMatches[0],
        kind: "resolved",
        match_count: 1
      };

      this.cacheStore.set({
        cache_key: cacheKey,
        expires_at: new Date(Date.now() + this.cacheTtlMs).toISOString(),
        payload: {
          resolution: cloneIdentityResolution(resolution)
        },
        scope: "identity",
        stored_at: new Date().toISOString()
      } satisfies CacheEntryRecord);
      return resolution;
    }

    if (narrowedMatches.length > 1) {
      const resolution: IdentityResolution = {
        ambiguity_level: "strong",
        candidates: narrowedMatches,
        kind: "ambiguous",
        match_count: narrowedMatches.length,
        requires: [
          ...(query.uf === undefined ? (["uf"] as const) : []),
          ...(query.party === undefined ? (["party"] as const) : [])
        ]
      };

      this.cacheStore.set({
        cache_key: cacheKey,
        expires_at: new Date(Date.now() + this.cacheTtlMs).toISOString(),
        payload: {
          resolution: cloneIdentityResolution(resolution)
        },
        scope: "identity",
        stored_at: new Date().toISOString()
      } satisfies CacheEntryRecord);
      return resolution;
    }

    if (namedMatches.length > 1) {
      const resolution: IdentityResolution = {
        ambiguity_level: "strong",
        candidates: namedMatches,
        kind: "ambiguous",
        match_count: namedMatches.length,
        requires: [
          ...(query.uf === undefined ? (["uf"] as const) : []),
          ...(query.party === undefined ? (["party"] as const) : [])
        ]
      };

      this.cacheStore.set({
        cache_key: cacheKey,
        expires_at: new Date(Date.now() + this.cacheTtlMs).toISOString(),
        payload: {
          resolution: cloneIdentityResolution(resolution)
        },
        scope: "identity",
        stored_at: new Date().toISOString()
      } satisfies CacheEntryRecord);
      return resolution;
    }

    const resolution: IdentityResolution = {
      ambiguity_level: "strong",
      kind: "not_found",
      match_count: 0
    };

    this.cacheStore.set({
      cache_key: cacheKey,
      expires_at: new Date(Date.now() + this.cacheTtlMs).toISOString(),
      payload: {
        resolution: cloneIdentityResolution(resolution)
      },
      scope: "identity",
      stored_at: new Date().toISOString()
    } satisfies CacheEntryRecord);
    return resolution;
  }
}
