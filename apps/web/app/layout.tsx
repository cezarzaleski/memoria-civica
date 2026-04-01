import type { Metadata } from "next";

import "./globals.css";

export const metadata: Metadata = {
  applicationName: "Memoria Civica",
  description: "Consulta simples de candidatos com explicacao e fontes.",
  title: "Memoria Civica"
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>): React.JSX.Element {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}
