import { describe, expect, it } from "vitest";

import { SignalEngine } from "@/services/signal-engine";
import type {
  EvidenceClassificationRecord,
  EvidenceRecord,
  ResolvedCandidate
} from "@/domain/models";

describe("SignalEngine", () => {
  const incumbentFederalCandidate: ResolvedCandidate = {
    ambiguity_level: "none",
    canonical_name: "Erika Hilton",
    office: "deputado_federal",
    official_ids: {
      camara_id: "220639"
    },
    status: "incumbent",
    uf: "SP"
  };

  it("returns positive evidence_level when there is coverage across two official sources", () => {
    const engine = new SignalEngine();
    const evidence: EvidenceRecord[] = [
      {
        collected_at: "2026-03-29T12:00:00.000Z",
        evidence_id: "ev-1",
        evidence_type: "legislative_profile",
        person_id: "camara:220639",
        signal_type: "evidence_level",
        source_name: "camara",
        source_url: "https://dadosabertos.camara.leg.br/api/v2/deputados/220639",
        strength: "strong_official",
        summary: "Cadastro oficial."
      },
      {
        collected_at: "2026-03-29T12:00:01.000Z",
        evidence_id: "ev-2",
        evidence_type: "electoral_registry",
        person_id: "camara:220639",
        signal_type: "evidence_level",
        source_name: "tse",
        source_url: "https://resultados.tse.jus.br/oficial/app/index.html#/eleicao/resultados",
        strength: "strong_official",
        summary: "Resultado eleitoral."
      }
    ];
    const classifications: EvidenceClassificationRecord[] = [
      {
        classified_at: "2026-03-29T12:01:00.000Z",
        classification_id: "cl-1",
        confidence: "high",
        evidence_id: "ev-1",
        strength: "strong_official"
      },
      {
        classified_at: "2026-03-29T12:01:01.000Z",
        classification_id: "cl-2",
        confidence: "high",
        evidence_id: "ev-2",
        strength: "strong_official"
      }
    ];

    const result = engine.assessEvidenceLevel(evidence, classifications);

    expect(result.status).toBe("positive");
    expect(result.evidence_ids).toEqual(["ev-1", "ev-2"]);
  });

  it("returns insufficient evidence_level when no classified official evidence exists", () => {
    const engine = new SignalEngine();

    const result = engine.assessEvidenceLevel([], []);

    expect(result.status).toBe("insufficient");
    expect(result.reasons).toEqual([
      "Nenhuma evidencia oficial classificada foi encontrada."
    ]);
  });

  it("returns insufficient coherence for non-incumbent federal candidates", () => {
    const engine = new SignalEngine();
    const candidate: ResolvedCandidate = {
      ambiguity_level: "none",
      canonical_name: "Sonia Guajajara",
      office: "deputado_federal",
      official_ids: {},
      status: "challenger",
      uf: "SP"
    };

    const result = engine.assessCoherence(candidate, [], []);

    expect(result.status).toBe("insufficient");
    expect(result.reasons).toEqual([
      "Coherence minimo so se aplica a incumbentes federais."
    ]);
  });

  it("returns mixed coherence when an incumbent federal candidate has official Câmara evidence", () => {
    const engine = new SignalEngine();
    const evidence: EvidenceRecord[] = [
      {
        collected_at: "2026-03-29T12:00:00.000Z",
        evidence_id: "ev-4",
        evidence_type: "formal_activity_record",
        person_id: "camara:220639",
        signal_type: "coherence",
        source_name: "camara",
        source_url: "https://dadosabertos.camara.leg.br/api/v2/deputados/220639",
        strength: "strong_official",
        summary: "Perfil formal detalhado do deputado na Camara."
      }
    ];
    const classifications: EvidenceClassificationRecord[] = [
      {
        classified_at: "2026-03-29T12:01:00.000Z",
        classification_id: "cl-4",
        confidence: "high",
        evidence_id: "ev-4",
        strength: "strong_official"
      }
    ];

    const result = engine.assessCoherence(
      incumbentFederalCandidate,
      evidence,
      classifications
    );

    expect(result.status).toBe("mixed");
    expect(result.evidence_ids).toEqual(["ev-4"]);
    expect(result.reasons).toEqual([
      "Ha cobertura oficial da Camara em 1 bloco de coerencia: formal_activity_record. Ainda faltam: voting_summary, propositions_summary."
    ]);
  });

  it("returns positive coherence when an incumbent federal candidate has two distinct official Camara blocks", () => {
    const engine = new SignalEngine();
    const evidence: EvidenceRecord[] = [
      {
        collected_at: "2026-03-29T12:00:00.000Z",
        evidence_id: "ev-4",
        evidence_type: "formal_activity_record",
        person_id: "camara:220639",
        signal_type: "coherence",
        source_name: "camara",
        source_url: "https://dadosabertos.camara.leg.br/api/v2/deputados/220639",
        strength: "strong_official",
        summary: "Perfil formal detalhado do deputado na Camara."
      },
      {
        collected_at: "2026-03-29T12:00:01.000Z",
        evidence_id: "ev-5",
        evidence_type: "voting_summary",
        person_id: "camara:220639",
        signal_type: "coherence",
        source_name: "camara",
        source_url: "https://dadosabertos.camara.leg.br/api/v2/votacoes",
        strength: "strong_official",
        summary: "Participacao nominal recente em votacoes da Camara."
      }
    ];
    const classifications: EvidenceClassificationRecord[] = [
      {
        classified_at: "2026-03-29T12:01:00.000Z",
        classification_id: "cl-4",
        confidence: "high",
        evidence_id: "ev-4",
        strength: "strong_official"
      },
      {
        classified_at: "2026-03-29T12:01:01.000Z",
        classification_id: "cl-5",
        confidence: "high",
        evidence_id: "ev-5",
        strength: "strong_official"
      }
    ];

    const result = engine.assessCoherence(
      incumbentFederalCandidate,
      evidence,
      classifications
    );

    expect(result.status).toBe("positive");
    expect(result.evidence_ids).toEqual(["ev-4", "ev-5"]);
    expect(result.reasons).toEqual([
      "Ha cobertura oficial da Camara em 2 blocos independentes de coerencia: formal_activity_record, voting_summary."
    ]);
  });

  it("describes missing coherence blocks for incumbents", () => {
    const engine = new SignalEngine();
    const evidence: EvidenceRecord[] = [
      {
        collected_at: "2026-03-29T12:00:00.000Z",
        evidence_id: "ev-4",
        evidence_type: "formal_activity_record",
        person_id: "camara:220639",
        signal_type: "coherence",
        source_name: "camara",
        source_url: "https://dadosabertos.camara.leg.br/api/v2/deputados/220639",
        strength: "strong_official",
        summary: "Perfil formal detalhado do deputado na Camara."
      }
    ];
    const classifications: EvidenceClassificationRecord[] = [
      {
        classified_at: "2026-03-29T12:01:00.000Z",
        classification_id: "cl-4",
        confidence: "high",
        evidence_id: "ev-4",
        strength: "strong_official"
      }
    ];

    const coverage = engine.describeCoherenceCoverage(
      incumbentFederalCandidate,
      evidence,
      classifications
    );

    expect(coverage.collected_types).toEqual(["formal_activity_record"]);
    expect(coverage.missing_types).toEqual([
      "voting_summary",
      "propositions_summary"
    ]);
  });

  it("returns insufficient integrity when no integrity evidence exists", () => {
    const engine = new SignalEngine();

    const result = engine.assessIntegrity([], []);

    expect(result.status).toBe("insufficient");
    expect(result.reasons).toEqual([
      "Nenhuma evidencia oficial de integridade foi encontrada."
    ]);
  });

  it("returns negative integrity when an official integrity alert is classified", () => {
    const engine = new SignalEngine();
    const evidence: EvidenceRecord[] = [
      {
        collected_at: "2026-03-29T12:00:00.000Z",
        evidence_id: "ev-3",
        evidence_type: "integrity_alert",
        person_id: "tse:2022:SP:deputado_federal:5080",
        signal_type: "integrity",
        source_name: "tse",
        source_url: "https://exemplo.oficial/integridade",
        strength: "strong_official",
        summary: "Alerta oficial de integridade."
      }
    ];
    const classifications: EvidenceClassificationRecord[] = [
      {
        classified_at: "2026-03-29T12:01:00.000Z",
        classification_id: "cl-3",
        confidence: "high",
        evidence_id: "ev-3",
        strength: "strong_official"
      }
    ];

    const result = engine.assessIntegrity(evidence, classifications);

    expect(result.status).toBe("negative");
    expect(result.evidence_ids).toEqual(["ev-3"]);
  });

  it("returns positive values_fit when a supported theme has a strong official match", () => {
    const engine = new SignalEngine();
    const evidence: EvidenceRecord[] = [
      {
        collected_at: "2026-04-01T12:00:00.000Z",
        evidence_id: "ev-values-1",
        evidence_type: "propositions_summary",
        person_id: "camara:220639",
        signal_type: "coherence",
        source_name: "camara",
        source_url: "https://dadosabertos.camara.leg.br/api/v2/proposicoes?idDeputadoAutor=220639",
        strength: "strong_official",
        summary:
          "Proposicoes autorais recentes sobre custo de vida, renda e emprego foram identificadas."
      }
    ];
    const classifications: EvidenceClassificationRecord[] = [
      {
        classified_at: "2026-04-01T12:01:00.000Z",
        classification_id: "cl-values-1",
        confidence: "high",
        evidence_id: "ev-values-1",
        strength: "strong_official"
      }
    ];

    const result = engine.assessValuesFit(
      incumbentFederalCandidate,
      evidence,
      classifications,
      ["custo de vida", "educacao"]
    );

    expect(result.status).toBe("positive");
    expect(result.evidence_ids).toEqual(["ev-values-1"]);
    expect(result.reasons[0]).toContain("Economia e Custo de Vida");
  });

  it("returns mixed values_fit when a supported theme has only partial official matches", () => {
    const engine = new SignalEngine();
    const evidence: EvidenceRecord[] = [
      {
        collected_at: "2026-04-01T12:00:00.000Z",
        evidence_id: "ev-values-2",
        evidence_type: "propositions_summary",
        person_id: "camara:220639",
        signal_type: "coherence",
        source_name: "camara",
        source_url: "https://dadosabertos.camara.leg.br/api/v2/proposicoes?idDeputadoAutor=220639",
        strength: "official_partial",
        summary: "Proposicoes autorais sobre direitos das mulheres em fase inicial."
      },
      {
        collected_at: "2026-04-01T12:00:01.000Z",
        evidence_id: "ev-values-3",
        evidence_type: "formal_activity_record",
        person_id: "camara:220639",
        signal_type: "coherence",
        source_name: "camara",
        source_url: "https://dadosabertos.camara.leg.br/api/v2/deputados/220639",
        strength: "official_partial",
        summary: "Atuacao formal relacionada a direitos das mulheres."
      }
    ];
    const classifications: EvidenceClassificationRecord[] = [
      {
        classified_at: "2026-04-01T12:01:00.000Z",
        classification_id: "cl-values-2",
        confidence: "low",
        evidence_id: "ev-values-2",
        strength: "official_partial"
      },
      {
        classified_at: "2026-04-01T12:01:01.000Z",
        classification_id: "cl-values-3",
        confidence: "low",
        evidence_id: "ev-values-3",
        strength: "official_partial"
      }
    ];

    const result = engine.assessValuesFit(
      incumbentFederalCandidate,
      evidence,
      classifications,
      ["direitos das mulheres"]
    );

    expect(result.status).toBe("mixed");
    expect(result.evidence_ids).toEqual(["ev-values-2", "ev-values-3"]);
  });

  it("returns insufficient values_fit when the evidence is weak or unsupported", () => {
    const engine = new SignalEngine();
    const evidence: EvidenceRecord[] = [
      {
        collected_at: "2026-04-01T12:00:00.000Z",
        evidence_id: "ev-values-4",
        evidence_type: "news_screening",
        person_id: "camara:220639",
        signal_type: "values_fit",
        source_name: "jornal-local",
        source_url: "https://jornal.local/reportagem/1",
        strength: "complementary",
        summary: "Cobertura jornalistica sobre tema economico."
      },
      {
        collected_at: "2026-04-01T12:00:01.000Z",
        evidence_id: "ev-values-5",
        evidence_type: "legislative_profile",
        person_id: "camara:220639",
        signal_type: "evidence_level",
        source_name: "camara",
        source_url: "https://dadosabertos.camara.leg.br/api/v2/deputados/220639",
        strength: "weak",
        summary: "Perfil sem conexao tematica suficiente."
      }
    ];
    const classifications: EvidenceClassificationRecord[] = [
      {
        classified_at: "2026-04-01T12:01:00.000Z",
        classification_id: "cl-values-4",
        confidence: "low",
        evidence_id: "ev-values-4",
        strength: "complementary"
      },
      {
        classified_at: "2026-04-01T12:01:01.000Z",
        classification_id: "cl-values-5",
        confidence: "low",
        evidence_id: "ev-values-5",
        strength: "weak"
      }
    ];

    const result = engine.assessValuesFit(
      incumbentFederalCandidate,
      evidence,
      classifications,
      ["transparencia"]
    );

    expect(result.status).toBe("insufficient");
    expect(result.reasons[0]).toContain("watchlist minima");
  });
});
