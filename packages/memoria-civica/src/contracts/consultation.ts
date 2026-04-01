import type {
  ConsultationResponse,
  ResolvedCandidate,
  SignalAssessment
} from "@/domain/models";

export interface ConsultCandidateRequest {
  readonly candidate_name: string;
  readonly office: "deputado_federal" | "deputado_distrital";
  readonly party?: string;
  readonly uf?: string;
  readonly user_priorities: readonly string[];
}

interface ConsultCandidateRequestInput {
  readonly candidate_name?: string;
  readonly office?: "deputado_federal" | "deputado_distrital";
  readonly party?: string;
  readonly uf?: string;
  readonly user_priorities?: readonly string[];
}

interface GrayResponseInput {
  readonly alerts: readonly string[];
  readonly candidate: ResolvedCandidate;
  readonly identity_metadata?: {
    readonly match_count: number;
    readonly requires?: ReadonlyArray<"uf" | "party">;
    readonly resolution_kind: "ambiguous" | "not_found" | "resolved";
  };
  readonly reasons?: readonly string[];
  readonly summary?: string;
}

const DEFAULT_INSUFFICIENT_REASON = "Sem coleta de evidencias nesta fase.";

function normalizeWhitespace(value: string): string {
  return value.replace(/\s+/g, " ").trim();
}

function normalizeOptionalToken(value?: string): string | undefined {
  if (value === undefined) {
    return undefined;
  }

  const normalized = normalizeWhitespace(value);
  return normalized === "" ? undefined : normalized.toUpperCase();
}

function buildInsufficientSignal(reason: string): SignalAssessment {
  return {
    evidence_ids: [],
    reasons: [reason],
    status: "insufficient"
  };
}

export function validateConsultCandidateRequest(
  input: ConsultCandidateRequestInput
): ConsultCandidateRequest {
  const candidateName = normalizeWhitespace(input.candidate_name ?? "");

  if (candidateName === "") {
    throw new Error("candidate_name is required");
  }

  const office = input.office ?? "deputado_federal";
  const uf = normalizeOptionalToken(input.uf);

  if (office === "deputado_distrital" && uf !== "DF") {
    throw new Error("deputado_distrital requires uf=DF");
  }

  return {
    candidate_name: candidateName,
    office,
    party: normalizeOptionalToken(input.party),
    uf,
    user_priorities: input.user_priorities ?? []
  };
}

export function buildGrayResponse(
  input: GrayResponseInput
): ConsultationResponse {
  const summary =
    input.summary ??
    "Ainda nao ha base suficiente para uma conclusao honesta nesta fase.";
  const reason = input.reasons?.[0] ?? DEFAULT_INSUFFICIENT_REASON;

  return {
    alerts: input.alerts,
    candidate: {
      ambiguity_level: input.candidate.ambiguity_level,
      canonical_name: input.candidate.canonical_name,
      match_count: input.identity_metadata?.match_count,
      official_ids: input.candidate.official_ids,
      party: input.candidate.party,
      requires: input.identity_metadata?.requires,
      resolution_kind: input.identity_metadata?.resolution_kind,
      status: input.candidate.status,
      uf: input.candidate.uf
    },
    confidence: "low",
    reasons: input.reasons ?? [reason],
    signals: {
      coherence: buildInsufficientSignal(DEFAULT_INSUFFICIENT_REASON),
      evidence_level: buildInsufficientSignal(reason),
      integrity: buildInsufficientSignal(DEFAULT_INSUFFICIENT_REASON),
      values_fit: buildInsufficientSignal(DEFAULT_INSUFFICIENT_REASON)
    },
    sources: [],
    summary,
    traffic_light: "gray"
  };
}
