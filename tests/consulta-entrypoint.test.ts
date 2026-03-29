import { describe, expect, it, vi } from "vitest";

import { parseConsultaCliArgs, runConsultaEntrypoint } from "@/cli/consulta-entrypoint";

describe("consulta entrypoint", () => {
  it("parses CLI flags into the canonical request shape", () => {
    expect(
      parseConsultaCliArgs([
        "--candidate",
        "Tabata Amaral",
        "--office",
        "deputado_federal",
        "--uf",
        "sp",
        "--party",
        "psb",
        "--priority",
        "educacao",
        "--priority",
        "transparencia"
      ])
    ).toEqual({
      candidate_name: "Tabata Amaral",
      office: "deputado_federal",
      party: "psb",
      uf: "sp",
      user_priorities: ["educacao", "transparencia"]
    });
  });

  it("writes the orchestrated response to stdout as formatted JSON", async () => {
    const write = vi.fn();

    await runConsultaEntrypoint(
      ["--candidate", "Tabata Amaral", "--office", "deputado_federal"],
      {
        stderr: { write: vi.fn() },
        stdout: { write }
      },
      {
        consult: vi.fn().mockResolvedValue({
          execution: {
            duration_ms: 4,
            started_at: "2026-03-29T00:00:00.000Z",
            status: "completed",
            steps: [
              "request_validated",
              "identity_resolved",
              "collection_planned",
              "response_assembled"
            ],
            trace_id: "trace-1"
          },
          response: {
            alerts: [],
            candidate: {
              canonical_name: "Tabata Amaral",
              official_ids: {},
              status: "challenger"
            },
            confidence: "low",
            reasons: ["Consulta inicial recebida."],
            signals: {
              coherence: { evidence_ids: [], reasons: [], status: "insufficient" },
              evidence_level: {
                evidence_ids: [],
                reasons: ["Sem coleta de evidencias nesta fase."],
                status: "insufficient"
              },
              integrity: { evidence_ids: [], reasons: [], status: "insufficient" },
              values_fit: { evidence_ids: [], reasons: [], status: "insufficient" }
            },
            sources: [],
            summary: "Sem base suficiente para uma conclusao nesta fase.",
            traffic_light: "gray"
          }
        })
      }
    );

    expect(write).toHaveBeenCalledOnce();
    expect(write.mock.calls[0]?.[0]).toContain('"traffic_light": "gray"');
  });
});
