import { describe, expect, it } from "vitest";

import { EvidenceClassifier } from "@/services/evidence-classifier";
import type { EvidenceRecord } from "@/domain/models";

describe("EvidenceClassifier", () => {
  it("keeps official evidence classified as strong_official", () => {
    const classifier = new EvidenceClassifier();
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
        summary: "Cadastro oficial do deputado na Camara."
      }
    ];

    const result = classifier.classify(evidence);

    expect(result).toHaveLength(1);
    expect(result[0]?.confidence).toBe("high");
    expect(result[0]?.evidence_id).toBe("ev-1");
    expect(result[0]?.strength).toBe("strong_official");
    expect(result[0]?.classified_at).toEqual(expect.any(String));
    expect(result[0]?.classification_id).toEqual(expect.any(String));
  });

  it("downgrades missing-source evidence to insufficient", () => {
    const classifier = new EvidenceClassifier();
    const evidence: EvidenceRecord[] = [
      {
        collected_at: "2026-03-29T12:00:00.000Z",
        evidence_id: "ev-2",
        evidence_type: "electoral_registry",
        person_id: "tse:2022:SP:deputado_federal:5080",
        signal_type: "evidence_level",
        source_name: "tse",
        source_url: "",
        strength: "strong_official",
        summary: "Resultado eleitoral sem referencia rastreavel."
      }
    ];

    const result = classifier.classify(evidence);

    expect(result[0]?.strength).toBe("insufficient");
    expect(result[0]?.confidence).toBe("low");
  });
});
