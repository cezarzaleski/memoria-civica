import { http, HttpResponse } from 'msw';
import type { Deputado, SingleResponse } from '@/lib/types';
import {
  generateDeputados,
  getDeputadoById,
  filterDeputadosByNome,
  filterDeputadosByPartido,
  filterDeputadosByUF,
} from '../data/deputados';
import { createPaginatedResponse, getPaginationParams, notFoundError, parseStrictId, validationError } from './utils';

/**
 * Generate the complete list of mock deputados once
 */
const deputados = generateDeputados(513);

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
    const { page, perPage } = getPaginationParams(url);

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

    return HttpResponse.json(createPaginatedResponse(filtered, page, perPage));
  }),

  /**
   * GET /api/v1/deputados/:id
   * Get a single deputado by ID
   * Returns 404 if deputy not found
   */
  http.get('*/api/v1/deputados/:id', ({ params }) => {
    const deputadoId = parseStrictId(params.id as string | undefined);

    if (!deputadoId) {
      return validationError('ID de deputado inválido');
    }

    const deputado = getDeputadoById(deputados, deputadoId);

    if (!deputado) {
      return notFoundError('Deputado não encontrado');
    }

    const response: SingleResponse<Deputado> = { data: deputado };
    return HttpResponse.json(response);
  }),
];
