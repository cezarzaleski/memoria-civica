import type {
  EvidenceClassificationRecord,
  EvidenceRecord
} from "@/domain/models";

function buildClassificationId(record: EvidenceRecord): string {
  return Buffer.from(
    [record.evidence_id, record.source_name, record.strength].join("|")
  ).toString("base64url");
}

export class EvidenceClassifier {
  public classify(
    evidence: readonly EvidenceRecord[]
  ): readonly EvidenceClassificationRecord[] {
    return evidence.map((record) => {
      const hasTraceableSource = record.source_url.trim() !== "";
      const strength = hasTraceableSource ? record.strength : "insufficient";

      return {
        classified_at: new Date().toISOString(),
        classification_id: buildClassificationId(record),
        confidence: strength === "strong_official" ? "high" : "low",
        evidence_id: record.evidence_id,
        strength
      };
    });
  }
}
