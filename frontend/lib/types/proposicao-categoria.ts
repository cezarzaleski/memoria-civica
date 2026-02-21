import type { CategoriaCivica } from './categoria-civica';

export type OrigemClassificacao = 'manual' | 'automatica' | (string & {});

export interface ProposicaoCategoria {
  id: number;
  proposicao_id: number;
  categoria_id: number;
  origem: OrigemClassificacao;
  confianca?: number;
  created_at: string;
  categoria?: CategoriaCivica;
}
