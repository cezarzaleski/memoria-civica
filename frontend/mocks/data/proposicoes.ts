import { TipoProposicao, type Proposicao } from '@/lib/types';

const TOTAL_PROPOSICOES_FIXTURE = 80;

const TIPOS_PROPOSICOES: TipoProposicao[] = [
  TipoProposicao.PL,
  TipoProposicao.PEC,
  TipoProposicao.MP,
  TipoProposicao.PLP,
  TipoProposicao.PDC,
  TipoProposicao.REQ,
  TipoProposicao.RIC,
  TipoProposicao.PFC,
  'PDL',
  'MSC',
];

const TEMAS = [
  'reforma tributária solidária',
  'saúde pública no SUS',
  'transição energética',
  'defesa dos direitos das mulheres',
  'infraestrutura ferroviária',
  'inclusão digital em escolas públicas',
  'segurança alimentar',
  'prevenção a desastres climáticos',
  'transparência e controle social',
  'economia criativa e inovação',
  'combate ao trabalho escravo',
  'fortalecimento da agricultura familiar',
] as const;

function formatISODateForProposicao(id: number): string {
  const year = 2022 + (id % 4);
  const month = (id * 3) % 12;
  const day = ((id * 5) % 27) + 1;

  return new Date(Date.UTC(year, month, day, 14, 0, 0)).toISOString();
}

function buildNumeroProposicao(id: number, tipo: TipoProposicao): number {
  const tipoSeed = tipo.length * 97;
  return tipoSeed + id * 11;
}

function buildEmenta(id: number, tema: string): string {
  const artigosReferencia = 20 + (id % 80);

  return `Dispõe sobre ${tema} e altera dispositivos da Lei nº ${artigosReferencia}.`;
}

function buildProposicao(id: number): Proposicao {
  const tipo = TIPOS_PROPOSICOES[(id - 1) % TIPOS_PROPOSICOES.length] ?? TipoProposicao.PL;
  const tema = TEMAS[(id - 1) % TEMAS.length] ?? TEMAS[0];
  const numero = buildNumeroProposicao(id, tipo);

  return {
    id,
    tipo,
    numero,
    ano: 2022 + (id % 4),
    ementa: buildEmenta(id, tema),
    ementa_simplificada: id % 4 === 0 ? undefined : `Proposição sobre ${tema}`,
    autor_id: id % 7 === 0 ? undefined : ((id * 13) % 513) + 1,
    data_apresentacao: formatISODateForProposicao(id),
  };
}

export const PROPOSICOES_FIXTURES: Proposicao[] = Array.from(
  { length: TOTAL_PROPOSICOES_FIXTURE },
  (_, index) => buildProposicao(index + 1)
);

function normalizeCount(count: number): number {
  if (!Number.isFinite(count)) {
    return 0;
  }

  return Math.max(0, Math.floor(count));
}

export function generateProposicoes(count: number = 50): Proposicao[] {
  const normalizedCount = normalizeCount(count);

  if (normalizedCount <= PROPOSICOES_FIXTURES.length) {
    return PROPOSICOES_FIXTURES.slice(0, normalizedCount);
  }

  return Array.from({ length: normalizedCount }, (_, index) => buildProposicao(index + 1));
}

export function getProposicaoById(proposicoes: Proposicao[], id: number): Proposicao | undefined {
  return proposicoes.find((proposicao) => proposicao.id === id);
}
