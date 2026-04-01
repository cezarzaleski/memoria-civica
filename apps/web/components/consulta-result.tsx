import type { ConsultationResponse } from "@/domain/models";

function renderTrafficLightLabel(value: ConsultationResponse["traffic_light"]): string {
  switch (value) {
    case "red":
      return "Atenção alta";
    case "yellow":
      return "Exige cautela";
    case "green":
      return "Sinal favorável";
    default:
      return "Base insuficiente";
  }
}

export function ConsultaResult({
  response
}: Readonly<{
  response: ConsultationResponse;
}>): React.JSX.Element {
  const trafficLightClass = `pill ${response.traffic_light}`;

  return (
    <section className="result-card" aria-live="polite">
      <div className="result-meta">
        <span className={trafficLightClass}>{renderTrafficLightLabel(response.traffic_light)}</span>
        <span className="pill gray">Confianca {response.confidence}</span>
      </div>
      <h2>{response.candidate.canonical_name}</h2>
      <p>{response.summary}</p>

      {response.reasons.length > 0 ? (
        <ul className="reason-list">
          {response.reasons.map((reason) => {
            return <li key={reason}>{reason}</li>;
          })}
        </ul>
      ) : null}

      {response.sources.length > 0 ? (
        <ul className="source-list">
          {response.sources.map((source) => {
            return (
              <li key={source}>
                <a href={source} rel="noreferrer" target="_blank">
                  Ver fonte
                </a>
              </li>
            );
          })}
        </ul>
      ) : null}
    </section>
  );
}
