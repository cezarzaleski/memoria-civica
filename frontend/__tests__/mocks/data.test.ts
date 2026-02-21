import { describe, it, expect } from 'vitest';
import {
  generateDeputados,
  getDeputadoById,
  filterDeputadosByNome,
  filterDeputadosByPartido,
  filterDeputadosByUF,
} from '@/mocks/data/deputados';
import { generateProposicoes, getProposicaoById } from '@/mocks/data/proposicoes';
import { generateVotacoes, getVotacaoById } from '@/mocks/data/votacoes';
import { generateVotos, countVotosByTipo } from '@/mocks/data/votos';
import { TipoProposicao, ResultadoVotacao, TipoVoto } from '@/lib/types';

describe('Mock Data Factories', () => {
  describe('generateDeputados', () => {
    it('should generate 513 deputies by default', () => {
      const deputies = generateDeputados();
      expect(deputies).toHaveLength(513);
    });

    it('should generate correct number of deputies when count is specified', () => {
      const deputies = generateDeputados(100);
      expect(deputies).toHaveLength(100);
    });

    it('should generate deputies with required fields', () => {
      const deputies = generateDeputados(10);

      deputies.forEach((deputy) => {
        expect(deputy.id).toBeDefined();
        expect(deputy.nome).toBeDefined();
        expect(deputy.sigla_partido).toBeDefined();
        expect(deputy.uf).toBeDefined();
      });
    });

    it('should have unique IDs for each deputy', () => {
      const deputies = generateDeputados(50);
      const ids = deputies.map((d) => d.id);
      const uniqueIds = new Set(ids);

      expect(uniqueIds.size).toBe(ids.length);
    });

    it('should have valid UF (state) abbreviations', () => {
      const deputies = generateDeputados(50);
      const validUFs = [
        'SP', 'MG', 'RJ', 'BA', 'PR', 'RS', 'PE', 'CE', 'PA', 'GO',
        'PB', 'SC', 'MA', 'ES', 'PI', 'AL', 'RN', 'MT', 'MS', 'DF',
        'AC', 'AM', 'AP', 'RO', 'RR', 'TO',
      ];

      deputies.forEach((deputy) => {
        expect(validUFs).toContain(deputy.uf);
      });
    });

    it('should include foto_url for all deputies', () => {
      const deputies = generateDeputados(10);

      deputies.forEach((deputy) => {
        expect(deputy.foto_url).toBeDefined();
        expect(deputy.foto_url).toContain('camara.leg.br');
      });
    });

    it('should have email field (may be undefined)', () => {
      const deputies = generateDeputados(50);
      let hasEmail = false;

      deputies.forEach((deputy) => {
        if (deputy.email) {
          hasEmail = true;
          expect(deputy.email).toMatch(/@/);
        }
      });

      // At least some deputies should have emails
      expect(hasEmail).toBe(true);
    });
  });

  describe('deputados filtering functions', () => {
    const deputies = generateDeputados(50);

    it('should filter deputies by name', () => {
      const filtered = filterDeputadosByNome(deputies, 'João');
      const allMatch = filtered.every((d) => d.nome.toLowerCase().includes('joão'));

      expect(filtered.length).toBeGreaterThan(0);
      expect(allMatch).toBe(true);
    });

    it('should filter deputies by partido', () => {
      const partido = deputies[0].sigla_partido;
      const filtered = filterDeputadosByPartido(deputies, partido);

      expect(filtered.length).toBeGreaterThan(0);
      expect(filtered.every((d) => d.sigla_partido === partido)).toBe(true);
    });

    it('should filter deputies by UF', () => {
      const uf = deputies[0].uf;
      const filtered = filterDeputadosByUF(deputies, uf);

      expect(filtered.length).toBeGreaterThan(0);
      expect(filtered.every((d) => d.uf === uf)).toBe(true);
    });

    it('should return deputy by ID', () => {
      const target = deputies[10];
      const found = getDeputadoById(deputies, target.id);

      expect(found).toEqual(target);
    });

    it('should return undefined for non-existent deputy ID', () => {
      const found = getDeputadoById(deputies, 99999);
      expect(found).toBeUndefined();
    });
  });

  describe('generateProposicoes', () => {
    it('should generate 50 propositions by default', () => {
      const propositions = generateProposicoes();
      expect(propositions).toHaveLength(50);
    });

    it('should generate correct number when specified', () => {
      const propositions = generateProposicoes(30);
      expect(propositions).toHaveLength(30);
    });

    it('should have required fields for each proposition', () => {
      const propositions = generateProposicoes(10);

      propositions.forEach((prop) => {
        expect(prop.id).toBeDefined();
        expect(prop.tipo).toBeDefined();
        expect(prop.numero).toBeDefined();
        expect(prop.ano).toBeDefined();
        expect(prop.ementa).toBeDefined();
      });
    });

    it('should use valid TipoProposicao values', () => {
      const propositions = generateProposicoes(20);
      const validTipos = Object.values(TipoProposicao);

      propositions.forEach((prop) => {
        expect(validTipos).toContain(prop.tipo);
      });
    });

    it('should have reasonable year values', () => {
      const propositions = generateProposicoes(20);
      const currentYear = new Date().getFullYear();

      propositions.forEach((prop) => {
        expect(prop.ano).toBeGreaterThanOrEqual(currentYear - 3);
        expect(prop.ano).toBeLessThanOrEqual(currentYear);
      });
    });

    it('should return proposition by ID', () => {
      const propositions = generateProposicoes(20);
      const target = propositions[5];
      const found = getProposicaoById(propositions, target.id);

      expect(found).toEqual(target);
    });
  });

  describe('generateVotacoes', () => {
    it('should generate 50 votações by default', () => {
      const votacoes = generateVotacoes();
      expect(votacoes).toHaveLength(50);
    });

    it('should generate votações sorted by date descending', () => {
      const votacoes = generateVotacoes(20);

      for (let i = 0; i < votacoes.length - 1; i++) {
        const current = new Date(votacoes[i].data_hora);
        const next = new Date(votacoes[i + 1].data_hora);
        expect(current.getTime()).toBeGreaterThanOrEqual(next.getTime());
      }
    });

    it('should have nested proposicao in each votação', () => {
      const votacoes = generateVotacoes(10);

      votacoes.forEach((votacao) => {
        expect(votacao.proposicao).toBeDefined();
        expect(votacao.proposicao?.id).toBeDefined();
        expect(votacao.proposicao?.tipo).toBeDefined();
      });
    });

    it('should have valid resultado values', () => {
      const votacoes = generateVotacoes(20);

      votacoes.forEach((votacao) => {
        expect([ResultadoVotacao.APROVADO, ResultadoVotacao.REJEITADO]).toContain(votacao.resultado);
      });
    });

    it('should have placar summing to 513 (or close)', () => {
      const votacoes = generateVotacoes(10);

      votacoes.forEach((votacao) => {
        const total = votacao.placar.votos_sim + votacao.placar.votos_nao + votacao.placar.votos_outros;
        expect(total).toBe(513);
      });
    });

    it('should have realistic placar distributions', () => {
      const votacoes = generateVotacoes(20);

      votacoes.forEach((votacao) => {
        // Not all votes should be on one side
        expect(votacao.placar.votos_sim).toBeGreaterThan(0);
        expect(votacao.placar.votos_sim).toBeLessThan(513);
      });
    });

    it('should return votação by ID', () => {
      const votacoes = generateVotacoes(20);
      const target = votacoes[5];
      const found = getVotacaoById(votacoes, target.id);

      expect(found).toEqual(target);
    });

    it('should return undefined for non-existent votação ID', () => {
      const votacoes = generateVotacoes(10);
      const found = getVotacaoById(votacoes, 999999);

      expect(found).toBeUndefined();
    });
  });

  describe('generateVotos', () => {
    it('should generate 513 votos (one per deputy)', () => {
      const votos = generateVotos(1);
      expect(votos).toHaveLength(513);
    });

    it('should have nested deputado for each voto', () => {
      const votos = generateVotos(1);

      votos.forEach((voto) => {
        expect(voto.deputado).toBeDefined();
        expect(voto.deputado?.id).toBeDefined();
        expect(voto.deputado?.nome).toBeDefined();
      });
    });

    it('should have valid TipoVoto values', () => {
      const votos = generateVotos(1);
      const validTipos = Object.values(TipoVoto);

      votos.forEach((voto) => {
        expect(validTipos).toContain(voto.voto);
      });
    });

    it('should have correct votacao_id reference', () => {
      const votacao_id = 123;
      const votos = generateVotos(votacao_id);

      votos.forEach((voto) => {
        expect(voto.votacao_id).toBe(votacao_id);
      });
    });

    it('should have unique IDs for each voto', () => {
      const votos = generateVotos(1);
      const ids = votos.map((v) => v.id);
      const uniqueIds = new Set(ids);

      expect(uniqueIds.size).toBe(ids.length);
    });

    it('should have reasonable vote type distribution', () => {
      const votos = generateVotos(1);
      const counts = countVotosByTipo(votos, 1);

      // Check that vote types are distributed reasonably
      expect(counts.sim + counts.nao).toBeGreaterThan(counts.outros);
    });
  });
});
