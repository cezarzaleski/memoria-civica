import { http, HttpResponse } from 'msw';
import type { Voto } from '@/lib/types';
import { generateVotos } from '../data/votos';
import { generateVotacoes } from '../data/votacoes';
import { createPaginatedResponse, getPaginationParams, notFoundError, parseStrictId, validationError } from './utils';

/**
 * Cache for generated votos per votação
 * This ensures consistent data for the same votação across multiple requests
 */
const votosCache = new Map<number, ReturnType<typeof generateVotos>>();
const votacaoIds = new Set(generateVotacoes(50).map((votacao) => votacao.id));

function getVotosByVotacaoId(votacaoId: number): Voto[] {
  if (!votosCache.has(votacaoId)) {
    votosCache.set(votacaoId, generateVotos(votacaoId));
  }

  return votosCache.get(votacaoId) ?? [];
}

function handleVotosList(requestUrl: string, votacaoId: number) {
  if (!votacaoIds.has(votacaoId)) {
    return notFoundError('Votação não encontrada');
  }

  const url = new URL(requestUrl);
  const { page, perPage } = getPaginationParams(url);
  const votos = getVotosByVotacaoId(votacaoId);

  return HttpResponse.json(createPaginatedResponse(votos, page, perPage));
}

/**
 * MSW handlers for votos endpoints
 *
 * Endpoints:
 * - GET /api/v1/votacoes/:id/votos - Get all votos (individual votes) for a specific votação
 * - GET /api/v1/votos?votacao_id=:id - Get votos with votação filter
 */
export const votosHandlers = [
  /**
   * GET /api/v1/votacoes/:votacao_id/votos
   * Get all 513 votos for a specific votação with nested deputado objects
   * Returns 404 if votação ID is invalid (non-existent votação)
   *
   * Note: In a real API, you'd validate that the votacao_id exists.
   * For this mock, we generate votos for any requested votação_id.
   */
  http.get('*/api/v1/votacoes/:votacao_id/votos', ({ request, params }) => {
    const votacao_id = parseStrictId(params.votacao_id as string | undefined);

    if (!votacao_id) {
      return validationError('ID de votação inválido');
    }

    return handleVotosList(request.url, votacao_id);
  }),

  /**
   * GET /api/v1/votos?votacao_id=:id
   * Lista votos por votação com filtro obrigatório de votacao_id
   */
  http.get('*/api/v1/votos', ({ request }) => {
    const url = new URL(request.url);
    const votacaoIdParam = url.searchParams.get('votacao_id');

    if (votacaoIdParam === null) {
      return validationError('Parâmetro votacao_id é obrigatório');
    }

    const votacaoId = parseStrictId(votacaoIdParam);
    if (!votacaoId) {
      return validationError('Parâmetro votacao_id inválido');
    }

    return handleVotosList(request.url, votacaoId);
  }),
];
