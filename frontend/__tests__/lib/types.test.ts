import { describe, expect, expectTypeOf, it } from 'vitest';
import type {
  CategoriaCivica,
  Deputado,
  Orientacao,
  OrigemClassificacao,
  PaginatedResponse,
  PaginationMeta,
  Placar,
  Proposicao,
  ProposicaoCategoria,
  ResultadoVotacao,
  SingleResponse,
  TipoProposicao,
  TipoVoto,
  Votacao,
  VotacaoProposicao,
  Voto,
} from '@/lib/types';
import type { Deputado as DeputadoFromModule } from '@/lib/types/deputado';
import type { PaginatedResponse as PaginatedResponseFromModule } from '@/lib/types/pagination';
import type { Proposicao as ProposicaoFromModule } from '@/lib/types/proposicao';
import type { Votacao as VotacaoFromModule } from '@/lib/types/votacao';
import type { Voto as VotoFromModule } from '@/lib/types/voto';

describe('Contratos TypeScript alinhados com ETL', () => {
  describe('Deputado', () => {
    it('deve seguir o contrato canônico com campos obrigatórios', () => {
      const deputado: Deputado = {
        id: 10,
        nome: 'Ana Martins',
        sigla_partido: 'PSB',
        uf: 'PE',
        foto_url: 'https://example.com/ana-martins.jpg',
        email: 'ana.martins@camara.leg.br',
      };

      expect(deputado.sigla_partido).toBe('PSB');
      expect(deputado.foto_url).toContain('https://');
      expect(deputado.email).toContain('@');
      expectTypeOf<Deputado['id']>().toEqualTypeOf<number>();
    });
  });

  describe('Proposicao', () => {
    it('deve aceitar tipos previstos e fallback string', () => {
      const tipos: TipoProposicao[] = ['PL', 'PEC', 'MP', 'PLP', 'PDC', 'REQ', 'RIC', 'PFC', 'OUTRO'];

      expect(tipos).toContain('REQ');
      expect(tipos).toContain('OUTRO');
    });

    it('deve incluir data_apresentacao e nullability correta', () => {
      const proposicao: Proposicao = {
        id: 101,
        tipo: 'PL',
        numero: 1234,
        ano: 2025,
        ementa: 'Altera regras de transparência pública',
        ementa_simplificada: 'Transparência pública',
        autor_id: 42,
        data_apresentacao: '2025-04-01T12:30:00Z',
      };

      expect(proposicao.data_apresentacao).toBe('2025-04-01T12:30:00Z');
      expectTypeOf<Proposicao['autor_id']>().toEqualTypeOf<number | undefined>();
    });
  });

  describe('Votacao e Placar', () => {
    it('deve usar estrutura de placar canônica com 3 campos', () => {
      const placar: Placar = {
        votos_sim: 280,
        votos_nao: 180,
        votos_outros: 53,
      };

      expect(placar.votos_sim + placar.votos_nao + placar.votos_outros).toBe(513);
      expectTypeOf<Placar['votos_sim']>().toEqualTypeOf<number>();
    });

    it('deve seguir contrato de votação com campos novos e opcionais', () => {
      const votacao: Votacao = {
        id: 9001,
        proposicao_id: 101,
        data_hora: '2025-06-10T19:00:00Z',
        resultado: 'Aprovado',
        placar: {
          votos_sim: 300,
          votos_nao: 140,
          votos_outros: 73,
        },
        eh_nominal: true,
        descricao: 'Votação em turno único',
        sigla_orgao: 'PLEN',
      };

      expect(votacao.id).toBe(9001);
      expect(votacao.data_hora).toContain('T');
      expect(votacao.eh_nominal).toBe(true);
      expectTypeOf<Votacao['resultado']>().toEqualTypeOf<ResultadoVotacao>();
      expectTypeOf<Votacao['proposicao_id']>().toEqualTypeOf<number | undefined>();
    });

    it('deve aceitar valores de resultado previstos e fallback string', () => {
      const resultados: ResultadoVotacao[] = [
        'Aprovado',
        'Rejeitado',
        'Aprovado com substitutivo',
        'Aguardando apuração',
      ];

      expect(resultados).toContain('Aprovado com substitutivo');
      expect(resultados).toContain('Aguardando apuração');
    });
  });

  describe('Voto', () => {
    it('deve usar campo canônico voto e IDs numéricos', () => {
      const voto: Voto = {
        id: 70001,
        votacao_id: 9001,
        deputado_id: 10,
        voto: 'Sim',
      };

      expect(voto.voto).toBe('Sim');
      expect(voto.votacao_id).toBe(9001);
      expectTypeOf<Voto['id']>().toEqualTypeOf<number>();
      expectTypeOf<Voto['votacao_id']>().toEqualTypeOf<number>();
    });

    it('deve aceitar votos previstos e fallback string', () => {
      const tipos: TipoVoto[] = ['Sim', 'Não', 'Abstenção', 'Obstrução', 'Art. 17', 'Liberado'];

      expect(tipos).toContain('Art. 17');
      expect(tipos).toContain('Liberado');
    });
  });

  describe('Novas entidades de domínio', () => {
    it('deve validar CategoriaCivica e Orientacao', () => {
      const categoria: CategoriaCivica = {
        id: 1,
        codigo: 'saude',
        nome: 'Saúde',
        descricao: 'Políticas públicas de saúde',
        icone: 'heart-pulse',
      };

      const orientacao: Orientacao = {
        id: 2,
        votacao_id: 9001,
        sigla_bancada: 'GOV',
        orientacao: 'Sim',
        created_at: '2025-06-10T18:00:00Z',
      };

      expect(categoria.codigo).toBe('saude');
      expect(orientacao.sigla_bancada).toBe('GOV');
    });

    it('deve validar ProposicaoCategoria e VotacaoProposicao', () => {
      const origem: OrigemClassificacao = 'manual';

      const proposicaoCategoria: ProposicaoCategoria = {
        id: 3,
        proposicao_id: 101,
        categoria_id: 1,
        origem,
        confianca: 0.98,
        created_at: '2025-06-10T17:00:00Z',
      };

      const votacaoProposicao: VotacaoProposicao = {
        id: 4,
        votacao_id: 9001,
        proposicao_id: 101,
        titulo: 'PL 1234/2025',
        ementa: 'Transparência pública',
        sigla_tipo: 'PL',
        numero: 1234,
        ano: 2025,
        eh_principal: true,
        created_at: '2025-06-10T17:05:00Z',
      };

      expect(proposicaoCategoria.origem).toBe('manual');
      expect(votacaoProposicao.eh_principal).toBe(true);
    });
  });

  describe('Paginação e resposta de recurso único', () => {
    it('deve validar envelope paginado', () => {
      const response: PaginatedResponse<Voto> = {
        data: [
          {
            id: 70001,
            votacao_id: 9001,
            deputado_id: 10,
            voto: 'Sim',
          },
        ],
        pagination: {
          page: 1,
          per_page: 20,
          total: 1,
        },
      };

      expect(response.data).toHaveLength(1);
      expect(response.pagination.total).toBe(1);
      expectTypeOf<PaginationMeta>().toEqualTypeOf<{
        page: number;
        per_page: number;
        total: number;
      }>();
    });

    it('deve validar envelope de recurso único', () => {
      const response: SingleResponse<Orientacao> = {
        data: {
          id: 2,
          votacao_id: 9001,
          sigla_bancada: 'GOV',
          orientacao: 'Sim',
          created_at: '2025-06-10T18:00:00Z',
        },
      };

      expect(response.data.id).toBe(2);
      expect(response.data.orientacao).toBe('Sim');
    });
  });

  describe('Remoção de expectativas legadas', () => {
    it('deve garantir campos canônicos e ausência de campos antigos', () => {
      type PlacarTemSim = 'sim' extends keyof Placar ? true : false;
      type VotacaoTemData = 'data' extends keyof Votacao ? true : false;
      type VotoTemTipo = 'tipo' extends keyof Voto ? true : false;
      type PlacarTemVotosSim = 'votos_sim' extends keyof Placar ? true : false;
      type VotacaoTemDataHora = 'data_hora' extends keyof Votacao ? true : false;
      type VotoTemVoto = 'voto' extends keyof Voto ? true : false;

      const placarTemSim: PlacarTemSim = false;
      const votacaoTemData: VotacaoTemData = false;
      const votoTemTipo: VotoTemTipo = false;
      const placarTemVotosSim: PlacarTemVotosSim = true;
      const votacaoTemDataHora: VotacaoTemDataHora = true;
      const votoTemVoto: VotoTemVoto = true;

      expect(placarTemSim).toBe(false);
      expect(votacaoTemData).toBe(false);
      expect(votoTemTipo).toBe(false);
      expect(placarTemVotosSim).toBe(true);
      expect(votacaoTemDataHora).toBe(true);
      expect(votoTemVoto).toBe(true);
    });
  });

  describe('Barrel exports', () => {
    it('deve manter os tipos acessíveis pelo barrel central', () => {
      expectTypeOf<Deputado>().toEqualTypeOf<DeputadoFromModule>();
      expectTypeOf<Proposicao>().toEqualTypeOf<ProposicaoFromModule>();
      expectTypeOf<Votacao>().toEqualTypeOf<VotacaoFromModule>();
      expectTypeOf<Voto>().toEqualTypeOf<VotoFromModule>();
      expectTypeOf<PaginatedResponse<Voto>>().toEqualTypeOf<PaginatedResponseFromModule<Voto>>();
      expect(true).toBe(true);
    });
  });
});
