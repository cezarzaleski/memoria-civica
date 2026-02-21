import type { Proposicao } from './proposicao';

export const ResultadoVotacao = {
  APROVADO: 'Aprovado',
  REJEITADO: 'Rejeitado',
  APROVADO_COM_SUBSTITUTIVO: 'Aprovado com substitutivo',
} as const;

export type ResultadoVotacao = (typeof ResultadoVotacao)[keyof typeof ResultadoVotacao] | (string & {});

/**
 * Placar agregado conforme estrutura canônica do ETL.
 */
export interface Placar {
  votos_sim: number;
  votos_nao: number;
  votos_outros: number;
}

/**
 * Representa uma votação legislativa conforme contrato canônico do ETL.
 */
export interface Votacao {
  id: number;
  proposicao_id?: number;
  data_hora: string;
  resultado: ResultadoVotacao;
  placar: Placar;
  eh_nominal?: boolean;
  descricao?: string;
  sigla_orgao?: string;
  proposicao?: Proposicao;
}
