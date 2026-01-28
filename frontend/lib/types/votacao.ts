import type { Proposicao } from './proposicao';

/**
 * Resultado de uma votação
 */
export enum ResultadoVotacao {
  APROVADO = 'APROVADO',
  REJEITADO = 'REJEITADO',
}

/**
 * Placar de uma votação
 */
export interface Placar {
  sim: number;
  nao: number;
  abstencao: number;
  obstrucao: number;
}

/**
 * Representação de uma votação legislativa
 */
export interface Votacao {
  id: string;
  proposicao_id: number;
  proposicao?: Proposicao;
  data: string;
  resultado: ResultadoVotacao;
  placar: Placar;
}
