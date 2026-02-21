import type { VotacaoProposicao } from '@/lib/types';
import { PROPOSICOES_FIXTURES } from './proposicoes';

const TOTAL_VOTACOES_FIXTURE = 50;

function buildCreatedAt(votacaoId: number, offset: number): string {
  return new Date(Date.UTC(2025, 1, votacaoId, 18, offset * 10, 0)).toISOString();
}

function buildVotacoesProposicoes(): VotacaoProposicao[] {
  const relacoes: VotacaoProposicao[] = [];
  let relationId = 1;

  for (let votacaoId = 1; votacaoId <= TOTAL_VOTACOES_FIXTURE; votacaoId += 1) {
    const proposicaoPrincipal =
      PROPOSICOES_FIXTURES[(votacaoId - 1) % PROPOSICOES_FIXTURES.length] ?? PROPOSICOES_FIXTURES[0];

    relacoes.push({
      id: relationId,
      votacao_id: votacaoId,
      proposicao_id: proposicaoPrincipal.id,
      titulo: `${proposicaoPrincipal.tipo} ${proposicaoPrincipal.numero}/${proposicaoPrincipal.ano}`,
      ementa: proposicaoPrincipal.ementa,
      sigla_tipo: proposicaoPrincipal.tipo,
      numero: proposicaoPrincipal.numero,
      ano: proposicaoPrincipal.ano,
      eh_principal: true,
      created_at: buildCreatedAt(votacaoId, 1),
      proposicao: proposicaoPrincipal,
    });

    relationId += 1;

    if (votacaoId % 4 === 0) {
      const proposicaoSecundaria =
        PROPOSICOES_FIXTURES[(votacaoId + 10) % PROPOSICOES_FIXTURES.length] ?? PROPOSICOES_FIXTURES[0];

      relacoes.push({
        id: relationId,
        votacao_id: votacaoId,
        proposicao_id: proposicaoSecundaria.id,
        titulo: `${proposicaoSecundaria.tipo} ${proposicaoSecundaria.numero}/${proposicaoSecundaria.ano}`,
        ementa: proposicaoSecundaria.ementa,
        sigla_tipo: proposicaoSecundaria.tipo,
        numero: proposicaoSecundaria.numero,
        ano: proposicaoSecundaria.ano,
        eh_principal: false,
        created_at: buildCreatedAt(votacaoId, 2),
        proposicao: proposicaoSecundaria,
      });

      relationId += 1;
    }
  }

  return relacoes;
}

export const VOTACOES_PROPOSICOES_FIXTURES: VotacaoProposicao[] = buildVotacoesProposicoes();

export function getProposicoesByVotacaoId(votacaoId: number): VotacaoProposicao[] {
  return VOTACOES_PROPOSICOES_FIXTURES.filter((item) => item.votacao_id === votacaoId);
}
