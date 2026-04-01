import type {
  CacheEntryRecord,
  EvidenceClassificationRecord,
  EvidenceRecord,
  ResolvedCandidate,
  SignalAssessment
} from "@/domain/models";
import {
  InMemoryCacheStore,
  type CacheStore
} from "@/services/cache-store";
import { SignalEngine } from "@/services/signal-engine";

interface CachedSignalServiceOptions {
  readonly cacheStore?: CacheStore;
  readonly ttlMs?: number;
}

interface CachedSignalResult {
  readonly coherence: SignalAssessment;
  readonly coherenceCoverage: ReturnType<SignalEngine["describeCoherenceCoverage"]>;
  readonly evidence_level: SignalAssessment;
  readonly integrity: SignalAssessment;
}

function buildSignalCacheKey(
  candidate: ResolvedCandidate,
  evidence: readonly EvidenceRecord[]
): string {
  return JSON.stringify({
    canonical_name: candidate.canonical_name,
    office: candidate.office,
    official_ids: candidate.official_ids,
    evidence_ids: evidence.map((record) => record.evidence_id).sort()
  });
}

function cloneSignalResult(result: CachedSignalResult): CachedSignalResult {
  return JSON.parse(JSON.stringify(result)) as CachedSignalResult;
}

export class CachedSignalService {
  private readonly cacheStore: CacheStore;

  private readonly signalEngine: SignalEngine;

  private readonly ttlMs: number;

  public constructor(
    signalEngine = new SignalEngine(),
    options: CachedSignalServiceOptions = {}
  ) {
    this.cacheStore = options.cacheStore ?? new InMemoryCacheStore();
    this.signalEngine = signalEngine;
    this.ttlMs = options.ttlMs ?? 5 * 60 * 1000;
  }

  public compute(
    candidate: ResolvedCandidate,
    evidence: readonly EvidenceRecord[],
    classifications: readonly EvidenceClassificationRecord[]
  ): CachedSignalResult {
    const cacheKey = buildSignalCacheKey(candidate, evidence);
    const cached = this.cacheStore.get("signal", cacheKey);

    if (cached !== null) {
      return cloneSignalResult(cached.payload.result as CachedSignalResult);
    }

    const result = {
      coherence: this.signalEngine.assessCoherence(
        candidate,
        evidence,
        classifications
      ),
      coherenceCoverage: this.signalEngine.describeCoherenceCoverage(
        candidate,
        evidence,
        classifications
      ),
      evidence_level: this.signalEngine.assessEvidenceLevel(
        evidence,
        classifications
      ),
      integrity: this.signalEngine.assessIntegrity(evidence, classifications)
    } satisfies CachedSignalResult;

    this.cacheStore.set({
      cache_key: cacheKey,
      expires_at: new Date(Date.now() + this.ttlMs).toISOString(),
      payload: {
        result: cloneSignalResult(result)
      },
      scope: "signal",
      stored_at: new Date().toISOString()
    } satisfies CacheEntryRecord);

    return result;
  }
}
