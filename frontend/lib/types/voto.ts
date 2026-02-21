import type { Deputado } from './deputado';

export const TipoVoto = {
  SIM: 'Sim',
  NAO: 'Não',
  ABSTENCAO: 'Abstenção',
  OBSTRUCAO: 'Obstrução',
  ART_17: 'Art. 17',
} as const;

export type TipoVoto = (typeof TipoVoto)[keyof typeof TipoVoto] | (string & {});

/**
 * Representa um voto individual de um deputado.
 */
export interface Voto {
  id: number;
  votacao_id: number;
  deputado_id: number;
  deputado?: Deputado;
  voto: TipoVoto;
}
