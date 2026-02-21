/**
 * Representa um deputado federal conforme contrato canônico do ETL.
 */
export interface Deputado {
  id: number;
  nome: string;
  sigla_partido: string;
  uf: string;
  foto_url: string;
  email: string;
}
