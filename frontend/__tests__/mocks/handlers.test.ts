import { describe, expect, it } from 'vitest';
import type { Deputado, PaginatedResponse, SingleResponse, Votacao, Voto } from '@/lib/types';

describe('MSW Handlers', () => {
  describe('Deputados handlers', () => {
    it('deve retornar lista paginada de deputados', async () => {
      const response = await fetch('http://localhost/api/v1/deputados');
      const payload = (await response.json()) as PaginatedResponse<Deputado>;

      expect(response.status).toBe(200);
      expect(Array.isArray(payload.data)).toBe(true);
      expect(payload.data.length).toBe(20);
      expect(payload.pagination).toEqual({
        page: 1,
        per_page: 20,
        total: 513,
      });
      expect(payload.data[0]).toHaveProperty('id');
      expect(payload.data[0]).toHaveProperty('nome');
      expect(payload.data[0]).toHaveProperty('sigla_partido');
      expect(payload.data[0]).toHaveProperty('uf');
    });

    it('deve filtrar deputados por nome', async () => {
      const response = await fetch('http://localhost/api/v1/deputados?nome=João&per_page=200');
      const payload = (await response.json()) as PaginatedResponse<Deputado>;

      expect(response.status).toBe(200);
      payload.data.forEach((deputado) => {
        expect(deputado.nome.toLowerCase()).toContain('joão');
      });
      expect(payload.pagination.total).toBe(payload.data.length);
    });

    it('deve filtrar deputados por partido', async () => {
      const listResponse = await fetch('http://localhost/api/v1/deputados?per_page=1');
      const listPayload = (await listResponse.json()) as PaginatedResponse<Deputado>;
      const testPartido = listPayload.data[0].sigla_partido;

      const response = await fetch(`http://localhost/api/v1/deputados?partido=${testPartido}&per_page=200`);
      const payload = (await response.json()) as PaginatedResponse<Deputado>;

      expect(response.status).toBe(200);
      payload.data.forEach((deputado) => {
        expect(deputado.sigla_partido).toBe(testPartido);
      });
    });

    it('deve filtrar deputados por UF', async () => {
      const response = await fetch('http://localhost/api/v1/deputados?uf=SP&per_page=200');
      const payload = (await response.json()) as PaginatedResponse<Deputado>;

      expect(response.status).toBe(200);
      payload.data.forEach((deputado) => {
        expect(deputado.uf).toBe('SP');
      });
    });

    it('deve suportar múltiplos filtros combinados', async () => {
      const response = await fetch('http://localhost/api/v1/deputados?nome=Silva&uf=RJ&per_page=200');
      const payload = (await response.json()) as PaginatedResponse<Deputado>;

      expect(response.status).toBe(200);
      payload.data.forEach((deputado) => {
        expect(deputado.nome.toLowerCase()).toContain('silva');
        expect(deputado.uf).toBe('RJ');
      });
    });

    it('deve retornar deputado único por ID com envelope de recurso', async () => {
      const response = await fetch('http://localhost/api/v1/deputados/1');
      const payload = (await response.json()) as SingleResponse<Deputado>;

      expect(response.status).toBe(200);
      expect(payload.data.id).toBe(1);
      expect(payload.data.nome).toBeDefined();
      expect(payload.data.sigla_partido).toBeDefined();
    });

    it('deve retornar 404 para deputado inexistente', async () => {
      const response = await fetch('http://localhost/api/v1/deputados/99999');
      expect(response.status).toBe(404);
    });

    it('deve retornar 400 com envelope de erro para ID de deputado inválido', async () => {
      const response = await fetch('http://localhost/api/v1/deputados/1abc');
      const payload = (await response.json()) as {
        error: {
          code: string;
          message: string;
        };
      };

      expect(response.status).toBe(400);
      expect(payload.error.code).toBe('VALIDATION_ERROR');
      expect(payload.error.message).toContain('inválido');
    });

    it('deve retornar página vazia quando page estiver fora do range', async () => {
      const response = await fetch('http://localhost/api/v1/deputados?page=999&per_page=50');
      const payload = (await response.json()) as PaginatedResponse<Deputado>;

      expect(response.status).toBe(200);
      expect(payload.data).toHaveLength(0);
      expect(payload.pagination).toEqual({
        page: 999,
        per_page: 50,
        total: 513,
      });
    });
  });

  describe('Votações handlers', () => {
    it('deve retornar lista paginada de votações', async () => {
      const response = await fetch('http://localhost/api/v1/votacoes');
      const payload = (await response.json()) as PaginatedResponse<Votacao>;

      expect(response.status).toBe(200);
      expect(Array.isArray(payload.data)).toBe(true);
      expect(payload.data.length).toBe(20);
      expect(payload.pagination).toEqual({
        page: 1,
        per_page: 20,
        total: 50,
      });
    });

    it('deve retornar votações ordenadas por data_hora desc', async () => {
      const response = await fetch('http://localhost/api/v1/votacoes?per_page=50');
      const payload = (await response.json()) as PaginatedResponse<Votacao>;

      for (let i = 0; i < payload.data.length - 1; i += 1) {
        const current = new Date(payload.data[i].data_hora);
        const next = new Date(payload.data[i + 1].data_hora);
        expect(current.getTime()).toBeGreaterThanOrEqual(next.getTime());
      }
    });

    it('deve incluir proposicao aninhada em votações', async () => {
      const response = await fetch('http://localhost/api/v1/votacoes?per_page=50');
      const payload = (await response.json()) as PaginatedResponse<Votacao>;

      payload.data.forEach((votacao) => {
        expect(votacao.proposicao).toBeDefined();
        expect(votacao.proposicao?.id).toBeDefined();
        expect(votacao.proposicao?.tipo).toBeDefined();
      });
    });

    it('deve retornar votação única por ID com envelope de recurso', async () => {
      const listResponse = await fetch('http://localhost/api/v1/votacoes?per_page=1');
      const listPayload = (await listResponse.json()) as PaginatedResponse<Votacao>;
      const testId = listPayload.data[0].id;

      const response = await fetch(`http://localhost/api/v1/votacoes/${testId}`);
      const payload = (await response.json()) as SingleResponse<Votacao>;

      expect(response.status).toBe(200);
      expect(payload.data.id).toBe(testId);
      expect(payload.data.proposicao).toBeDefined();
      expect(payload.data.placar).toBeDefined();
    });

    it('deve retornar 404 para votação inexistente', async () => {
      const response = await fetch('http://localhost/api/v1/votacoes/999999');
      expect(response.status).toBe(404);
    });

    it('deve manter placar válido nas votações', async () => {
      const response = await fetch('http://localhost/api/v1/votacoes?per_page=50');
      const payload = (await response.json()) as PaginatedResponse<Votacao>;

      payload.data.forEach((votacao) => {
        expect(votacao.placar.votos_sim).toBeGreaterThanOrEqual(0);
        expect(votacao.placar.votos_nao).toBeGreaterThanOrEqual(0);
        expect(votacao.placar.votos_outros).toBeGreaterThanOrEqual(0);

        const total = votacao.placar.votos_sim + votacao.placar.votos_nao + votacao.placar.votos_outros;
        expect(total).toBe(513);
      });
    });

    it('deve filtrar votações por sigla_orgao e eh_nominal', async () => {
      const response = await fetch('http://localhost/api/v1/votacoes?sigla_orgao=PLEN&eh_nominal=true&per_page=100');
      const payload = (await response.json()) as PaginatedResponse<Votacao>;

      expect(response.status).toBe(200);
      payload.data.forEach((votacao) => {
        expect(votacao.sigla_orgao).toBe('PLEN');
        expect(votacao.eh_nominal).toBe(true);
      });
    });
  });

  describe('Votos handlers', () => {
    it('deve retornar lista paginada de votos para uma votação', async () => {
      const votacaoResponse = await fetch('http://localhost/api/v1/votacoes?per_page=1');
      const votacaoPayload = (await votacaoResponse.json()) as PaginatedResponse<Votacao>;
      const testVotacaoId = votacaoPayload.data[0].id;

      const response = await fetch(`http://localhost/api/v1/votacoes/${testVotacaoId}/votos`);
      const payload = (await response.json()) as PaginatedResponse<Voto>;

      expect(response.status).toBe(200);
      expect(Array.isArray(payload.data)).toBe(true);
      expect(payload.data.length).toBe(20);
      expect(payload.pagination).toEqual({
        page: 1,
        per_page: 20,
        total: 513,
      });
    });

    it('deve incluir deputado aninhado nos votos', async () => {
      const votacaoResponse = await fetch('http://localhost/api/v1/votacoes?per_page=1');
      const votacaoPayload = (await votacaoResponse.json()) as PaginatedResponse<Votacao>;
      const testVotacaoId = votacaoPayload.data[0].id;

      const response = await fetch(`http://localhost/api/v1/votacoes/${testVotacaoId}/votos?per_page=200`);
      const payload = (await response.json()) as PaginatedResponse<Voto>;

      payload.data.forEach((voto) => {
        expect(voto.deputado).toBeDefined();
        expect(voto.deputado?.id).toBeDefined();
        expect(voto.deputado?.nome).toBeDefined();
      });
    });

    it('deve retornar tipos de voto válidos', async () => {
      const votacaoResponse = await fetch('http://localhost/api/v1/votacoes?per_page=1');
      const votacaoPayload = (await votacaoResponse.json()) as PaginatedResponse<Votacao>;
      const testVotacaoId = votacaoPayload.data[0].id;

      const response = await fetch(`http://localhost/api/v1/votacoes/${testVotacaoId}/votos?per_page=200`);
      const payload = (await response.json()) as PaginatedResponse<Voto>;
      const validTipos = ['Sim', 'Não', 'Abstenção', 'Obstrução', 'Art. 17'];

      payload.data.forEach((voto) => {
        expect(validTipos).toContain(voto.voto);
      });
    });

    it('deve retornar votacao_id correto nos votos', async () => {
      const votacaoResponse = await fetch('http://localhost/api/v1/votacoes?per_page=1');
      const votacaoPayload = (await votacaoResponse.json()) as PaginatedResponse<Votacao>;
      const testVotacaoId = votacaoPayload.data[0].id;

      const response = await fetch(`http://localhost/api/v1/votacoes/${testVotacaoId}/votos?per_page=200`);
      const payload = (await response.json()) as PaginatedResponse<Voto>;

      payload.data.forEach((voto) => {
        expect(voto.votacao_id).toBe(testVotacaoId);
      });
    });

    it('deve manter consistência entre múltiplas requisições para a mesma votação', async () => {
      const votacaoResponse = await fetch('http://localhost/api/v1/votacoes?per_page=1');
      const votacaoPayload = (await votacaoResponse.json()) as PaginatedResponse<Votacao>;
      const testVotacaoId = votacaoPayload.data[0].id;

      const response1 = await fetch(`http://localhost/api/v1/votacoes/${testVotacaoId}/votos?page=1&per_page=50`);
      const payload1 = (await response1.json()) as PaginatedResponse<Voto>;

      const response2 = await fetch(`http://localhost/api/v1/votacoes/${testVotacaoId}/votos?page=1&per_page=50`);
      const payload2 = (await response2.json()) as PaginatedResponse<Voto>;

      expect(payload1.pagination.total).toBe(payload2.pagination.total);
      expect(payload1.data.length).toBe(payload2.data.length);

      payload1.data.forEach((voto, index) => {
        expect(voto.id).toBe(payload2.data[index].id);
        expect(voto.voto).toBe(payload2.data[index].voto);
      });
    });

    it('deve retornar página vazia de votos quando page estiver fora do range', async () => {
      const votacaoResponse = await fetch('http://localhost/api/v1/votacoes?per_page=1');
      const votacaoPayload = (await votacaoResponse.json()) as PaginatedResponse<Votacao>;
      const testVotacaoId = votacaoPayload.data[0].id;

      const response = await fetch(`http://localhost/api/v1/votacoes/${testVotacaoId}/votos?page=999&per_page=100`);
      const payload = (await response.json()) as PaginatedResponse<Voto>;

      expect(response.status).toBe(200);
      expect(payload.data).toHaveLength(0);
      expect(payload.pagination.total).toBe(513);
    });

    it('deve retornar 400 com envelope de erro para votacao_id inválido', async () => {
      const response = await fetch('http://localhost/api/v1/votacoes/abc123/votos');
      const payload = (await response.json()) as {
        error: {
          code: string;
          message: string;
        };
      };

      expect(response.status).toBe(400);
      expect(payload.error.code).toBe('VALIDATION_ERROR');
      expect(payload.error.message).toContain('inválido');
    });
  });

  describe('Error handling', () => {
    it('deve retornar lista vazia quando filtro não encontra resultados', async () => {
      const response = await fetch('http://localhost/api/v1/deputados?nome=XYZ_NONEXISTENT_');
      const payload = (await response.json()) as PaginatedResponse<Deputado>;

      expect(response.status).toBe(200);
      expect(Array.isArray(payload.data)).toBe(true);
      expect(payload.data).toHaveLength(0);
      expect(payload.pagination.total).toBe(0);
    });
  });
});
