import type { CacheEntryRecord, CollectionPlan, RawEvidence, ResolvedCandidate } from "@/domain/models";
import {
  InMemoryCacheStore,
  type CacheStore
} from "@/services/cache-store";
import type { OfficialEvidenceCollector } from "@/source-connectors/mcp-brasil";

interface CachedEvidenceCollectorOptions {
  readonly cacheStore?: CacheStore;
  readonly ttlMs?: number;
}

function buildEvidenceCacheKey(
  candidate: ResolvedCandidate,
  plan: CollectionPlan
): string {
  return JSON.stringify({
    canonical_name: candidate.canonical_name,
    office: candidate.office,
    official_ids: candidate.official_ids,
    plan
  });
}

function cloneRawEvidence(evidence: readonly RawEvidence[]): readonly RawEvidence[] {
  return JSON.parse(JSON.stringify(evidence)) as RawEvidence[];
}

export class CachedEvidenceCollector implements OfficialEvidenceCollector {
  private readonly cacheStore: CacheStore;

  private readonly ttlMs: number;

  public constructor(
    private readonly delegate: OfficialEvidenceCollector,
    options: CachedEvidenceCollectorOptions = {}
  ) {
    this.cacheStore = options.cacheStore ?? new InMemoryCacheStore();
    this.ttlMs = options.ttlMs ?? 5 * 60 * 1000;
  }

  public async collect(
    candidate: ResolvedCandidate,
    plan: CollectionPlan
  ): Promise<readonly RawEvidence[]> {
    const cacheKey = buildEvidenceCacheKey(candidate, plan);
    const cached = this.cacheStore.get("evidence", cacheKey);

    if (cached !== null) {
      return cloneRawEvidence(cached.payload.evidence as RawEvidence[]);
    }

    const evidence = await this.delegate.collect(candidate, plan);

    this.cacheStore.set({
      cache_key: cacheKey,
      expires_at: new Date(Date.now() + this.ttlMs).toISOString(),
      payload: {
        evidence: cloneRawEvidence(evidence)
      },
      scope: "evidence",
      stored_at: new Date().toISOString()
    } satisfies CacheEntryRecord);

    return evidence;
  }
}
