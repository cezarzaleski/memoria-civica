import { http, HttpResponse } from 'msw';
import type { Proposicao, ProposicaoCategoria, SingleResponse } from '@/lib/types';
import { generateProposicoes, getProposicaoById } from '../data/proposicoes';
import { getCategoriasByProposicaoId } from '../data/proposicoes-categorias';
import { createPaginatedResponse, getPaginationParams, notFoundError, parseStrictId, validationError } from './utils';

const proposicoes = generateProposicoes(80);

export const proposicoesHandlers = [
  /**
   * GET /api/v1/proposicoes
   * Lista proposições com filtros opcionais
   */
  http.get('*/api/v1/proposicoes', ({ request }) => {
    const url = new URL(request.url);
    const { page, perPage } = getPaginationParams(url);
    const tipo = url.searchParams.get('tipo');
    const anoParam = url.searchParams.get('ano');

    const ano = anoParam === null ? null : parseStrictId(anoParam);
    if (anoParam !== null && ano === null) {
      return validationError('Parâmetro de ano inválido');
    }

    let filtered: Proposicao[] = proposicoes;

    if (tipo) {
      filtered = filtered.filter((proposicao) => proposicao.tipo === tipo);
    }

    if (ano !== null) {
      filtered = filtered.filter((proposicao) => proposicao.ano === ano);
    }

    return HttpResponse.json(createPaginatedResponse(filtered, page, perPage));
  }),

  /**
   * GET /api/v1/proposicoes/:id
   * Detalha uma proposição por ID
   */
  http.get('*/api/v1/proposicoes/:id', ({ params }) => {
    const proposicaoId = parseStrictId(params.id as string | undefined);

    if (!proposicaoId) {
      return validationError('ID de proposição inválido');
    }

    const proposicao = getProposicaoById(proposicoes, proposicaoId);
    if (!proposicao) {
      return notFoundError('Proposição não encontrada');
    }

    const response: SingleResponse<Proposicao> = { data: proposicao };
    return HttpResponse.json(response);
  }),

  /**
   * GET /api/v1/proposicoes/:id/categorias
   * Lista as categorias cívicas relacionadas a uma proposição
   */
  http.get('*/api/v1/proposicoes/:id/categorias', ({ request, params }) => {
    const proposicaoId = parseStrictId(params.id as string | undefined);

    if (!proposicaoId) {
      return validationError('ID de proposição inválido');
    }

    const proposicao = getProposicaoById(proposicoes, proposicaoId);
    if (!proposicao) {
      return notFoundError('Proposição não encontrada');
    }

    const url = new URL(request.url);
    const { page, perPage } = getPaginationParams(url);
    const categorias: ProposicaoCategoria[] = getCategoriasByProposicaoId(proposicao.id);

    return HttpResponse.json(createPaginatedResponse(categorias, page, perPage));
  }),
];
