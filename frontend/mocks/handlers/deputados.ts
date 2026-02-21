import { http, HttpResponse } from 'msw';
import type { Deputado, PaginatedResponse, SingleResponse } from '@/lib/types';
import {
  generateDeputados,
  getDeputadoById,
  filterDeputadosByNome,
  filterDeputadosByPartido,
  filterDeputadosByUF,
} from '../data/deputados';

/**
 * Generate the complete list of mock deputados once
 */
const deputados = generateDeputados(513);
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
 * MSW handlers for deputados endpoints
 *
 * Endpoints:
 * - GET /api/v1/deputados - List all deputies with optional filtering
 *   Query parameters:
 *     - nome: Filter by name (case-insensitive substring match)
 *     - partido: Filter by party exact match
 *     - uf: Filter by state exact match
 *
 * - GET /api/v1/deputados/:id - Get a single deputy by ID
 */
export const deputadosHandlers = [
  /**
   * GET /api/v1/deputados
   * List all deputados with optional filtering by query parameters
   */
  http.get('*/api/v1/deputados', ({ request }) => {
    const url = new URL(request.url);
    const nome = url.searchParams.get('nome');
    const partido = url.searchParams.get('partido');
    const uf = url.searchParams.get('uf');
    const page = parsePositiveInteger(url.searchParams.get('page'), DEFAULT_PAGE);
    const perPage = parsePositiveInteger(url.searchParams.get('per_page'), DEFAULT_PER_PAGE);

    let filtered: Deputado[] = deputados;

    // Apply filters in sequence
    if (nome) {
      filtered = filterDeputadosByNome(filtered, nome);
    }

    if (partido) {
      filtered = filterDeputadosByPartido(filtered, partido);
    }

    if (uf) {
      filtered = filterDeputadosByUF(filtered, uf);
    }

    return HttpResponse.json(paginate(filtered, page, perPage));
  }),

  /**
   * GET /api/v1/deputados/:id
   * Get a single deputado by ID
   * Returns 404 if deputy not found
   */
  http.get('*/api/v1/deputados/:id', ({ params }) => {
    const deputadoId = parseStrictId(params.id as string | undefined);

    if (!deputadoId) {
      return HttpResponse.json(
        {
          error: {
            code: 'VALIDATION_ERROR',
            message: 'ID de deputado inválido',
          },
        },
        { status: 400 }
      );
    }

    const deputado = getDeputadoById(deputados, deputadoId);

    if (!deputado) {
      return HttpResponse.json(
        {
          error: {
            code: 'NOT_FOUND',
            message: 'Deputado não encontrado',
          },
        },
        { status: 404 }
      );
    }

    const response: SingleResponse<Deputado> = { data: deputado };
    return HttpResponse.json(response);
  }),
];
