import type {
  EvidenceClassificationRecord,
  EvidenceRecord,
  ResolvedCandidate,
  SignalAssessment
} from "@/domain/models";

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
          record.evidence_type === "formal_activity_record"
        );
      }),
      classifications,
      "coherence"
    );
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

    const coherenceEvidence = this.filterStrongOfficialCamaraEvidence(
      evidence,
      classifications
    );

    if (coherenceEvidence.length === 0) {
      return {
        evidence_ids: [],
        reasons: [
          "Nenhuma evidencia oficial da Camara foi encontrada para coerencia."
        ],
        status: "insufficient"
      };
    }

    if (coherenceEvidence.length >= 2) {
      return {
        evidence_ids: coherenceEvidence.map((record) => record.evidence_id),
        reasons: [
          `Ha ${coherenceEvidence.length} evidencias oficiais da Camara sobre atuacao formal, mas ainda sem autoria, relatoria ou voto nominal por deputado neste fluxo.`
        ],
        status: "positive"
      };
    }

    return {
      evidence_ids: coherenceEvidence.map((record) => record.evidence_id),
      reasons: [
        "Ha evidencia oficial da Camara sobre atuacao formal, suficiente apenas para uma leitura minima de coerencia."
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
