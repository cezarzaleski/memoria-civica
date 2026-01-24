/**
 * Tipo de proposição legislativa
 */
export enum TipoProposicao {
  PL = 'PL', // Projeto de Lei
  PEC = 'PEC', // Proposta de Emenda Constitucional
  MP = 'MP', // Medida Provisória
  PLP = 'PLP', // Projeto de Lei Complementar
  PDC = 'PDC', // Projeto de Decreto Legislativo
}

/**
 * Representação de uma proposição legislativa
 */
export interface Proposicao {
  id: number;
  tipo: TipoProposicao;
  numero: number;
  ano: number;
  ementa: string;
  ementa_simplificada?: string;
  autor_id?: number;
}
