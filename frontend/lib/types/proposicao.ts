export const TipoProposicao = {
  PL: 'PL',
  PEC: 'PEC',
  MP: 'MP',
  PLP: 'PLP',
  PDC: 'PDC',
  REQ: 'REQ',
  RIC: 'RIC',
  PFC: 'PFC',
} as const;

export type TipoProposicao = (typeof TipoProposicao)[keyof typeof TipoProposicao] | (string & {});

/**
 * Representa uma proposição legislativa conforme contrato canônico do ETL.
 */
export interface Proposicao {
  id: number;
  tipo: TipoProposicao;
  numero: number;
  ano: number;
  ementa: string;
  ementa_simplificada?: string;
  autor_id?: number;
  data_apresentacao: string;
}
