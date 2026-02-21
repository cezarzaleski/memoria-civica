/**
 * MSW request handlers for mock API endpoints
 * Consolidated handlers for all REST API endpoints
 */

import { deputadosHandlers } from './deputados';
import { proposicoesHandlers } from './proposicoes';
import { votacoesHandlers } from './votacoes';
import { orientacoesHandlers } from './orientacoes';
import { votosHandlers } from './votos';
import { categoriasCivicasHandlers } from './categorias-civicas';

/**
 * Complete set of MSW handlers for the mock API
 * Includes:
 * - Deputados endpoints (GET /api/v1/deputados, /api/v1/deputados/:id)
 * - Proposições endpoints (GET /api/v1/proposicoes, /api/v1/proposicoes/:id, /api/v1/proposicoes/:id/categorias)
 * - Votações endpoints (GET /api/v1/votacoes, /api/v1/votacoes/:id)
 * - Orientações endpoint (GET /api/v1/votacoes/:id/orientacoes)
 * - Votos endpoints (GET /api/v1/votacoes/:id/votos)
 * - Categorias cívicas endpoint (GET /api/v1/categorias-civicas)
 */
export const handlers = [
  ...deputadosHandlers,
  ...proposicoesHandlers,
  ...votacoesHandlers,
  ...orientacoesHandlers,
  ...votosHandlers,
  ...categoriasCivicasHandlers,
];
