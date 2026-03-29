import type { EvidenceRecord, RawEvidence } from "@/domain/models";

export interface EvidenceStore {
  save(evidence: readonly RawEvidence[]): Promise<readonly EvidenceRecord[]>;
}

function buildEvidenceId(raw: RawEvidence): string {
  return Buffer.from(
    [
      raw.person_id,
      raw.source_name,
      raw.evidence_type,
      raw.collected_at,
      raw.source_url
    ].join("|")
  ).toString("base64url");
}

export class InMemoryEvidenceStore implements EvidenceStore {
  private readonly records: EvidenceRecord[] = [];

  public save(
    evidence: readonly RawEvidence[]
  ): Promise<readonly EvidenceRecord[]> {
    const stored = evidence.map((item) => {
      const record: EvidenceRecord = {
        ...item,
        evidence_id: buildEvidenceId(item)
      };

      this.records.push(record);
      return record;
    });

    return Promise.resolve(stored);
  }

  public list(): readonly EvidenceRecord[] {
    return [...this.records];
  }
}
