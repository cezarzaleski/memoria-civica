import type {
  ConfidenceLevel,
  ConsultationResponse,
  ResolvedCandidate,
  SignalAssessment,
  SignalName,
  TrafficLight
} from "@/domain/models";

interface AssembleResponseInput {
  readonly alerts: readonly string[];
  readonly candidate: ResolvedCandidate;
  readonly signals: Record<SignalName, SignalAssessment>;
  readonly sources: readonly string[];
}

function buildReasons(
  signals: Record<SignalName, SignalAssessment>
): readonly string[] {
  return [
    ...signals.evidence_level.reasons,
    ...signals.integrity.reasons,
    ...signals.coherence.reasons
  ].slice(0, 3);
}

function deriveConfidence(
  evidenceLevel: SignalAssessment["status"]
): ConfidenceLevel {
  if (evidenceLevel === "positive") {
    return "high";
  }

  if (evidenceLevel === "mixed") {
    return "medium";
  }

  return "low";
}

function deriveTrafficLight(
  evidenceLevel: SignalAssessment["status"],
  integrity: SignalAssessment["status"]
): TrafficLight {
  if (integrity === "negative") {
    return "red";
  }

  if (evidenceLevel === "insufficient") {
    return "gray";
  }

  return "yellow";
}

function buildSummary(
  trafficLight: TrafficLight,
  candidate: ResolvedCandidate
): string {
  if (trafficLight === "red") {
    return `A consulta encontrou alerta oficial de integridade para ${candidate.canonical_name}.`;
  }

  if (trafficLight === "yellow") {
    return `A consulta encontrou base oficial inicial para ${candidate.canonical_name}, mas a leitura ainda exige cautela.`;
  }

  return `Ainda nao ha base suficiente para concluir a consulta sobre ${candidate.canonical_name}.`;
}

export class ResponseAssembler {
  public assemble(input: AssembleResponseInput): ConsultationResponse {
    const confidence = deriveConfidence(input.signals.evidence_level.status);
    const trafficLight = deriveTrafficLight(
      input.signals.evidence_level.status,
      input.signals.integrity.status
    );

    return {
      alerts: input.alerts,
      candidate: {
        ambiguity_level: input.candidate.ambiguity_level,
        canonical_name: input.candidate.canonical_name,
        official_ids: input.candidate.official_ids,
        party: input.candidate.party,
        status: input.candidate.status,
        uf: input.candidate.uf
      },
      confidence,
      reasons: buildReasons(input.signals),
      signals: input.signals,
      sources: input.sources,
      summary: buildSummary(trafficLight, input.candidate),
      traffic_light: trafficLight
    };
  }
}
