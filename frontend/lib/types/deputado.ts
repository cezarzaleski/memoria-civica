/**
 * Representação de um deputado federal
 */
export interface Deputado {
  id: number;
  nome: string;
  partido: string;
  uf: string;
  foto_url?: string;
  email?: string;
}
