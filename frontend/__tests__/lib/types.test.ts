import { describe, it, expect } from 'vitest';
import {
  Deputado,
  TipoProposicao,
  Proposicao,
  ResultadoVotacao,
  Votacao,
  Placar,
  TipoVoto,
  Voto,
} from '@/lib/types';

describe('TypeScript Types and Enums', () => {
  describe('TipoProposicao Enum', () => {
    it('should have all expected values', () => {
      expect(TipoProposicao.PL).toBe('PL');
      expect(TipoProposicao.PEC).toBe('PEC');
      expect(TipoProposicao.MP).toBe('MP');
      expect(TipoProposicao.PLP).toBe('PLP');
      expect(TipoProposicao.PDC).toBe('PDC');
    });

    it('should have exactly 5 enum values', () => {
      const values = Object.values(TipoProposicao);
      expect(values).toHaveLength(5);
    });

    it('should match expected string literals', () => {
      const expectedValues = ['PL', 'PEC', 'MP', 'PLP', 'PDC'];
      const actualValues = Object.values(TipoProposicao);
      expect(actualValues).toEqual(expect.arrayContaining(expectedValues));
    });
  });

  describe('ResultadoVotacao Enum', () => {
    it('should have all expected values', () => {
      expect(ResultadoVotacao.APROVADO).toBe('APROVADO');
      expect(ResultadoVotacao.REJEITADO).toBe('REJEITADO');
    });

    it('should have exactly 2 enum values', () => {
      const values = Object.values(ResultadoVotacao);
      expect(values).toHaveLength(2);
    });

    it('should match expected string literals', () => {
      const expectedValues = ['APROVADO', 'REJEITADO'];
      const actualValues = Object.values(ResultadoVotacao);
      expect(actualValues).toEqual(expect.arrayContaining(expectedValues));
    });
  });

  describe('TipoVoto Enum', () => {
    it('should have all expected values', () => {
      expect(TipoVoto.SIM).toBe('SIM');
      expect(TipoVoto.NAO).toBe('NAO');
      expect(TipoVoto.ABSTENCAO).toBe('ABSTENCAO');
      expect(TipoVoto.OBSTRUCAO).toBe('OBSTRUCAO');
    });

    it('should have exactly 4 enum values', () => {
      const values = Object.values(TipoVoto);
      expect(values).toHaveLength(4);
    });

    it('should match expected string literals', () => {
      const expectedValues = ['SIM', 'NAO', 'ABSTENCAO', 'OBSTRUCAO'];
      const actualValues = Object.values(TipoVoto);
      expect(actualValues).toEqual(expect.arrayContaining(expectedValues));
    });
  });

  describe('Deputado Interface', () => {
    it('should create a valid Deputado with required fields only', () => {
      const deputado: Deputado = {
        id: 1,
        nome: 'João da Silva',
        partido: 'PT',
        uf: 'SP',
      };

      expect(deputado.id).toBe(1);
      expect(deputado.nome).toBe('João da Silva');
      expect(deputado.partido).toBe('PT');
      expect(deputado.uf).toBe('SP');
      expect(deputado.foto_url).toBeUndefined();
      expect(deputado.email).toBeUndefined();
    });

    it('should create a valid Deputado with optional fields', () => {
      const deputado: Deputado = {
        id: 2,
        nome: 'Maria Santos',
        partido: 'PSDB',
        uf: 'RJ',
        foto_url: 'https://example.com/photo.jpg',
        email: 'maria@example.com',
      };

      expect(deputado.foto_url).toBe('https://example.com/photo.jpg');
      expect(deputado.email).toBe('maria@example.com');
    });

    it('should have optional fields correctly typed', () => {
      const deputado: Deputado = {
        id: 3,
        nome: 'Pedro Costa',
        partido: 'PL',
        uf: 'MG',
      };

      // These should not throw type errors
      const url: string | undefined = deputado.foto_url;
      const email: string | undefined = deputado.email;

      expect(url).toBeUndefined();
      expect(email).toBeUndefined();
    });
  });

  describe('Proposicao Interface', () => {
    it('should create a valid Proposicao with required fields only', () => {
      const proposicao: Proposicao = {
        id: 1,
        tipo: TipoProposicao.PL,
        numero: 1234,
        ano: 2024,
        ementa: 'Dispõe sobre a reforma tributária',
      };

      expect(proposicao.id).toBe(1);
      expect(proposicao.tipo).toBe(TipoProposicao.PL);
      expect(proposicao.numero).toBe(1234);
      expect(proposicao.ano).toBe(2024);
      expect(proposicao.ementa).toBe('Dispõe sobre a reforma tributária');
      expect(proposicao.ementa_simplificada).toBeUndefined();
      expect(proposicao.autor_id).toBeUndefined();
    });

    it('should create a valid Proposicao with optional fields', () => {
      const proposicao: Proposicao = {
        id: 2,
        tipo: TipoProposicao.PEC,
        numero: 123,
        ano: 2023,
        ementa: 'Emenda constitucional',
        ementa_simplificada: 'Reforma constitucional',
        autor_id: 5,
      };

      expect(proposicao.ementa_simplificada).toBe('Reforma constitucional');
      expect(proposicao.autor_id).toBe(5);
    });

    it('should accept all TipoProposicao enum values', () => {
      const tipos = [
        TipoProposicao.PL,
        TipoProposicao.PEC,
        TipoProposicao.MP,
        TipoProposicao.PLP,
        TipoProposicao.PDC,
      ];

      tipos.forEach((tipo) => {
        const proposicao: Proposicao = {
          id: 1,
          tipo,
          numero: 1,
          ano: 2024,
          ementa: 'Test',
        };
        expect(proposicao.tipo).toBe(tipo);
      });
    });
  });

  describe('Placar Interface', () => {
    it('should create a valid Placar with all fields', () => {
      const placar: Placar = {
        sim: 300,
        nao: 150,
        abstencao: 50,
        obstrucao: 13,
      };

      expect(placar.sim).toBe(300);
      expect(placar.nao).toBe(150);
      expect(placar.abstencao).toBe(50);
      expect(placar.obstrucao).toBe(13);
    });

    it('should validate placar with sum equal to total', () => {
      const placar: Placar = {
        sim: 300,
        nao: 150,
        abstencao: 50,
        obstrucao: 13,
      };

      const total = placar.sim + placar.nao + placar.abstencao + placar.obstrucao;
      expect(total).toBe(513); // Total typical size of Brazilian Chamber
    });

    it('should accept zero values in placar', () => {
      const placar: Placar = {
        sim: 513,
        nao: 0,
        abstencao: 0,
        obstrucao: 0,
      };

      expect(placar.sim).toBe(513);
      expect(placar.nao).toBe(0);
      expect(placar.abstencao).toBe(0);
      expect(placar.obstrucao).toBe(0);
    });
  });

  describe('Votacao Interface', () => {
    it('should create a valid Votacao with required fields only', () => {
      const votacao: Votacao = {
        id: 'votacao-1',
        proposicao_id: 1,
        data: '2024-01-24T10:30:00Z',
        resultado: ResultadoVotacao.APROVADO,
        placar: {
          sim: 300,
          nao: 150,
          abstencao: 50,
          obstrucao: 13,
        },
      };

      expect(votacao.id).toBe('votacao-1');
      expect(votacao.proposicao_id).toBe(1);
      expect(votacao.data).toBe('2024-01-24T10:30:00Z');
      expect(votacao.resultado).toBe(ResultadoVotacao.APROVADO);
      expect(votacao.proposicao).toBeUndefined();
    });

    it('should create a valid Votacao with nested Proposicao', () => {
      const votacao: Votacao = {
        id: 'votacao-2',
        proposicao_id: 1,
        proposicao: {
          id: 1,
          tipo: TipoProposicao.PL,
          numero: 1234,
          ano: 2024,
          ementa: 'Test Law',
        },
        data: '2024-01-24T10:30:00Z',
        resultado: ResultadoVotacao.REJEITADO,
        placar: {
          sim: 150,
          nao: 300,
          abstencao: 50,
          obstrucao: 13,
        },
      };

      expect(votacao.proposicao).toBeDefined();
      expect(votacao.proposicao?.tipo).toBe(TipoProposicao.PL);
      expect(votacao.proposicao?.numero).toBe(1234);
    });

    it('should accept ISO 8601 date strings', () => {
      const validDates = [
        '2024-01-24T10:30:00Z',
        '2024-01-24T10:30:00+00:00',
        '2024-01-24T10:30:00-03:00',
      ];

      validDates.forEach((date) => {
        const votacao: Votacao = {
          id: 'test',
          proposicao_id: 1,
          data: date,
          resultado: ResultadoVotacao.APROVADO,
          placar: { sim: 1, nao: 1, abstencao: 1, obstrucao: 1 },
        };
        expect(votacao.data).toBe(date);
      });
    });

    it('should accept both ResultadoVotacao values', () => {
      const votacao1: Votacao = {
        id: 'test-1',
        proposicao_id: 1,
        data: '2024-01-24T10:30:00Z',
        resultado: ResultadoVotacao.APROVADO,
        placar: { sim: 1, nao: 1, abstencao: 1, obstrucao: 1 },
      };

      const votacao2: Votacao = {
        id: 'test-2',
        proposicao_id: 1,
        data: '2024-01-24T10:30:00Z',
        resultado: ResultadoVotacao.REJEITADO,
        placar: { sim: 1, nao: 1, abstencao: 1, obstrucao: 1 },
      };

      expect(votacao1.resultado).toBe(ResultadoVotacao.APROVADO);
      expect(votacao2.resultado).toBe(ResultadoVotacao.REJEITADO);
    });
  });

  describe('Voto Interface', () => {
    it('should create a valid Voto with required fields only', () => {
      const voto: Voto = {
        id: 'voto-1',
        votacao_id: 'votacao-1',
        deputado_id: 1,
        tipo: TipoVoto.SIM,
      };

      expect(voto.id).toBe('voto-1');
      expect(voto.votacao_id).toBe('votacao-1');
      expect(voto.deputado_id).toBe(1);
      expect(voto.tipo).toBe(TipoVoto.SIM);
      expect(voto.deputado).toBeUndefined();
    });

    it('should create a valid Voto with nested Deputado', () => {
      const voto: Voto = {
        id: 'voto-2',
        votacao_id: 'votacao-1',
        deputado_id: 1,
        deputado: {
          id: 1,
          nome: 'João Silva',
          partido: 'PT',
          uf: 'SP',
        },
        tipo: TipoVoto.NAO,
      };

      expect(voto.deputado).toBeDefined();
      expect(voto.deputado?.nome).toBe('João Silva');
      expect(voto.deputado?.partido).toBe('PT');
    });

    it('should accept all TipoVoto enum values', () => {
      const tipos = [TipoVoto.SIM, TipoVoto.NAO, TipoVoto.ABSTENCAO, TipoVoto.OBSTRUCAO];

      tipos.forEach((tipo) => {
        const voto: Voto = {
          id: 'voto-1',
          votacao_id: 'votacao-1',
          deputado_id: 1,
          tipo,
        };
        expect(voto.tipo).toBe(tipo);
      });
    });

    it('should have optional Deputado field correctly typed', () => {
      const voto: Voto = {
        id: 'voto-3',
        votacao_id: 'votacao-1',
        deputado_id: 1,
        tipo: TipoVoto.ABSTENCAO,
      };

      // This should not throw a type error
      const deputado: Deputado | undefined = voto.deputado;
      expect(deputado).toBeUndefined();
    });
  });

  describe('Type Compatibility', () => {
    it('should handle nested objects in Votacao and Voto together', () => {
      const proposicao: Proposicao = {
        id: 1,
        tipo: TipoProposicao.PL,
        numero: 1234,
        ano: 2024,
        ementa: 'Test Law',
      };

      const deputado: Deputado = {
        id: 1,
        nome: 'Test Deputy',
        partido: 'PT',
        uf: 'SP',
      };

      const votacao: Votacao = {
        id: 'votacao-1',
        proposicao_id: 1,
        proposicao,
        data: '2024-01-24T10:30:00Z',
        resultado: ResultadoVotacao.APROVADO,
        placar: {
          sim: 300,
          nao: 150,
          abstencao: 50,
          obstrucao: 13,
        },
      };

      const voto: Voto = {
        id: 'voto-1',
        votacao_id: 'votacao-1',
        deputado_id: 1,
        deputado,
        tipo: TipoVoto.SIM,
      };

      expect(votacao.proposicao?.tipo).toBe(proposicao.tipo);
      expect(voto.deputado?.nome).toBe(deputado.nome);
    });

    it('should allow JSON serialization of all types', () => {
      const deputado: Deputado = {
        id: 1,
        nome: 'Test',
        partido: 'PT',
        uf: 'SP',
      };

      const proposicao: Proposicao = {
        id: 1,
        tipo: TipoProposicao.PL,
        numero: 1234,
        ano: 2024,
        ementa: 'Test',
      };

      const votacao: Votacao = {
        id: 'votacao-1',
        proposicao_id: 1,
        proposicao,
        data: '2024-01-24T10:30:00Z',
        resultado: ResultadoVotacao.APROVADO,
        placar: { sim: 300, nao: 150, abstencao: 50, obstrucao: 13 },
      };

      const voto: Voto = {
        id: 'voto-1',
        votacao_id: 'votacao-1',
        deputado_id: 1,
        deputado,
        tipo: TipoVoto.SIM,
      };

      // Should be serializable without errors
      const deputadoJson = JSON.stringify(deputado);
      const proposicaoJson = JSON.stringify(proposicao);
      const votacaoJson = JSON.stringify(votacao);
      const votoJson = JSON.stringify(voto);

      expect(deputadoJson).toBeDefined();
      expect(proposicaoJson).toBeDefined();
      expect(votacaoJson).toBeDefined();
      expect(votoJson).toBeDefined();
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty optional fields in Deputado', () => {
      const deputado: Deputado = {
        id: 1,
        nome: 'Test',
        partido: 'PT',
        uf: 'SP',
        foto_url: undefined,
        email: undefined,
      };

      expect(deputado.foto_url).toBeUndefined();
      expect(deputado.email).toBeUndefined();
    });

    it('should handle empty string in ementa field', () => {
      const proposicao: Proposicao = {
        id: 1,
        tipo: TipoProposicao.PL,
        numero: 1,
        ano: 2024,
        ementa: '',
      };

      expect(proposicao.ementa).toBe('');
    });

    it('should handle zero values in placar', () => {
      const placar: Placar = {
        sim: 0,
        nao: 0,
        abstencao: 0,
        obstrucao: 0,
      };

      expect(placar.sim).toBe(0);
    });

    it('should handle large numbers in IDs and counts', () => {
      const deputado: Deputado = {
        id: 999999,
        nome: 'Test',
        partido: 'PT',
        uf: 'SP',
      };

      const placar: Placar = {
        sim: 999999,
        nao: 999999,
        abstencao: 999999,
        obstrucao: 999999,
      };

      expect(deputado.id).toBe(999999);
      expect(placar.sim).toBe(999999);
    });
  });
});
