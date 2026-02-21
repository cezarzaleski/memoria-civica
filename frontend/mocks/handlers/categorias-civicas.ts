import { http, HttpResponse } from 'msw';
import { CATEGORIAS_CIVICAS_FIXTURES } from '../data/categorias-civicas';
import { createPaginatedResponse, getPaginationParams } from './utils';

export const categoriasCivicasHandlers = [
  /**
   * GET /api/v1/categorias-civicas
   * Lista categorias cívicas paginadas
   */
  http.get('*/api/v1/categorias-civicas', ({ request }) => {
    const url = new URL(request.url);
    const { page, perPage } = getPaginationParams(url);

    return HttpResponse.json(createPaginatedResponse(CATEGORIAS_CIVICAS_FIXTURES, page, perPage));
  }),
];
