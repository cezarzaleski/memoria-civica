import type { Deputado } from '@/lib/types';

const TOTAL_DEPUTADOS_CAMARA = 513;
const CAMERA_PHOTO_BASE_URL = 'https://www.camara.leg.br/internet/deputado/bandep';

const NOMES = [
  'Ana',
  'Bruno',
  'Camila',
  'Daniel',
  'Eduarda',
  'Felipe',
  'Gabriela',
  'Henrique',
  'Isabela',
  'João',
  'Karina',
  'Leonardo',
  'Mariana',
  'Nicolas',
  'Otávio',
  'Patrícia',
  'Rafaela',
  'Sérgio',
  'Tatiana',
  'Vinícius',
  'Yasmin',
  'André',
  'Beatriz',
  'Caio',
  'Débora',
  'Fábio',
  'Giovana',
  'Helena',
  'Igor',
  'Juliana',
  'Luana',
  'Marcelo',
] as const;

const SOBRENOMES = [
  'Silva',
  'Santos',
  'Oliveira',
  'Souza',
  'Pereira',
  'Costa',
  'Rodrigues',
  'Almeida',
  'Nascimento',
  'Lima',
  'Araújo',
  'Fernandes',
  'Carvalho',
  'Gomes',
  'Martins',
  'Rocha',
  'Melo',
  'Ribeiro',
  'Barbosa',
  'Teixeira',
  'Freitas',
  'Moura',
  'Rezende',
  'Tavares',
  'Assis',
  'Batista',
  'Castro',
  'Duarte',
  'Figueiredo',
  'Vieira',
  'Mendes',
  'Correia',
] as const;

const PARTIDOS = [
  'PL',
  'PT',
  'MDB',
  'UNIÃO',
  'PP',
  'PSD',
  'REPUBLICANOS',
  'PSB',
  'PDT',
  'PSDB',
  'PODE',
  'AVANTE',
  'CIDADANIA',
  'NOVO',
  'SOLIDARIEDADE',
] as const;

const UFS = [
  'AC',
  'AL',
  'AP',
  'AM',
  'BA',
  'CE',
  'DF',
  'ES',
  'GO',
  'MA',
  'MT',
  'MS',
  'MG',
  'PA',
  'PB',
  'PR',
  'PE',
  'PI',
  'RJ',
  'RN',
  'RS',
  'RO',
  'RR',
  'SC',
  'SP',
  'SE',
  'TO',
] as const;

function buildDeputado(id: number): Deputado {
  const nome = NOMES[(id - 1) % NOMES.length] ?? NOMES[0];
  const sobrenome = SOBRENOMES[Math.floor((id - 1) / NOMES.length) % SOBRENOMES.length] ?? SOBRENOMES[0];
  const sigla_partido = PARTIDOS[(id - 1) % PARTIDOS.length] ?? PARTIDOS[0];
  const uf = UFS[(id - 1) % UFS.length] ?? UFS[0];

  return {
    id,
    nome: `${nome} ${sobrenome}`,
    sigla_partido,
    uf,
    foto_url: `${CAMERA_PHOTO_BASE_URL}/${100000 + id}.jpg`,
    email: `deputado.${id}@camara.leg.br`,
  };
}

export const DEPUTADOS_FIXTURES: Deputado[] = Array.from(
  { length: TOTAL_DEPUTADOS_CAMARA },
  (_, index) => buildDeputado(index + 1)
);

function normalizeCount(count: number): number {
  if (!Number.isFinite(count)) {
    return 0;
  }

  return Math.max(0, Math.floor(count));
}

export function generateDeputados(count: number = TOTAL_DEPUTADOS_CAMARA): Deputado[] {
  const normalizedCount = normalizeCount(count);

  if (normalizedCount <= DEPUTADOS_FIXTURES.length) {
    return DEPUTADOS_FIXTURES.slice(0, normalizedCount);
  }

  return Array.from({ length: normalizedCount }, (_, index) => buildDeputado(index + 1));
}

export function getDeputadoById(deputados: Deputado[], id: number): Deputado | undefined {
  return deputados.find((deputado) => deputado.id === id);
}

export function filterDeputadosByNome(deputados: Deputado[], nome: string): Deputado[] {
  const lowerCaseNome = nome.toLowerCase();
  return deputados.filter((deputado) => deputado.nome.toLowerCase().includes(lowerCaseNome));
}

export function filterDeputadosByPartido(deputados: Deputado[], partido: string): Deputado[] {
  return deputados.filter((deputado) => deputado.sigla_partido === partido);
}

export function filterDeputadosByUF(deputados: Deputado[], uf: string): Deputado[] {
  return deputados.filter((deputado) => deputado.uf === uf);
}
