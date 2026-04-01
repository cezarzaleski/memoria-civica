import type {
  EvidenceClassificationRecord,
  EvidenceRecord,
  ResolvedCandidate,
  SignalAssessment
} from "@/domain/models";
import {
  MINIMUM_VALUES_FIT_WATCHLIST,
  matchesEditorialTheme,
  normalizeSupportedPriorities
} from "@/services/editorial-config";

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
  private findClassification(
    evidenceId: string,
    classifications: readonly EvidenceClassificationRecord[]
  ): EvidenceClassificationRecord | undefined {
    return classifications.find((classification) => {
      return classification.evidence_id === evidenceId;
    });
  }

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

  private buildValuesFitReason(
    themeLabel: string,
    status: SignalAssessment["status"],
    evidenceIds: readonly string[],
    matchedEvidenceCount: number
  ): string {
    const limitation =
      "Evidencias fracas, manchetes isoladas e jornalismo sem ato formal associado nao entram na base principal.";

    if (status === "positive") {
      return `Tema ${themeLabel} com alinhamento observavel: ${matchedEvidenceCount} evidencia oficial forte compativel com a watchlist minima. ${limitation}`;
    }

    if (status === "mixed") {
      return `Tema ${themeLabel} com aderencia parcial: ${matchedEvidenceCount} evidencias oficiais parciais compativeis com a watchlist minima. ${limitation}`;
    }

    if (evidenceIds.length === 0) {
      return `Tema ${themeLabel} sem base suficiente na watchlist minima. ${limitation}`;
    }

    return `Tema ${themeLabel} ainda sem base suficiente: ${matchedEvidenceCount} evidencia oficial compativel nao basta para subir acima de insuficiente. ${limitation}`;
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

  public assessValuesFit(
    _candidate: Pick<ResolvedCandidate, "office" | "status">,
    evidence: readonly EvidenceRecord[],
    classifications: readonly EvidenceClassificationRecord[],
    userPriorities: readonly string[]
  ): SignalAssessment {
    const selectedThemes = normalizeSupportedPriorities(userPriorities);

    if (selectedThemes.length === 0) {
      return {
        evidence_ids: [],
        reasons: [
          "Nenhuma prioridade compatível com a watchlist minima foi informada."
        ],
        status: "insufficient"
      };
    }

    const themeAssessments = selectedThemes.map((themeId) => {
      const theme = MINIMUM_VALUES_FIT_WATCHLIST.find((item) => item.id === themeId);

      if (theme === undefined) {
        return {
          evidence_ids: [],
          matchedEvidenceCount: 0,
          reason: "Tema nao suportado pela watchlist minima.",
          status: "insufficient" as const,
          themeLabel: themeId
        };
      }

      const matchedEvidence = evidence.filter((record) => {
        const classification = this.findClassification(
          record.evidence_id,
          classifications
        );

        if (classification === undefined) {
          return false;
        }

        if (
          record.signal_type !== "coherence" &&
          record.signal_type !== "integrity"
        ) {
          return false;
        }

        return matchesEditorialTheme(
          theme,
          `${record.evidence_type} ${record.source_name} ${record.summary} ${record.source_url}`,
          record.signal_type,
          classification.strength
        );
      });

      const strongMatches = matchedEvidence.filter((record) => {
        const classification = this.findClassification(
          record.evidence_id,
          classifications
        );

        return classification?.strength === "strong_official";
      });

      const partialMatches = matchedEvidence.filter((record) => {
        const classification = this.findClassification(
          record.evidence_id,
          classifications
        );

        return classification?.strength === "official_partial";
      });

      let status: SignalAssessment["status"] = "insufficient";

      if (strongMatches.length > 0) {
        status = "positive";
      } else if (partialMatches.length >= 2) {
        status = "mixed";
      }

      return {
        evidence_ids: matchedEvidence.map((record) => record.evidence_id),
        matchedEvidenceCount:
          status === "positive" ? strongMatches.length : partialMatches.length,
        reason: this.buildValuesFitReason(
          theme.label,
          status,
          matchedEvidence.map((record) => record.evidence_id),
          status === "positive" ? strongMatches.length : partialMatches.length
        ),
        status,
        themeLabel: theme.label
      };
    });

    const rankedAssessments = themeAssessments
      .filter((assessment) => assessment.status !== "insufficient")
      .sort((left, right) => {
        const leftRank = left.status === "positive" ? 2 : 1;
        const rightRank = right.status === "positive" ? 2 : 1;

        if (rightRank !== leftRank) {
          return rightRank - leftRank;
        }

        return right.matchedEvidenceCount - left.matchedEvidenceCount;
      });

    if (rankedAssessments.length > 0) {
      const bestRank =
        rankedAssessments[0]?.status === "positive" ? "positive" : "mixed";
      const bestAssessments = rankedAssessments.filter((assessment) => {
        return assessment.status === bestRank;
      });

      return {
        evidence_ids: [...new Set(bestAssessments.flatMap((assessment) => assessment.evidence_ids))],
        reasons: bestAssessments.map((assessment) => assessment.reason),
        status: bestRank
      };
    }

    const fallback = themeAssessments[0];

    return {
      evidence_ids: fallback?.evidence_ids ?? [],
      reasons: [
        fallback?.reason ??
          "Nenhuma prioridade compatível com a watchlist minima encontrou base suficiente."
      ],
      status: "insufficient"
    };
  }
}
