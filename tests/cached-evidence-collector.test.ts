import { describe, expect, it, vi } from "vitest";

import type { CollectionPlan, RawEvidence, ResolvedCandidate } from "@/domain/models";
import { InMemoryCacheStore } from "@/services/cache-store";
import { CachedEvidenceCollector } from "@/services/cached-evidence-collector";

describe("CachedEvidenceCollector", () => {
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

  const plan: CollectionPlan = {
    profile: "incumbent_federal",
    requested_signals: ["evidence_level", "coherence"],
    tasks: [
      {
        objective: "confirmar_identidade_legislativa",
        params: {
          camara_id: "220639",
          name: "Erika Hilton"
        },
        priority: 1,
        source: "camara"
      }
    ]
  };

  it("reuses cached evidence for repeated collection plans", async () => {
    const delegateEvidence: RawEvidence[] = [
      {
        collected_at: "2026-04-01T12:00:00.000Z",
        evidence_type: "legislative_profile",
        person_id: "camara:220639",
        signal_type: "evidence_level",
        source_name: "camara",
        source_url: "https://dadosabertos.camara.leg.br/api/v2/deputados/220639",
        strength: "strong_official",
        summary: "Cadastro oficial."
      }
    ];
    const delegate = {
      collect: vi.fn().mockResolvedValue(delegateEvidence)
    };
    const collector = new CachedEvidenceCollector(delegate, {
      cacheStore: new InMemoryCacheStore(),
      ttlMs: 60_000
    });

    const first = await collector.collect(candidate, plan);
    const second = await collector.collect(candidate, plan);

    expect(delegate.collect).toHaveBeenCalledTimes(1);
    expect(first).toEqual(delegateEvidence);
    expect(second).toEqual(delegateEvidence);
    expect(first).not.toBe(second);
  });
});
