import type { Deputado } from './deputado';

/**
 * Tipo de voto em uma proposição
 */
export enum TipoVoto {
  SIM = 'SIM',
  NAO = 'NAO',
  ABSTENCAO = 'ABSTENCAO',
  OBSTRUCAO = 'OBSTRUCAO',
}

/**
 * Representação de um voto individual de um deputado
 */
export interface Voto {
  id: string;
  votacao_id: string;
  deputado_id: number;
  deputado?: Deputado;
  tipo: TipoVoto;
}
