import { describe, expect, it } from 'vitest';
import type {
  CategoriaCivica,
  Deputado,
  Orientacao,
  PaginatedResponse,
  Proposicao,
  ProposicaoCategoria,
  SingleResponse,
  Votacao,
  VotacaoProposicao,
  Voto,
} from '@/lib/types';

interface ErrorResponse {
  error: {
    code: string;
    message: string;
  };
}

async function getPrimeiraVotacaoId(): Promise<number> {
  const response = await fetch('http://localhost/api/v1/votacoes?per_page=1');
  const payload = (await response.json()) as PaginatedResponse<Votacao>;

  expect(response.status).toBe(200);
  expect(payload.data[0]).toBeDefined();

  const votacao = payload.data[0];
  if (!votacao) {
    throw new Error('Nenhuma votação encontrada no fixture');
  }

  return votacao.id;
}

async function getPrimeiraProposicao(): Promise<Proposicao> {
  const response = await fetch('http://localhost/api/v1/proposicoes?per_page=1');
  const payload = (await response.json()) as PaginatedResponse<Proposicao>;

  expect(response.status).toBe(200);
  expect(payload.data[0]).toBeDefined();

  const proposicao = payload.data[0];
  if (!proposicao) {
    throw new Error('Nenhuma proposição encontrada no fixture');
  }

  return proposicao;
}

describe('MSW Handlers', () => {
  describe('Deputados handlers', () => {
    it('deve retornar lista paginada de deputados', async () => {
      const response = await fetch('http://localhost/api/v1/deputados');
      const payload = (await response.json()) as PaginatedResponse<Deputado>;

      expect(response.status).toBe(200);
      expect(payload.data).toHaveLength(20);
      expect(payload.pagination).toEqual({
        page: 1,
        per_page: 20,
        total: 513,
      });
      expect(payload.data[0]).toHaveProperty('id');
      expect(payload.data[0]).toHaveProperty('nome');
    });

    it('deve suportar filtros combinados em deputados', async () => {
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
      expect(payload.data.sigla_partido).toBeDefined();
    });

    it('deve retornar 400 para ID de deputado inválido', async () => {
      const response = await fetch('http://localhost/api/v1/deputados/abc');
      const payload = (await response.json()) as ErrorResponse;

      expect(response.status).toBe(400);
      expect(payload.error.code).toBe('VALIDATION_ERROR');
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

  describe('Proposições handlers', () => {
    it('deve retornar lista paginada de proposições', async () => {
      const response = await fetch('http://localhost/api/v1/proposicoes');
      const payload = (await response.json()) as PaginatedResponse<Proposicao>;

      expect(response.status).toBe(200);
      expect(payload.data).toHaveLength(20);
      expect(payload.pagination.page).toBe(1);
      expect(payload.pagination.per_page).toBe(20);
      expect(payload.pagination.total).toBeGreaterThan(0);
    });

    it('deve filtrar proposições por tipo e ano', async () => {
      const amostra = await getPrimeiraProposicao();

      const response = await fetch(
        `http://localhost/api/v1/proposicoes?tipo=${encodeURIComponent(amostra.tipo)}&ano=${amostra.ano}&per_page=200`
      );
      const payload = (await response.json()) as PaginatedResponse<Proposicao>;

      expect(response.status).toBe(200);
      payload.data.forEach((proposicao) => {
        expect(proposicao.tipo).toBe(amostra.tipo);
        expect(proposicao.ano).toBe(amostra.ano);
      });
    });

    it('deve retornar 400 para filtro ano inválido', async () => {
      const response = await fetch('http://localhost/api/v1/proposicoes?ano=20a4');
      const payload = (await response.json()) as ErrorResponse;

      expect(response.status).toBe(400);
      expect(payload.error.code).toBe('VALIDATION_ERROR');
    });

    it('deve retornar proposição única por ID', async () => {
      const proposicao = await getPrimeiraProposicao();
      const response = await fetch(`http://localhost/api/v1/proposicoes/${proposicao.id}`);
      const payload = (await response.json()) as SingleResponse<Proposicao>;

      expect(response.status).toBe(200);
      expect(payload.data.id).toBe(proposicao.id);
      expect(payload.data.ementa).toBeDefined();
    });

    it('deve retornar categorias de uma proposição com envelope paginado', async () => {
      const proposicao = await getPrimeiraProposicao();
      const response = await fetch(`http://localhost/api/v1/proposicoes/${proposicao.id}/categorias`);
      const payload = (await response.json()) as PaginatedResponse<ProposicaoCategoria>;

      expect(response.status).toBe(200);
      payload.data.forEach((categoriaRelacao) => {
        expect(categoriaRelacao.proposicao_id).toBe(proposicao.id);
      });
      expect(payload.pagination).toHaveProperty('total');
    });

    it('deve retornar 404 para proposição inexistente no sub-endpoint de categorias', async () => {
      const response = await fetch('http://localhost/api/v1/proposicoes/999999/categorias');
      const payload = (await response.json()) as ErrorResponse;

      expect(response.status).toBe(404);
      expect(payload.error.code).toBe('NOT_FOUND');
    });
  });

  describe('Votações handlers', () => {
    it('deve retornar lista paginada de votações', async () => {
      const response = await fetch('http://localhost/api/v1/votacoes');
      const payload = (await response.json()) as PaginatedResponse<Votacao>;

      expect(response.status).toBe(200);
      expect(payload.data).toHaveLength(20);
      expect(payload.pagination).toEqual({
        page: 1,
        per_page: 20,
        total: 50,
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

    it('deve retornar votação única por ID com envelope de recurso', async () => {
      const votacaoId = await getPrimeiraVotacaoId();
      const response = await fetch(`http://localhost/api/v1/votacoes/${votacaoId}`);
      const payload = (await response.json()) as SingleResponse<Votacao>;

      expect(response.status).toBe(200);
      expect(payload.data.id).toBe(votacaoId);
      expect(payload.data.placar).toBeDefined();
      expect(payload.data.proposicao).toBeDefined();
    });

    it('deve retornar 400 para ID inválido no detalhe de votação', async () => {
      const response = await fetch('http://localhost/api/v1/votacoes/abc');
      const payload = (await response.json()) as ErrorResponse;

      expect(response.status).toBe(400);
      expect(payload.error.code).toBe('VALIDATION_ERROR');
    });

    it('deve retornar proposições de uma votação', async () => {
      const votacaoId = await getPrimeiraVotacaoId();
      const response = await fetch(`http://localhost/api/v1/votacoes/${votacaoId}/proposicoes`);
      const payload = (await response.json()) as PaginatedResponse<VotacaoProposicao>;

      expect(response.status).toBe(200);
      payload.data.forEach((item) => {
        expect(item.votacao_id).toBe(votacaoId);
        expect(item.proposicao_id).toBeDefined();
      });
      expect(payload.pagination).toHaveProperty('total');
    });

    it('deve retornar 400 para ID inválido no sub-endpoint de proposições da votação', async () => {
      const response = await fetch('http://localhost/api/v1/votacoes/abc/proposicoes');
      const payload = (await response.json()) as ErrorResponse;

      expect(response.status).toBe(400);
      expect(payload.error.code).toBe('VALIDATION_ERROR');
    });

    it('deve retornar 404 para votação inexistente no sub-endpoint de proposições', async () => {
      const response = await fetch('http://localhost/api/v1/votacoes/999999/proposicoes');
      const payload = (await response.json()) as ErrorResponse;

      expect(response.status).toBe(404);
      expect(payload.error.code).toBe('NOT_FOUND');
    });
  });

  describe('Orientações handlers', () => {
    it('deve retornar orientações paginadas para uma votação', async () => {
      const votacaoId = await getPrimeiraVotacaoId();
      const response = await fetch(`http://localhost/api/v1/votacoes/${votacaoId}/orientacoes`);
      const payload = (await response.json()) as PaginatedResponse<Orientacao>;

      expect(response.status).toBe(200);
      expect(payload.data.length).toBeGreaterThan(0);
      payload.data.forEach((orientacao) => {
        expect(orientacao.votacao_id).toBe(votacaoId);
      });
    });

    it('deve retornar página vazia de orientações quando page estiver fora do range', async () => {
      const votacaoId = await getPrimeiraVotacaoId();
      const response = await fetch(`http://localhost/api/v1/votacoes/${votacaoId}/orientacoes?page=999&per_page=100`);
      const payload = (await response.json()) as PaginatedResponse<Orientacao>;

      expect(response.status).toBe(200);
      expect(payload.data).toHaveLength(0);
      expect(payload.pagination.total).toBeGreaterThan(0);
    });

    it('deve retornar 400 para ID inválido em orientações', async () => {
      const response = await fetch('http://localhost/api/v1/votacoes/xyz/orientacoes');
      const payload = (await response.json()) as ErrorResponse;

      expect(response.status).toBe(400);
      expect(payload.error.code).toBe('VALIDATION_ERROR');
    });

    it('deve retornar 404 para votação inexistente em orientações', async () => {
      const response = await fetch('http://localhost/api/v1/votacoes/999999/orientacoes');
      const payload = (await response.json()) as ErrorResponse;

      expect(response.status).toBe(404);
      expect(payload.error.code).toBe('NOT_FOUND');
    });
  });

  describe('Categorias cívicas handlers', () => {
    it('deve retornar lista paginada de categorias cívicas', async () => {
      const response = await fetch('http://localhost/api/v1/categorias-civicas?per_page=3');
      const payload = (await response.json()) as PaginatedResponse<CategoriaCivica>;

      expect(response.status).toBe(200);
      expect(payload.data).toHaveLength(3);
      expect(payload.pagination).toEqual({
        page: 1,
        per_page: 3,
        total: 8,
      });
      expect(payload.data[0]).toHaveProperty('codigo');
      expect(payload.data[0]).toHaveProperty('nome');
    });
  });

  describe('Votos handlers', () => {
    it('deve retornar lista paginada de votos para uma votação', async () => {
      const votacaoId = await getPrimeiraVotacaoId();
      const response = await fetch(`http://localhost/api/v1/votacoes/${votacaoId}/votos`);
      const payload = (await response.json()) as PaginatedResponse<Voto>;

      expect(response.status).toBe(200);
      expect(payload.data).toHaveLength(20);
      expect(payload.pagination).toEqual({
        page: 1,
        per_page: 20,
        total: 513,
      });
    });

    it('deve retornar 404 para votação inexistente no endpoint aninhado de votos', async () => {
      const response = await fetch('http://localhost/api/v1/votacoes/999999/votos');
      const payload = (await response.json()) as ErrorResponse;

      expect(response.status).toBe(404);
      expect(payload.error.code).toBe('NOT_FOUND');
    });

    it('deve exigir votacao_id no endpoint direto de votos', async () => {
      const response = await fetch('http://localhost/api/v1/votos');
      const payload = (await response.json()) as ErrorResponse;

      expect(response.status).toBe(400);
      expect(payload.error.code).toBe('VALIDATION_ERROR');
    });

    it('deve retornar 400 para votacao_id inválido no endpoint direto de votos', async () => {
      const response = await fetch('http://localhost/api/v1/votos?votacao_id=abc');
      const payload = (await response.json()) as ErrorResponse;

      expect(response.status).toBe(400);
      expect(payload.error.code).toBe('VALIDATION_ERROR');
    });

    it('deve retornar 404 para votação inexistente no endpoint direto de votos', async () => {
      const response = await fetch('http://localhost/api/v1/votos?votacao_id=999999');
      const payload = (await response.json()) as ErrorResponse;

      expect(response.status).toBe(404);
      expect(payload.error.code).toBe('NOT_FOUND');
    });

    it('deve retornar votos filtrados por votacao_id no endpoint direto', async () => {
      const votacaoId = await getPrimeiraVotacaoId();
      const response = await fetch(`http://localhost/api/v1/votos?votacao_id=${votacaoId}&per_page=30`);
      const payload = (await response.json()) as PaginatedResponse<Voto>;

      expect(response.status).toBe(200);
      expect(payload.data).toHaveLength(30);
      payload.data.forEach((voto) => {
        expect(voto.votacao_id).toBe(votacaoId);
        expect(voto.deputado).toBeDefined();
      });
    });

    it('deve manter consistência entre endpoint aninhado e endpoint direto de votos', async () => {
      const votacaoId = await getPrimeiraVotacaoId();

      const nestedResponse = await fetch(`http://localhost/api/v1/votacoes/${votacaoId}/votos?page=1&per_page=10`);
      const nestedPayload = (await nestedResponse.json()) as PaginatedResponse<Voto>;

      const directResponse = await fetch(`http://localhost/api/v1/votos?votacao_id=${votacaoId}&page=1&per_page=10`);
      const directPayload = (await directResponse.json()) as PaginatedResponse<Voto>;

      expect(nestedResponse.status).toBe(200);
      expect(directResponse.status).toBe(200);
      expect(nestedPayload.pagination.total).toBe(directPayload.pagination.total);

      nestedPayload.data.forEach((voto, index) => {
        expect(voto.id).toBe(directPayload.data[index]?.id);
        expect(voto.voto).toBe(directPayload.data[index]?.voto);
      });
    });
  });

  describe('Cobertura de endpoints', () => {
    it('deve cobrir todos os 12 endpoints MSW mapeados sem unhandled request', async () => {
      const votacaoId = await getPrimeiraVotacaoId();
      const proposicao = await getPrimeiraProposicao();

      const responses = await Promise.all([
        fetch('http://localhost/api/v1/deputados'),
        fetch('http://localhost/api/v1/deputados/1'),
        fetch('http://localhost/api/v1/proposicoes'),
        fetch(`http://localhost/api/v1/proposicoes/${proposicao.id}`),
        fetch(`http://localhost/api/v1/proposicoes/${proposicao.id}/categorias`),
        fetch('http://localhost/api/v1/votacoes'),
        fetch(`http://localhost/api/v1/votacoes/${votacaoId}`),
        fetch(`http://localhost/api/v1/votacoes/${votacaoId}/proposicoes`),
        fetch(`http://localhost/api/v1/votacoes/${votacaoId}/orientacoes`),
        fetch(`http://localhost/api/v1/votacoes/${votacaoId}/votos`),
        fetch('http://localhost/api/v1/categorias-civicas'),
        fetch(`http://localhost/api/v1/votos?votacao_id=${votacaoId}`),
      ]);

      responses.forEach((response) => {
        expect(response.status).toBe(200);
      });
    });
  });

  describe('Error handling', () => {
    it('deve retornar lista vazia quando filtro de deputados não encontra resultados', async () => {
      const response = await fetch('http://localhost/api/v1/deputados?nome=XYZ_NONEXISTENT_');
      const payload = (await response.json()) as PaginatedResponse<Deputado>;

      expect(response.status).toBe(200);
      expect(payload.data).toHaveLength(0);
      expect(payload.pagination.total).toBe(0);
    });
  });
});
