import type {
  EvidenceClassificationRecord,
  EvidenceRecord,
  ResolvedCandidate,
  SignalAssessment
} from "@/domain/models";

export const EXPECTED_CAMARA_COHERENCE_EVIDENCE_TYPES = [
  "formal_activity_record",
  "voting_summary",
  "propositions_summary"
] as const;

interface CoherenceCoverage {
  readonly collected_types: readonly string[];
  readonly evidence: readonly EvidenceRecord[];
  readonly missing_types: readonly string[];
}

export class SignalEngine {
  private filterStrongOfficialEvidence(
    evidence: readonly EvidenceRecord[],
    classifications: readonly EvidenceClassificationRecord[],
    signalType: EvidenceRecord["signal_type"]
  ): readonly EvidenceRecord[] {
    return evidence.filter((record) => {
      return (
        record.signal_type === signalType &&
        classifications.some((classification) => {
          return (
            classification.evidence_id === record.evidence_id &&
            classification.strength === "strong_official"
          );
        })
      );
    });
  }

  private filterStrongOfficialCamaraEvidence(
    evidence: readonly EvidenceRecord[],
    classifications: readonly EvidenceClassificationRecord[]
  ): readonly EvidenceRecord[] {
    return this.filterStrongOfficialEvidence(
      evidence.filter((record) => {
        return (
          record.source_name === "camara" &&
          EXPECTED_CAMARA_COHERENCE_EVIDENCE_TYPES.includes(
            record.evidence_type as
              (typeof EXPECTED_CAMARA_COHERENCE_EVIDENCE_TYPES)[number]
          )
        );
      }),
      classifications,
      "coherence"
    );
  }

  public describeCoherenceCoverage(
    candidate: Pick<ResolvedCandidate, "office" | "status">,
    evidence: readonly EvidenceRecord[],
    classifications: readonly EvidenceClassificationRecord[]
  ): CoherenceCoverage {
    if (candidate.office !== "deputado_federal" || candidate.status !== "incumbent") {
      return {
        collected_types: [],
        evidence: [],
        missing_types: []
      };
    }

    const coherenceEvidence = this.filterStrongOfficialCamaraEvidence(
      evidence,
      classifications
    );
    const collectedTypes = [...new Set(coherenceEvidence.map((record) => record.evidence_type))];

    return {
      collected_types: collectedTypes,
      evidence: coherenceEvidence,
      missing_types: EXPECTED_CAMARA_COHERENCE_EVIDENCE_TYPES.filter((type) => {
        return !collectedTypes.includes(type);
      })
    };
  }

  public assessEvidenceLevel(
    evidence: readonly EvidenceRecord[],
    classifications: readonly EvidenceClassificationRecord[]
  ): SignalAssessment {
    const classifiedEvidence = this.filterStrongOfficialEvidence(
      evidence,
      classifications,
      "evidence_level"
    );

    if (classifiedEvidence.length === 0) {
      return {
        evidence_ids: [],
        reasons: ["Nenhuma evidencia oficial classificada foi encontrada."],
        status: "insufficient"
      };
    }

    const sourceCount = new Set(classifiedEvidence.map((record) => record.source_name)).size;

    if (sourceCount >= 2) {
      return {
        evidence_ids: classifiedEvidence.map((record) => record.evidence_id),
        reasons: [
          `Ha ${classifiedEvidence.length} evidencias oficiais em ${sourceCount} fontes independentes.`
        ],
        status: "positive"
      };
    }

    return {
      evidence_ids: classifiedEvidence.map((record) => record.evidence_id),
      reasons: [
        `Ha ${classifiedEvidence.length} evidencia oficial, mas a cobertura ainda depende de uma unica fonte.`
      ],
      status: "mixed"
    };
  }

  public assessCoherence(
    candidate: Pick<ResolvedCandidate, "office" | "status">,
    evidence: readonly EvidenceRecord[],
    classifications: readonly EvidenceClassificationRecord[]
  ): SignalAssessment {
    if (candidate.office !== "deputado_federal" || candidate.status !== "incumbent") {
      return {
        evidence_ids: [],
        reasons: ["Coherence minimo so se aplica a incumbentes federais."],
        status: "insufficient"
      };
    }

    const coherenceCoverage = this.describeCoherenceCoverage(
      candidate,
      evidence,
      classifications
    );
    const coherenceEvidence = coherenceCoverage.evidence;

    if (coherenceEvidence.length === 0) {
      return {
        evidence_ids: [],
        reasons: [
          `Nenhuma evidencia oficial da Camara foi encontrada para coerencia. Blocos esperados nesta trilha: ${EXPECTED_CAMARA_COHERENCE_EVIDENCE_TYPES.join(", ")}.`
        ],
        status: "insufficient"
      };
    }

    const coherenceTypes = coherenceCoverage.collected_types;

    if (coherenceTypes.length >= 2) {
      return {
        evidence_ids: coherenceEvidence.map((record) => record.evidence_id),
        reasons: [
          `Ha cobertura oficial da Camara em ${coherenceTypes.length} blocos independentes de coerencia: ${coherenceTypes.join(", ")}.`
        ],
        status: "positive"
      };
    }

    return {
      evidence_ids: coherenceEvidence.map((record) => record.evidence_id),
      reasons: [
        `Ha cobertura oficial da Camara em 1 bloco de coerencia: ${coherenceTypes[0]}. Ainda faltam: ${coherenceCoverage.missing_types.join(", ")}.`
      ],
      status: "mixed"
    };
  }

  public assessIntegrity(
    evidence: readonly EvidenceRecord[],
    classifications: readonly EvidenceClassificationRecord[]
  ): SignalAssessment {
    const integrityEvidence = this.filterStrongOfficialEvidence(
      evidence,
      classifications,
      "integrity"
    );

    if (integrityEvidence.length === 0) {
      return {
        evidence_ids: [],
        reasons: ["Nenhuma evidencia oficial de integridade foi encontrada."],
        status: "insufficient"
      };
    }

    const hasAlert = integrityEvidence.some((record) => {
      return record.evidence_type === "integrity_alert";
    });

    if (hasAlert) {
      return {
        evidence_ids: integrityEvidence.map((record) => record.evidence_id),
        reasons: ["Ha alerta oficial de integridade que exige cautela."],
        status: "negative"
      };
    }

    return {
      evidence_ids: integrityEvidence.map((record) => record.evidence_id),
      reasons: ["Ha registro oficial relacionado a integridade, sem alerta grave classificado."],
      status: "mixed"
    };
  }
}
