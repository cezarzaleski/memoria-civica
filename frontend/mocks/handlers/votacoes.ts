import { http, HttpResponse } from 'msw';
import type { PaginatedResponse, SingleResponse, Votacao } from '@/lib/types';
import { generateVotacoes, getVotacaoById } from '../data/votacoes';

/**
 * Generate the complete list of mock votações once
 * Already sorted by data descending (most recent first)
 */
const votacoes = generateVotacoes(50);
const DEFAULT_PAGE = 1;
const DEFAULT_PER_PAGE = 20;

function parsePositiveInteger(value: string | null, fallback: number): number {
  const parsedValue = Number.parseInt(value ?? '', 10);
  return Number.isInteger(parsedValue) && parsedValue > 0 ? parsedValue : fallback;
}

function parseBoolean(value: string | null): boolean | undefined {
  if (value === 'true') return true;
  if (value === 'false') return false;
  return undefined;
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
    const page = parsePositiveInteger(url.searchParams.get('page'), DEFAULT_PAGE);
    const perPage = parsePositiveInteger(url.searchParams.get('per_page'), DEFAULT_PER_PAGE);
    const siglaOrgao = url.searchParams.get('sigla_orgao');
    const ehNominal = parseBoolean(url.searchParams.get('eh_nominal'));

    let filtered: Votacao[] = votacoes;

    if (siglaOrgao) {
      filtered = filtered.filter((votacao) => votacao.sigla_orgao === siglaOrgao);
    }

    if (ehNominal !== undefined) {
      filtered = filtered.filter((votacao) => Boolean(votacao.eh_nominal) === ehNominal);
    }

    return HttpResponse.json(paginate(filtered, page, perPage));
  }),

  /**
   * GET /api/v1/votacoes/:id
   * Get a single votação by ID with its nested proposicao
   * Returns 404 if votação not found
   */
  http.get('*/api/v1/votacoes/:id', ({ params }) => {
    const votacaoId = Number(params.id);

    if (!Number.isInteger(votacaoId)) {
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

    const votacao = getVotacaoById(votacoes, votacaoId);

    if (!votacao) {
      return HttpResponse.json(
        {
          error: {
            code: 'NOT_FOUND',
            message: 'Votação não encontrada',
          },
        },
        { status: 404 }
      );
    }

    const response: SingleResponse<Votacao> = { data: votacao };
    return HttpResponse.json(response);
  }),
];
