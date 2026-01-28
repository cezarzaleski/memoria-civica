/**
 * MSW request handlers for mock API endpoints
 * Consolidated handlers for all REST API endpoints
 */

import { deputadosHandlers } from './deputados';
import { votacoesHandlers } from './votacoes';
import { votosHandlers } from './votos';

/**
 * Complete set of MSW handlers for the mock API
 * Includes:
 * - Deputados endpoints (GET /api/v1/deputados, /api/v1/deputados/:id)
 * - Votações endpoints (GET /api/v1/votacoes, /api/v1/votacoes/:id)
 * - Votos endpoints (GET /api/v1/votacoes/:id/votos)
 */
export const handlers = [
  ...deputadosHandlers,
  ...votacoesHandlers,
  ...votosHandlers,
];
