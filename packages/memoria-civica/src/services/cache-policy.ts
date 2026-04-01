export interface CacheTtlPolicy {
  readonly evidence_ms: number;
  readonly identity_ms: number;
  readonly signal_ms: number;
}

export const DEFAULT_CACHE_TTL_POLICY: CacheTtlPolicy = {
  evidence_ms: 2 * 60 * 1000,
  identity_ms: 5 * 60 * 1000,
  signal_ms: 60 * 1000
};
