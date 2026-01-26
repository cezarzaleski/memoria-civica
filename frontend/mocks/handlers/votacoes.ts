import { http, HttpResponse } from 'msw';
import { generateVotacoes, getVotacaoById } from '../data/votacoes';

/**
 * Generate the complete list of mock votações once
 * Already sorted by data descending (most recent first)
 */
const votacoes = generateVotacoes(50);

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
  http.get('http://localhost/api/v1/votacoes', () => {
    return HttpResponse.json(votacoes);
  }),

  /**
   * GET /api/v1/votacoes/:id
   * Get a single votação by ID with its nested proposicao
   * Returns 404 if votação not found
   */
  http.get('http://localhost/api/v1/votacoes/:id', ({ params }) => {
    const votacao = getVotacaoById(votacoes, params.id as string);

    if (!votacao) {
      return new HttpResponse(null, { status: 404 });
    }

    return HttpResponse.json(votacao);
  }),
];
