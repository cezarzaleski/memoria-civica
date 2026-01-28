import { describe, it, expect } from 'vitest';
import type { Deputado, Votacao, Voto } from '@/lib/types';

/**
 * Integration tests for MSW handlers
 * Tests that handlers correctly intercept and respond to fetch requests
 */
describe('MSW Handlers', () => {
  // MSW server is already configured in vitest.setup.ts
  // but we'll ensure it's clean for these tests

  describe('Deputados handlers', () => {
    it('should return list of deputados', async () => {
      const response = await fetch('http://localhost/api/v1/deputados');
      const data = (await response.json()) as Deputado[];

      expect(response.status).toBe(200);
      expect(Array.isArray(data)).toBe(true);
      expect(data.length).toBe(513);
      expect(data[0]).toHaveProperty('id');
      expect(data[0]).toHaveProperty('nome');
      expect(data[0]).toHaveProperty('partido');
      expect(data[0]).toHaveProperty('uf');
    });

    it('should filter deputados by nome query parameter', async () => {
      const response = await fetch('http://localhost/api/v1/deputados?nome=João');
      const data = (await response.json()) as Deputado[];

      expect(response.status).toBe(200);
      expect(Array.isArray(data)).toBe(true);
      data.forEach((dep) => {
        expect(dep.nome.toLowerCase()).toContain('joão');
      });
    });

    it('should filter deputados by partido query parameter', async () => {
      // First, get a list to know what parties exist
      const listResponse = await fetch('http://localhost/api/v1/deputados');
      const allDeputados = (await listResponse.json()) as Deputado[];
      const testPartido = allDeputados[0].partido;

      // Now filter by that party
      const response = await fetch(`http://localhost/api/v1/deputados?partido=${testPartido}`);
      const data = (await response.json()) as Deputado[];

      expect(response.status).toBe(200);
      data.forEach((dep) => {
        expect(dep.partido).toBe(testPartido);
      });
    });

    it('should filter deputados by uf query parameter', async () => {
      const response = await fetch('http://localhost/api/v1/deputados?uf=SP');
      const data = (await response.json()) as Deputado[];

      expect(response.status).toBe(200);
      data.forEach((dep) => {
        expect(dep.uf).toBe('SP');
      });
    });

    it('should support multiple filters combined', async () => {
      const response = await fetch('http://localhost/api/v1/deputados?nome=Silva&uf=RJ');
      const data = (await response.json()) as Deputado[];

      expect(response.status).toBe(200);
      data.forEach((dep) => {
        expect(dep.nome.toLowerCase()).toContain('silva');
        expect(dep.uf).toBe('RJ');
      });
    });

    it('should return single deputado by ID', async () => {
      const response = await fetch('http://localhost/api/v1/deputados/1');
      const data = (await response.json()) as Deputado;

      expect(response.status).toBe(200);
      expect(data.id).toBe(1);
      expect(data.nome).toBeDefined();
      expect(data.partido).toBeDefined();
    });

    it('should return 404 for non-existent deputado ID', async () => {
      const response = await fetch('http://localhost/api/v1/deputados/99999');

      expect(response.status).toBe(404);
    });
  });

  describe('Votações handlers', () => {
    it('should return list of votações', async () => {
      const response = await fetch('http://localhost/api/v1/votacoes');
      const data = (await response.json()) as Votacao[];

      expect(response.status).toBe(200);
      expect(Array.isArray(data)).toBe(true);
      expect(data.length).toBeGreaterThan(0);
    });

    it('should return votações ordered by data descending', async () => {
      const response = await fetch('http://localhost/api/v1/votacoes');
      const data = (await response.json()) as Votacao[];

      // Check that votações are ordered by date descending
      for (let i = 0; i < data.length - 1; i++) {
        const current = new Date(data[i].data);
        const next = new Date(data[i + 1].data);
        expect(current.getTime()).toBeGreaterThanOrEqual(next.getTime());
      }
    });

    it('should include nested proposicao in votações', async () => {
      const response = await fetch('http://localhost/api/v1/votacoes');
      const data = (await response.json()) as Votacao[];

      data.forEach((votacao) => {
        expect(votacao.proposicao).toBeDefined();
        expect(votacao.proposicao?.id).toBeDefined();
        expect(votacao.proposicao?.tipo).toBeDefined();
      });
    });

    it('should return single votação by ID', async () => {
      // First get a list to find a valid ID
      const listResponse = await fetch('http://localhost/api/v1/votacoes');
      const votacoes = (await listResponse.json()) as Votacao[];
      const testId = votacoes[0].id;

      // Now fetch that specific votação
      const response = await fetch(`http://localhost/api/v1/votacoes/${testId}`);
      const data = (await response.json()) as Votacao;

      expect(response.status).toBe(200);
      expect(data.id).toBe(testId);
      expect(data.proposicao).toBeDefined();
      expect(data.placar).toBeDefined();
    });

    it('should return 404 for non-existent votação ID', async () => {
      const response = await fetch('http://localhost/api/v1/votacoes/non-existent-id');

      expect(response.status).toBe(404);
    });

    it('should have valid placar in votações', async () => {
      const response = await fetch('http://localhost/api/v1/votacoes');
      const data = (await response.json()) as Votacao[];

      data.forEach((votacao) => {
        expect(votacao.placar.sim).toBeGreaterThanOrEqual(0);
        expect(votacao.placar.nao).toBeGreaterThanOrEqual(0);
        expect(votacao.placar.abstencao).toBeGreaterThanOrEqual(0);
        expect(votacao.placar.obstrucao).toBeGreaterThanOrEqual(0);

        const total = votacao.placar.sim + votacao.placar.nao + votacao.placar.abstencao + votacao.placar.obstrucao;
        expect(total).toBe(513);
      });
    });
  });

  describe('Votos handlers', () => {
    it('should return list of votos for a votação', async () => {
      // First, get a votação ID
      const votacaoResponse = await fetch('http://localhost/api/v1/votacoes');
      const votacoes = (await votacaoResponse.json()) as Votacao[];
      const testVotacaoId = votacoes[0].id;

      // Now get votos for that votação
      const response = await fetch(`http://localhost/api/v1/votacoes/${testVotacaoId}/votos`);
      const data = (await response.json()) as Voto[];

      expect(response.status).toBe(200);
      expect(Array.isArray(data)).toBe(true);
      expect(data.length).toBe(513); // One voto per deputy
    });

    it('should include nested deputado in votos', async () => {
      const votacaoResponse = await fetch('http://localhost/api/v1/votacoes');
      const votacoes = (await votacaoResponse.json()) as Votacao[];
      const testVotacaoId = votacoes[0].id;

      const response = await fetch(`http://localhost/api/v1/votacoes/${testVotacaoId}/votos`);
      const data = (await response.json()) as Voto[];

      data.forEach((voto) => {
        expect(voto.deputado).toBeDefined();
        expect(voto.deputado?.id).toBeDefined();
        expect(voto.deputado?.nome).toBeDefined();
      });
    });

    it('should have valid voto tipos', async () => {
      const votacaoResponse = await fetch('http://localhost/api/v1/votacoes');
      const votacoes = (await votacaoResponse.json()) as Votacao[];
      const testVotacaoId = votacoes[0].id;

      const response = await fetch(`http://localhost/api/v1/votacoes/${testVotacaoId}/votos`);
      const data = (await response.json()) as Voto[];

      const validTipos = ['SIM', 'NAO', 'ABSTENCAO', 'OBSTRUCAO'];

      data.forEach((voto) => {
        expect(validTipos).toContain(voto.tipo);
      });
    });

    it('should have correct votacao_id in votos', async () => {
      const votacaoResponse = await fetch('http://localhost/api/v1/votacoes');
      const votacoes = (await votacaoResponse.json()) as Votacao[];
      const testVotacaoId = votacoes[0].id;

      const response = await fetch(`http://localhost/api/v1/votacoes/${testVotacaoId}/votos`);
      const data = (await response.json()) as Voto[];

      data.forEach((voto) => {
        expect(voto.votacao_id).toBe(testVotacaoId);
      });
    });

    it('should return consistent votos for same votação across multiple requests', async () => {
      const votacaoResponse = await fetch('http://localhost/api/v1/votacoes');
      const votacoes = (await votacaoResponse.json()) as Votacao[];
      const testVotacaoId = votacoes[0].id;

      // Request votos twice
      const response1 = await fetch(`http://localhost/api/v1/votacoes/${testVotacaoId}/votos`);
      const data1 = (await response1.json()) as Voto[];

      const response2 = await fetch(`http://localhost/api/v1/votacoes/${testVotacaoId}/votos`);
      const data2 = (await response2.json()) as Voto[];

      // Verify same data returned both times
      expect(data1.length).toBe(data2.length);
      data1.forEach((voto1, index) => {
        expect(voto1.id).toBe(data2[index].id);
        expect(voto1.tipo).toBe(data2[index].tipo);
      });
    });
  });

  describe('Error handling', () => {
    it('should handle empty filter results gracefully', async () => {
      const response = await fetch('http://localhost/api/v1/deputados?nome=XYZ_NONEXISTENT_');
      const data = (await response.json()) as Deputado[];

      expect(response.status).toBe(200);
      expect(Array.isArray(data)).toBe(true);
      expect(data.length).toBe(0);
    });
  });
});
