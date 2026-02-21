import { http, HttpResponse } from 'msw';
import type { PaginatedResponse, Voto } from '@/lib/types';
import { generateVotos } from '../data/votos';

/**
 * Cache for generated votos per votação
 * This ensures consistent data for the same votação across multiple requests
 */
const votosCache = new Map<number, ReturnType<typeof generateVotos>>();
const DEFAULT_PAGE = 1;
const DEFAULT_PER_PAGE = 20;

function parsePositiveInteger(value: string | null, fallback: number): number {
  const parsedValue = Number.parseInt(value ?? '', 10);
  return Number.isInteger(parsedValue) && parsedValue > 0 ? parsedValue : fallback;
}

function parseStrictId(value: string | undefined): number | null {
  if (!value || !/^\d+$/.test(value)) {
    return null;
  }

  const parsedValue = Number(value);
  return Number.isSafeInteger(parsedValue) && parsedValue > 0 ? parsedValue : null;
}

function paginate<T>(items: T[], page: number, perPage: number): PaginatedResponse<T> {
  const startIndex = (page - 1) * perPage;
  return {
    data: items.slice(startIndex, startIndex + perPage),
    pagination: {
      page,
      per_page: perPage,
      total: items.length,
    },
  };
}

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
  http.get('*/api/v1/votacoes/:votacao_id/votos', ({ request, params }) => {
    const url = new URL(request.url);
    const votacao_id = parseStrictId(params.votacao_id as string | undefined);
    const page = parsePositiveInteger(url.searchParams.get('page'), DEFAULT_PAGE);
    const perPage = parsePositiveInteger(url.searchParams.get('per_page'), DEFAULT_PER_PAGE);

    if (!votacao_id) {
      return HttpResponse.json(
        {
          error: {
            code: 'VALIDATION_ERROR',
            message: 'ID de votação inválido',
          },
        },
        { status: 400 }
      );
    }

    // Check if we've already generated votos for this votação
    if (!votosCache.has(votacao_id)) {
      votosCache.set(votacao_id, generateVotos(votacao_id));
    }

    const votos = votosCache.get(votacao_id);
    if (!votos) {
      return HttpResponse.json(
        {
          error: {
            code: 'NOT_FOUND',
            message: 'Votos não encontrados para a votação',
          },
        },
        { status: 404 }
      );
    }

    const orderedVotes: Voto[] = votos;
    return HttpResponse.json(paginate(orderedVotes, page, perPage));
  }),
];
