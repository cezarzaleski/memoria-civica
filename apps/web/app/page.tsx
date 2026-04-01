import { ConsultaForm } from "../components/consulta-form";

export default function HomePage(): React.JSX.Element {
  return (
    <main className="app-shell">
      <section className="hero-card">
        <div className="hero-top">
          <div>
            <p className="eyebrow">Consulta simples</p>
            <h1>Descubra o que ja da para verificar sobre um candidato.</h1>
            <p className="hero-copy">
              Digite o nome e veja uma resposta curta, com explicacao e fontes.
              Se faltar contexto, a tela vai pedir so o necessario.
            </p>
          </div>
          <span className="install-badge">PWA inicial</span>
        </div>
        <ConsultaForm />
      </section>
    </main>
  );
}
