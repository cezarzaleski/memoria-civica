// @vitest-environment jsdom

import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { ConsultaForm } from "../apps/web/components/consulta-form";

describe("web consulta page", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("renders a result on the same screen for a successful consultation", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        json: () => {
          return Promise.resolve({
            alerts: [],
            candidate: {
              ambiguity_level: "none",
              canonical_name: "Tabata Amaral",
              match_count: 1,
              official_ids: {
                camara_id: "204534"
              },
              party: "PSB",
              resolution_kind: "resolved",
              status: "incumbent",
              uf: "SP"
            },
            confidence: "high",
            reasons: ["Ha base oficial inicial suficiente para a consulta."],
            signals: {
              coherence: { evidence_ids: [], reasons: [], status: "positive" },
              evidence_level: { evidence_ids: [], reasons: [], status: "positive" },
              integrity: { evidence_ids: [], reasons: [], status: "mixed" },
              values_fit: { evidence_ids: [], reasons: [], status: "insufficient" }
            },
            sources: ["https://dadosabertos.camara.leg.br/api/v2/deputados/204534"],
            summary:
              "A consulta encontrou base oficial inicial para Tabata Amaral, mas a leitura ainda exige cautela.",
            traffic_light: "yellow"
          });
        },
        ok: true
      })
    );

    render(<ConsultaForm />);

    await userEvent.type(screen.getByLabelText("Nome do candidato"), "Tabata Amaral");
    await userEvent.click(screen.getByRole("button", { name: "Consultar agora" }));

    await screen.findByText("Tabata Amaral");
    expect(
      screen.getByText(
        "A consulta encontrou base oficial inicial para Tabata Amaral, mas a leitura ainda exige cautela."
      )
    ).not.toBeNull();
  });

  it("shows the ambiguity state and asks for missing hints", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        json: () => {
          return Promise.resolve({
            alerts: [
              "Faltou contexto para identificar a pessoa certa. Informe UF e o partido para continuar."
            ],
            candidate: {
              ambiguity_level: "strong",
              canonical_name: "Joao Silva",
              match_count: 2,
              official_ids: {},
              requires: ["uf", "party"],
              resolution_kind: "ambiguous",
              status: "challenger"
            },
            confidence: "low",
            reasons: [
              "Faltou contexto para identificar a pessoa certa. Informe UF e o partido para continuar."
            ],
            signals: {
              coherence: { evidence_ids: [], reasons: [], status: "insufficient" },
              evidence_level: { evidence_ids: [], reasons: [], status: "insufficient" },
              integrity: { evidence_ids: [], reasons: [], status: "insufficient" },
              values_fit: { evidence_ids: [], reasons: [], status: "insufficient" }
            },
            sources: [],
            summary:
              "A consulta parou na etapa de identidade porque faltou contexto para identificar a pessoa certa.",
            traffic_light: "gray"
          });
        },
        ok: true
      })
    );

    render(<ConsultaForm />);

    await userEvent.type(screen.getByLabelText("Nome do candidato"), "Joao Silva");
    await userEvent.click(screen.getByRole("button", { name: "Consultar agora" }));

    await screen.findByText("Faltou contexto para identificar a pessoa certa.");
    expect(screen.getByLabelText("UF")).not.toBeNull();
    expect(screen.getByLabelText("Partido")).not.toBeNull();
  });

  it("shows a simple error when the API fails", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        json: () => {
          return Promise.resolve({
            error: {
              code: "API_DOWN",
              message: "Servico indisponivel no momento."
            }
          });
        },
        ok: false
      })
    );

    render(<ConsultaForm />);

    await userEvent.type(screen.getByLabelText("Nome do candidato"), "Nome Teste");
    await userEvent.click(screen.getByRole("button", { name: "Consultar agora" }));

    await waitFor(() => {
      expect(screen.getByText("Não deu certo desta vez.")).not.toBeNull();
    });
    expect(screen.getByText("Servico indisponivel no momento.")).not.toBeNull();
  });
});
