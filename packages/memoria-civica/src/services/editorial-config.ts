import type { EvidenceStrength } from "@/domain/models";

export type EditorialThemeId =
  | "corrupcao_transparencia"
  | "seguranca_publica"
  | "economia_custo_vida"
  | "direitos_das_mulheres"
  | "direitos_humanos_liberdades_civis";

export interface EditorialThemeRule {
  readonly aliases: readonly string[];
  readonly allowed_signals: readonly ("coherence" | "integrity")[];
  readonly evidence_terms: readonly string[];
  readonly id: EditorialThemeId;
  readonly label: string;
}

export const MINIMUM_VALUES_FIT_WATCHLIST = [
  {
    aliases: ["corrupcao", "corrupcao e transparencia", "transparencia"],
    allowed_signals: ["integrity"],
    evidence_terms: [
      "contas",
      "ressalvas",
      "devolucao ao tesouro",
      "irregular",
      "sancao",
      "acordao",
      "integridade",
      "transparencia",
      "tcu",
      "ceis",
      "cnep"
    ],
    id: "corrupcao_transparencia",
    label: "Corrupcao e Transparencia"
  },
  {
    aliases: ["seguranca", "seguranca publica"],
    allowed_signals: ["coherence"],
    evidence_terms: ["seguranca", "violencia", "crime", "penal", "policia", "prisao"],
    id: "seguranca_publica",
    label: "Seguranca Publica"
  },
  {
    aliases: ["economia", "custo de vida", "economia e custo de vida"],
    allowed_signals: ["coherence"],
    evidence_terms: [
      "economia",
      "custo de vida",
      "renda",
      "salario",
      "emprego",
      "trabalho",
      "imposto",
      "tribut"
    ],
    id: "economia_custo_vida",
    label: "Economia e Custo de Vida"
  },
  {
    aliases: ["direitos das mulheres", "mulheres"],
    allowed_signals: ["coherence"],
    evidence_terms: [
      "mulher",
      "mulheres",
      "violencia contra a mulher",
      "genero",
      "igualdade",
      "maternidade"
    ],
    id: "direitos_das_mulheres",
    label: "Direitos das Mulheres"
  },
  {
    aliases: [
      "direitos humanos",
      "liberdades civis",
      "direitos humanos e liberdades civis"
    ],
    allowed_signals: ["coherence"],
    evidence_terms: [
      "direitos humanos",
      "liberdades civis",
      "liberdade",
      "racismo",
      "discriminacao",
      "lgbt",
      "privacidade"
    ],
    id: "direitos_humanos_liberdades_civis",
    label: "Direitos Humanos e Liberdades Civis"
  }
] as const satisfies readonly EditorialThemeRule[];

function normalizeText(value: string): string {
  return value
    .normalize("NFD")
    .replace(/\p{Diacritic}/gu, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
}

function isEligibleStrength(strength: EvidenceStrength): boolean {
  return strength === "strong_official" || strength === "official_partial";
}

export function normalizeSupportedPriorities(
  priorities: readonly string[]
): readonly EditorialThemeId[] {
  const normalized = priorities
    .map((priority) => normalizeText(priority))
    .filter((priority) => priority !== "");
  const themeByAlias = new Map<string, EditorialThemeId>();

  for (const theme of MINIMUM_VALUES_FIT_WATCHLIST) {
    themeByAlias.set(normalizeText(theme.label), theme.id);
    themeByAlias.set(normalizeText(theme.id.replaceAll("_", " ")), theme.id);

    for (const alias of theme.aliases) {
      themeByAlias.set(normalizeText(alias), theme.id);
    }
  }

  const resolved: EditorialThemeId[] = [];
  const seen = new Set<EditorialThemeId>();

  for (const priority of normalized) {
    const themeId = themeByAlias.get(priority);

    if (themeId === undefined || seen.has(themeId)) {
      continue;
    }

    seen.add(themeId);
    resolved.push(themeId);
  }

  return resolved;
}

export function matchesEditorialTheme(
  theme: EditorialThemeRule,
  evidenceText: string,
  signalType: "coherence" | "integrity",
  strength: EvidenceStrength
): boolean {
  if (!theme.allowed_signals.includes(signalType)) {
    return false;
  }

  if (!isEligibleStrength(strength)) {
    return false;
  }

  const normalizedEvidenceText = normalizeText(evidenceText);

  return theme.evidence_terms.some((term) => {
    return normalizedEvidenceText.includes(normalizeText(term));
  });
}

export function normalizeForThemeMatch(value: string): string {
  return normalizeText(value);
}
