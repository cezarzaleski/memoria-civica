export type Office = "deputado_federal" | "deputado_distrital";

export type CandidateStatus = "incumbent" | "former" | "challenger";

export type AmbiguityLevel = "none" | "low" | "moderate" | "strong";

export type EvidenceStrength =
  | "strong_official"
  | "official_partial"
  | "complementary"
  | "weak"
  | "insufficient";

export type SignalName =
  | "integrity"
  | "coherence"
  | "evidence_level"
  | "values_fit";

export type SignalStatus = "positive" | "mixed" | "negative" | "insufficient";

export type TrafficLight = "green" | "yellow" | "red" | "gray";

export type ConfidenceLevel = "high" | "medium" | "low";

export interface OfficialIds {
  readonly camara_id?: string;
  readonly mcp_brasil_id?: string;
  readonly tse_id?: string;
}

export interface ResolvedCandidate {
  readonly ambiguity_level: AmbiguityLevel;
  readonly aliases?: readonly string[];
  readonly canonical_name: string;
  readonly office: Office;
  readonly official_ids: OfficialIds;
  readonly party?: string;
  readonly status: CandidateStatus;
  readonly uf?: string;
}

export interface IdentityQuery {
  readonly name: string;
  readonly office: Office;
  readonly party?: string;
  readonly uf?: string;
}

export interface AmbiguousIdentityResolution {
  readonly ambiguity_level: "strong";
  readonly candidates: readonly ResolvedCandidate[];
  readonly kind: "ambiguous";
  readonly match_count: number;
  readonly requires: ReadonlyArray<"uf" | "party">;
}

export interface MissingIdentityResolution {
  readonly ambiguity_level: "strong";
  readonly kind: "not_found";
  readonly match_count: 0;
}

export interface SuccessfulIdentityResolution {
  readonly ambiguity_level: AmbiguityLevel;
  readonly candidate: ResolvedCandidate;
  readonly kind: "resolved";
  readonly match_count: 1;
}

export type IdentityResolution =
  | AmbiguousIdentityResolution
  | MissingIdentityResolution
  | SuccessfulIdentityResolution;

export interface EvidenceRecord {
  readonly collected_at: string;
  readonly evidence_id: string;
  readonly evidence_type: string;
  readonly fact_date?: string;
  readonly person_id: string;
  readonly signal_type: SignalName;
  readonly source_name: string;
  readonly source_url: string;
  readonly strength: EvidenceStrength;
  readonly summary: string;
}

export interface RawEvidence {
  readonly collected_at: string;
  readonly evidence_type: string;
  readonly fact_date?: string;
  readonly person_id: string;
  readonly signal_type: SignalName;
  readonly source_name: string;
  readonly source_url: string;
  readonly strength: EvidenceStrength;
  readonly summary: string;
}

export interface EvidenceClassificationRecord {
  readonly classified_at: string;
  readonly classification_id: string;
  readonly confidence: ConfidenceLevel;
  readonly evidence_id: string;
  readonly notes?: string;
  readonly strength: EvidenceStrength;
}

export interface QueryExecutionRecord {
  readonly duration_ms: number;
  readonly finished_at?: string;
  readonly request_fingerprint: string;
  readonly started_at: string;
  readonly status: "completed" | "failed";
  readonly steps: readonly string[];
  readonly trace_id: string;
}

export interface CollectionTask {
  readonly objective: string;
  readonly params: Record<string, string | undefined>;
  readonly priority: number;
  readonly source: "camara" | "tse";
}

export interface CollectionPlan {
  readonly profile: "challenger" | "former_parliamentarian" | "incumbent_federal";
  readonly requested_signals: readonly SignalName[];
  readonly tasks: readonly CollectionTask[];
}

export interface CacheEntryRecord {
  readonly cache_key: string;
  readonly expires_at: string;
  readonly payload: Record<string, unknown>;
  readonly scope: "identity" | "evidence" | "signal";
  readonly stored_at: string;
}

export interface SignalAssessment {
  readonly evidence_ids: readonly string[];
  readonly reasons: readonly string[];
  readonly status: SignalStatus;
}

export interface ConsultationResponse {
  readonly alerts: readonly string[];
  readonly candidate: {
    readonly ambiguity_level?: AmbiguityLevel;
    readonly canonical_name: string;
    readonly match_count?: number;
    readonly official_ids: OfficialIds;
    readonly party?: string;
    readonly requires?: ReadonlyArray<"uf" | "party">;
    readonly resolution_kind?: IdentityResolution["kind"];
    readonly status: CandidateStatus;
    readonly uf?: string;
  };
  readonly confidence: ConfidenceLevel;
  readonly reasons: readonly string[];
  readonly signals: Record<SignalName, SignalAssessment>;
  readonly sources: readonly string[];
  readonly summary: string;
  readonly traffic_light: TrafficLight;
}
