import { http, HttpResponse } from 'msw';
import type { Deputado } from '@/lib/types';
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
  http.get('http://localhost/api/v1/deputados', ({ request }) => {
    const url = new URL(request.url);
    const nome = url.searchParams.get('nome');
    const partido = url.searchParams.get('partido');
    const uf = url.searchParams.get('uf');

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

    return HttpResponse.json(filtered);
  }),

  /**
   * GET /api/v1/deputados/:id
   * Get a single deputado by ID
   * Returns 404 if deputy not found
   */
  http.get('http://localhost/api/v1/deputados/:id', ({ params }) => {
    const deputado = getDeputadoById(deputados, parseInt(params.id as string));

    if (!deputado) {
      return new HttpResponse(null, { status: 404 });
    }

    return HttpResponse.json(deputado);
  }),
];
