import { describe, expect, it } from "vitest";

import {
  buildGrayResponse,
  validateConsultCandidateRequest
} from "@/contracts/consultation";

describe("consultation contracts", () => {
  it("normalizes a valid consultation request", () => {
    const result = validateConsultCandidateRequest({
      candidate_name: "  Erika Hilton  ",
      uf: "sp",
      party: "psol",
      user_priorities: ["transparencia", "direitos humanos"]
    });

    expect(result).toEqual({
      candidate_name: "Erika Hilton",
      office: "deputado_federal",
      party: "PSOL",
      uf: "SP",
      user_priorities: ["transparencia", "direitos humanos"]
    });
  });

  it("accepts deputado_distrital only for DF", () => {
    const result = validateConsultCandidateRequest({
      candidate_name: "Jane Klébia",
      office: "deputado_distrital",
      uf: "df"
    });

    expect(result.office).toBe("deputado_distrital");
    expect(result.uf).toBe("DF");
  });

  it("rejects deputado_distrital outside DF", () => {
    expect(() =>
      validateConsultCandidateRequest({
        candidate_name: "Nome Teste",
        office: "deputado_distrital",
        uf: "GO"
      })
    ).toThrow("deputado_distrital requires uf=DF");
  });

  it("builds the canonical gray response for insufficient evidence", () => {
    const response = buildGrayResponse({
      candidate: {
        ambiguity_level: "none",
        canonical_name: "Erika Hilton",
        office: "deputado_federal",
        official_ids: {
          camara_id: "220639"
        },
        party: "PSOL",
        status: "incumbent",
        uf: "SP"
      },
      alerts: ["Coleta de evidencias ainda nao implementada nesta fase."]
    });

    expect(response.traffic_light).toBe("gray");
    expect(response.confidence).toBe("low");
    expect(response.summary).toContain("base suficiente");
    expect(response.signals.evidence_level.status).toBe("insufficient");
    expect(response.sources).toEqual([]);
  });
});
