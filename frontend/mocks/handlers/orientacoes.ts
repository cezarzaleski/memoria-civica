import { http, HttpResponse } from 'msw';
import { getOrientacoesByVotacaoId } from '../data/orientacoes';
import { generateVotacoes } from '../data/votacoes';
import { createPaginatedResponse, getPaginationParams, notFoundError, parseStrictId, validationError } from './utils';

const votacaoIds = new Set(generateVotacoes(50).map((votacao) => votacao.id));

export const orientacoesHandlers = [
  /**
   * GET /api/v1/votacoes/:votacao_id/orientacoes
   * Lista orientações de bancada vinculadas à votação
   */
  http.get('*/api/v1/votacoes/:votacao_id/orientacoes', ({ request, params }) => {
    const votacaoId = parseStrictId(params.votacao_id as string | undefined);

    if (!votacaoId) {
      return validationError('ID de votação inválido');
    }

    if (!votacaoIds.has(votacaoId)) {
      return notFoundError('Votação não encontrada');
    }

    const orientacoes = getOrientacoesByVotacaoId(votacaoId);
    const url = new URL(request.url);
    const { page, perPage } = getPaginationParams(url);

    return HttpResponse.json(createPaginatedResponse(orientacoes, page, perPage));
  }),
];
