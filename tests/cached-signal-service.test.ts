import { describe, expect, it, vi } from "vitest";

import type {
  EvidenceClassificationRecord,
  EvidenceRecord,
  ResolvedCandidate
} from "@/domain/models";
import { InMemoryCacheStore } from "@/services/cache-store";
import { CachedSignalService } from "@/services/cached-signal-service";
import { SignalEngine } from "@/services/signal-engine";

describe("CachedSignalService", () => {
  it("reuses cached signal computation for the same candidate and evidence set", () => {
    const candidate: ResolvedCandidate = {
      ambiguity_level: "none",
      canonical_name: "Erika Hilton",
      office: "deputado_federal",
      official_ids: {
        camara_id: "220639"
      },
      party: "PSOL",
      status: "incumbent",
      uf: "SP"
    };
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
    const classifications: EvidenceClassificationRecord[] = [
      {
        classified_at: "2026-03-29T12:01:00.000Z",
        classification_id: "cl-1",
        confidence: "high",
        evidence_id: "ev-1",
        strength: "strong_official"
      }
    ];
    const signalEngine = new SignalEngine();
    const assessEvidenceLevel = vi.spyOn(signalEngine, "assessEvidenceLevel");
    const service = new CachedSignalService(signalEngine, {
      cacheStore: new InMemoryCacheStore(),
      ttlMs: 60_000
    });

    const first = service.compute(candidate, evidence, classifications);
    const second = service.compute(candidate, evidence, classifications);

    expect(first).toEqual(second);
    expect(first).not.toBe(second);
    expect(assessEvidenceLevel).toHaveBeenCalledTimes(1);
  });
});
