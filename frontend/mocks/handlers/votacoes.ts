import { http, HttpResponse } from 'msw';
import type { SingleResponse, Votacao } from '@/lib/types';
import { generateVotacoes, getVotacaoById } from '../data/votacoes';
import { getProposicoesByVotacaoId } from '../data/votacoes-proposicoes';
import { createPaginatedResponse, getPaginationParams, notFoundError, parseStrictId, validationError } from './utils';

/**
 * Generate the complete list of mock votações once
 * Already sorted by data descending (most recent first)
 */
const votacoes = generateVotacoes(50);

function parseBoolean(value: string | null): boolean | undefined {
  if (value === 'true') return true;
  if (value === 'false') return false;
  return undefined;
}

/**
 * MSW handlers for votações endpoints
 *
 * Endpoints:
 * - GET /api/v1/votacoes - List all votações (ordered by data_hora descending)
 * - GET /api/v1/votacoes/:id - Get a single votação by ID with nested proposicao
 */
export const votacoesHandlers = [
  /**
   * GET /api/v1/votacoes
   * List all votações ordered by date descending (most recent first)
   * Each votação includes its nested proposicao object
   */
  http.get('*/api/v1/votacoes', ({ request }) => {
    const url = new URL(request.url);
    const { page, perPage } = getPaginationParams(url);
    const siglaOrgao = url.searchParams.get('sigla_orgao');
    const ehNominal = parseBoolean(url.searchParams.get('eh_nominal'));

    let filtered: Votacao[] = votacoes;

    if (siglaOrgao) {
      filtered = filtered.filter((votacao) => votacao.sigla_orgao === siglaOrgao);
    }

    if (ehNominal !== undefined) {
      filtered = filtered.filter((votacao) => Boolean(votacao.eh_nominal) === ehNominal);
    }

    return HttpResponse.json(createPaginatedResponse(filtered, page, perPage));
  }),

  /**
   * GET /api/v1/votacoes/:id/proposicoes
   * Get proposições vinculadas a uma votação
   */
  http.get('*/api/v1/votacoes/:id/proposicoes', ({ request, params }) => {
    const votacaoId = parseStrictId(params.id as string | undefined);

    if (!votacaoId) {
      return validationError('ID de votação inválido');
    }

    const votacao = getVotacaoById(votacoes, votacaoId);
    if (!votacao) {
      return notFoundError('Votação não encontrada');
    }

    const url = new URL(request.url);
    const { page, perPage } = getPaginationParams(url);
    const proposicoes = getProposicoesByVotacaoId(votacao.id);

    return HttpResponse.json(createPaginatedResponse(proposicoes, page, perPage));
  }),

  /**
   * GET /api/v1/votacoes/:id
   * Get a single votação by ID with its nested proposicao
   * Returns 404 if votação not found
   */
  http.get('*/api/v1/votacoes/:id', ({ params }) => {
    const votacaoId = parseStrictId(params.id as string | undefined);

    if (!votacaoId) {
      return validationError('ID de votação inválido');
    }

    const votacao = getVotacaoById(votacoes, votacaoId);

    if (!votacao) {
      return notFoundError('Votação não encontrada');
    }

    const response: SingleResponse<Votacao> = { data: votacao };
    return HttpResponse.json(response);
  }),
];
