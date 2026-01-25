import { http, HttpResponse } from 'msw';
import { generateVotos } from '../data/votos';

/**
 * Cache for generated votos per votação
 * This ensures consistent data for the same votação across multiple requests
 */
const votosCache = new Map<string, ReturnType<typeof generateVotos>>();

/**
 * MSW handlers for votos endpoints
 *
 * Endpoints:
 * - GET /api/v1/votacoes/:id/votos - Get all votos (individual votes) for a specific votação
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
  http.get('/api/v1/votacoes/:votacao_id/votos', ({ params }) => {
    const votacao_id = params.votacao_id as string;

    // Check if we've already generated votos for this votação
    if (!votosCache.has(votacao_id)) {
      votosCache.set(votacao_id, generateVotos(votacao_id));
    }

    const votos = votosCache.get(votacao_id);
    if (!votos) {
      return new HttpResponse(null, { status: 404 });
    }

    return HttpResponse.json(votos);
  }),
];
