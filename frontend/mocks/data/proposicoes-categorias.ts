import type { ProposicaoCategoria } from '@/lib/types';
import { CATEGORIAS_CIVICAS_FIXTURES } from './categorias-civicas';
import { PROPOSICOES_FIXTURES } from './proposicoes';

function buildCreatedAt(index: number): string {
  const month = index % 12;
  const day = (index % 28) + 1;

  return new Date(Date.UTC(2025, month, day, 9, 0, 0)).toISOString();
}

function buildProposicoesCategorias(): ProposicaoCategoria[] {
  const relacoes: ProposicaoCategoria[] = [];
  let relationId = 1;

  PROPOSICOES_FIXTURES.slice(0, 60).forEach((proposicao, index) => {
    const categoriaPrincipal =
      CATEGORIAS_CIVICAS_FIXTURES[index % CATEGORIAS_CIVICAS_FIXTURES.length] ?? CATEGORIAS_CIVICAS_FIXTURES[0];

    relacoes.push({
      id: relationId,
      proposicao_id: proposicao.id,
      categoria_id: categoriaPrincipal.id,
      origem: 'manual',
      created_at: buildCreatedAt(relationId),
      categoria: categoriaPrincipal,
    });

    relationId += 1;

    if (proposicao.id % 3 === 0) {
      const categoriaSecundaria =
        CATEGORIAS_CIVICAS_FIXTURES[(index + 2) % CATEGORIAS_CIVICAS_FIXTURES.length] ??
        CATEGORIAS_CIVICAS_FIXTURES[0];

      relacoes.push({
        id: relationId,
        proposicao_id: proposicao.id,
        categoria_id: categoriaSecundaria.id,
        origem: 'automatica',
        confianca: Number((0.72 + ((proposicao.id % 9) * 0.03)).toFixed(2)),
        created_at: buildCreatedAt(relationId),
        categoria: categoriaSecundaria,
      });

      relationId += 1;
    }
  });

  return relacoes;
}

export const PROPOSICOES_CATEGORIAS_FIXTURES: ProposicaoCategoria[] = buildProposicoesCategorias();

export function getCategoriasByProposicaoId(proposicaoId: number): ProposicaoCategoria[] {
  return PROPOSICOES_CATEGORIAS_FIXTURES.filter((relacao) => relacao.proposicao_id === proposicaoId);
}
