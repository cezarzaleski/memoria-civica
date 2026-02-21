import type { Proposicao } from './proposicao';

export interface VotacaoProposicao {
  id: number;
  votacao_id: number;
  proposicao_id: number;
  titulo?: string;
  ementa?: string;
  sigla_tipo?: string;
  numero?: number;
  ano?: number;
  eh_principal: boolean;
  created_at: string;
  proposicao?: Proposicao;
}
