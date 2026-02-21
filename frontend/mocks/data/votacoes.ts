import { ResultadoVotacao, type Votacao } from '@/lib/types';
import { PROPOSICOES_FIXTURES, getProposicaoById } from './proposicoes';
import { buildPlacarFromVotacao } from './votos';

const TOTAL_VOTACOES_FIXTURE = 50;
const SIGLAS_ORGAO = ['PLEN', 'CCJC', 'CFT', 'CSSF', 'CMULHER'] as const;

function buildDataHora(index: number): string {
  const baseDate = Date.UTC(2025, 11, 20, 18, 30, 0);
  const displacementDays = (index - 1) * 2;
  const displacementHours = index % 4;

  return new Date(baseDate - displacementDays * 24 * 60 * 60 * 1000 - displacementHours * 60 * 60 * 1000).toISOString();
}

function buildResultado(votacaoId: number, votosSim: number, votosNao: number): Votacao['resultado'] {
  if (votacaoId % 10 === 0 && votosSim >= votosNao) {
    return ResultadoVotacao.APROVADO_COM_SUBSTITUTIVO;
  }

  return votosSim >= votosNao ? ResultadoVotacao.APROVADO : ResultadoVotacao.REJEITADO;
}

function buildDescricao(votacaoId: number, tema: string): string {
  return `Sessão deliberativa nº ${2020 + votacaoId}: ${tema}.`;
}

function buildVotacao(id: number): Votacao {
  const proposicao = getProposicaoById(PROPOSICOES_FIXTURES, id);
  const placar = buildPlacarFromVotacao(id);
  const siglaOrgao = SIGLAS_ORGAO[(id - 1) % SIGLAS_ORGAO.length] ?? SIGLAS_ORGAO[0];
  const tema = proposicao?.ementa_simplificada ?? proposicao?.ementa ?? 'matéria legislativa em apreciação';

  return {
    id,
    proposicao_id: proposicao?.id,
    proposicao,
    data_hora: buildDataHora(id),
    resultado: buildResultado(id, placar.votos_sim, placar.votos_nao),
    placar,
    eh_nominal: id % 5 !== 0,
    descricao: id % 6 === 0 ? undefined : buildDescricao(id, tema),
    sigla_orgao: id % 7 === 0 ? undefined : siglaOrgao,
  };
}

export const VOTACOES_FIXTURES: Votacao[] = Array.from(
  { length: TOTAL_VOTACOES_FIXTURE },
  (_, index) => buildVotacao(index + 1)
).sort((first, second) => new Date(second.data_hora).getTime() - new Date(first.data_hora).getTime());

function normalizeCount(count: number): number {
  if (!Number.isFinite(count)) {
    return 0;
  }

  return Math.max(0, Math.floor(count));
}

export function generateVotacoes(count: number = TOTAL_VOTACOES_FIXTURE): Votacao[] {
  const normalizedCount = normalizeCount(count);

  if (normalizedCount <= VOTACOES_FIXTURES.length) {
    return VOTACOES_FIXTURES.slice(0, normalizedCount);
  }

  const additionalVotacoes = Array.from({ length: normalizedCount - VOTACOES_FIXTURES.length }, (_, index) =>
    buildVotacao(VOTACOES_FIXTURES.length + index + 1)
  );

  return [...VOTACOES_FIXTURES, ...additionalVotacoes].sort(
    (first, second) => new Date(second.data_hora).getTime() - new Date(first.data_hora).getTime()
  );
}

export function getVotacaoById(votacoes: Votacao[], id: number): Votacao | undefined {
  return votacoes.find((votacao) => votacao.id === id);
}
