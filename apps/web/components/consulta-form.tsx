"use client";

import { useState } from "react";

import type { ConsultationResponse } from "@/domain/models";
import { ConsultaResult } from "./consulta-result";

type UiState =
  | { kind: "idle" }
  | { kind: "loading" }
  | { kind: "error"; message: string }
  | { kind: "ambiguity"; response: ConsultationResponse }
  | { kind: "success"; response: ConsultationResponse };

function extractApiError(payload: unknown): string {
  if (
    typeof payload === "object" &&
    payload !== null &&
    "error" in payload &&
    typeof payload.error === "object" &&
    payload.error !== null &&
    "message" in payload.error &&
    typeof payload.error.message === "string"
  ) {
    return payload.error.message;
  }

  return "Nao foi possivel concluir a consulta agora.";
}

function isAmbiguousResponse(response: ConsultationResponse): boolean {
  return response.candidate.resolution_kind === "ambiguous";
}

export function ConsultaForm(): React.JSX.Element {
  const [candidateName, setCandidateName] = useState("");
  const [party, setParty] = useState("");
  const [showHints, setShowHints] = useState(false);
  const [state, setState] = useState<UiState>({ kind: "idle" });
  const [uf, setUf] = useState("");

  async function submitConsulta(event: React.FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setState({ kind: "loading" });

    const response = await fetch("/api/consultas", {
      body: JSON.stringify({
        candidate_name: candidateName,
        party: party || undefined,
        uf: uf || undefined
      }),
      headers: {
        "content-type": "application/json"
      },
      method: "POST"
    });

    const payload: unknown = await response.json();

    if (!response.ok) {
      setState({
        kind: "error",
        message: extractApiError(payload)
      });
      return;
    }

    const consultation = payload as ConsultationResponse;

    if (isAmbiguousResponse(consultation)) {
      setShowHints(true);
      setState({
        kind: "ambiguity",
        response: consultation
      });
      return;
    }

    setState({
      kind: "success",
      response: consultation
    });
  }

  const requires =
    state.kind === "ambiguity" ? new Set(state.response.candidate.requires ?? []) : new Set<string>();

  return (
    <div className="consulta-panel">
      <form
        className="consulta-form"
        onSubmit={(event) => {
          void submitConsulta(event);
        }}
      >
        <label className="field-label">
          Nome do candidato
          <span>Comece só com o nome. Se faltar contexto, a tela pede o resto.</span>
          <input
            className="text-input"
            name="candidate_name"
            onChange={(event) => {
              setCandidateName(event.target.value);
            }}
            placeholder="Ex.: Tabata Amaral"
            required
            value={candidateName}
          />
        </label>

        {showHints ? (
          <div className="hint-grid">
            <label className="field-label">
              UF
              <span>Preencha se a tela pedir para diferenciar pessoas com o mesmo nome.</span>
              <input
                aria-label="UF"
                className="text-input"
                name="uf"
                onChange={(event) => {
                  setUf(event.target.value.toUpperCase());
                }}
                placeholder="Ex.: SP"
                value={uf}
              />
            </label>
            <label className="field-label">
              Partido
              <span>Use a sigla do partido só quando precisar refinar a busca.</span>
              <input
                aria-label="Partido"
                className="text-input"
                name="party"
                onChange={(event) => {
                  setParty(event.target.value.toUpperCase());
                }}
                placeholder="Ex.: PSB"
                value={party}
              />
            </label>
          </div>
        ) : null}

        <div className="actions">
          <button className="primary-button" disabled={state.kind === "loading"} type="submit">
            {state.kind === "loading" ? "Consultando..." : "Consultar agora"}
          </button>
          {!showHints ? (
            <button
              className="ghost-button"
              onClick={() => {
                setShowHints(true);
              }}
              type="button"
            >
              Adicionar UF ou partido
            </button>
          ) : null}
        </div>
      </form>

      {state.kind === "error" ? (
        <section className="feedback-card error" role="alert">
          <strong>Não deu certo desta vez.</strong>
          <p>{state.message}</p>
        </section>
      ) : null}

      {state.kind === "ambiguity" ? (
        <section className="feedback-card ambiguous" role="status">
          <strong>Faltou contexto para identificar a pessoa certa.</strong>
          <p>{state.response.summary}</p>
          {requires.size > 0 ? (
            <p>
              Complete
              {requires.has("uf") ? " a UF" : ""}
              {requires.has("uf") && requires.has("party") ? " e" : ""}
              {requires.has("party") ? " o partido" : ""}
              {" "}para tentar de novo.
            </p>
          ) : null}
        </section>
      ) : null}

      {state.kind === "success" ? <ConsultaResult response={state.response} /> : null}
    </div>
  );
}
