import { describe, expect, it } from 'vitest';
import { TipoProposicao, ResultadoVotacao, TipoVoto } from '@/lib/types';
import {
  DEPUTADOS_FIXTURES,
  filterDeputadosByNome,
  filterDeputadosByPartido,
  filterDeputadosByUF,
  generateDeputados,
  getDeputadoById,
} from '@/mocks/data/deputados';
import { CATEGORIAS_CIVICAS_FIXTURES, getCategoriaCivicaById } from '@/mocks/data/categorias-civicas';
import { ORIENTACOES_FIXTURES, getOrientacoesByVotacaoId } from '@/mocks/data/orientacoes';
import { PROPOSICOES_CATEGORIAS_FIXTURES, getCategoriasByProposicaoId } from '@/mocks/data/proposicoes-categorias';
import { PROPOSICOES_FIXTURES, generateProposicoes, getProposicaoById } from '@/mocks/data/proposicoes';
import { VOTACOES_PROPOSICOES_FIXTURES, getProposicoesByVotacaoId } from '@/mocks/data/votacoes-proposicoes';
import { VOTACOES_FIXTURES, generateVotacoes, getVotacaoById } from '@/mocks/data/votacoes';
import { buildPlacarFromVotacao, countVotosByTipo, generateVotos, getVotoById } from '@/mocks/data/votos';

describe('Mock data legislativo brasileiro', () => {
  describe('volumes mínimos para paginação e filtros', () => {
    it('deve manter massa crítica de registros no domínio', () => {
      expect(DEPUTADOS_FIXTURES.length).toBeGreaterThanOrEqual(513);
      expect(PROPOSICOES_FIXTURES.length).toBeGreaterThanOrEqual(50);
      expect(VOTACOES_FIXTURES.length).toBeGreaterThanOrEqual(50);
      expect(CATEGORIAS_CIVICAS_FIXTURES.length).toBeGreaterThanOrEqual(5);
      expect(ORIENTACOES_FIXTURES.length).toBeGreaterThanOrEqual(200);
      expect(PROPOSICOES_CATEGORIAS_FIXTURES.length).toBeGreaterThanOrEqual(60);
      expect(VOTACOES_PROPOSICOES_FIXTURES.length).toBeGreaterThanOrEqual(50);
    });
  });

  describe('deputados', () => {
    it('deve gerar 513 deputados por padrão e manter IDs únicos numéricos', () => {
      const deputados = generateDeputados();
      const ids = deputados.map((deputado) => deputado.id);

      expect(deputados).toHaveLength(513);
      expect(new Set(ids).size).toBe(ids.length);
      expect(ids.every((id) => Number.isInteger(id) && id > 0)).toBe(true);
    });

    it('deve retornar array vazio para count inválido ou negativo', () => {
      expect(generateDeputados(-10)).toEqual([]);
      expect(generateDeputados(Number.NaN)).toEqual([]);
    });

    it('deve conter siglas partidárias e UFs representativas do contexto brasileiro', () => {
      const deputados = generateDeputados(80);
      const ufsValidas = new Set([
        'AC',
        'AL',
        'AP',
        'AM',
        'BA',
        'CE',
        'DF',
        'ES',
        'GO',
        'MA',
        'MT',
        'MS',
        'MG',
        'PA',
        'PB',
        'PR',
        'PE',
        'PI',
        'RJ',
        'RN',
        'RS',
        'RO',
        'RR',
        'SC',
        'SP',
        'SE',
        'TO',
      ]);

      expect(deputados.some((deputado) => deputado.sigla_partido === 'PT')).toBe(true);
      expect(deputados.some((deputado) => deputado.sigla_partido === 'PL')).toBe(true);
      expect(deputados.some((deputado) => deputado.sigla_partido === 'MDB')).toBe(true);
      expect(deputados.every((deputado) => ufsValidas.has(deputado.uf))).toBe(true);
    });

    it('deve manter filtros utilitários funcionais', () => {
      const deputados = generateDeputados(120);

      const porNome = filterDeputadosByNome(deputados, 'João');
      const partidoAlvo = deputados[5]?.sigla_partido;
      const porPartido = partidoAlvo ? filterDeputadosByPartido(deputados, partidoAlvo) : [];
      const porUF = filterDeputadosByUF(deputados, 'SP');

      expect(porNome.every((deputado) => deputado.nome.toLowerCase().includes('joão'))).toBe(true);
      expect(porPartido.every((deputado) => deputado.sigla_partido === partidoAlvo)).toBe(true);
      expect(porUF.every((deputado) => deputado.uf === 'SP')).toBe(true);

      const deputado = deputados[10];
      expect(deputado).toBeDefined();
      expect(getDeputadoById(deputados, deputado?.id ?? -1)).toEqual(deputado);
    });
  });

  describe('proposições', () => {
    it('deve produzir proposições com shape canônico e tipos válidos', () => {
      const proposicoes = generateProposicoes(50);
      const tiposCanonicos = new Set(Object.values(TipoProposicao));

      expect(proposicoes).toHaveLength(50);
      proposicoes.forEach((proposicao) => {
        expect(Number.isInteger(proposicao.id)).toBe(true);
        expect(typeof proposicao.tipo).toBe('string');
        expect(proposicao.tipo.length).toBeGreaterThan(1);
        expect(Number.isInteger(proposicao.numero)).toBe(true);
        expect(Number.isInteger(proposicao.ano)).toBe(true);
        expect(proposicao.ementa.toLowerCase()).toContain('dispõe sobre');
        expect(proposicao.data_apresentacao).toContain('T');
      });

      expect(
        proposicoes.some((proposicao) =>
          tiposCanonicos.has(proposicao.tipo as (typeof TipoProposicao)[keyof typeof TipoProposicao])
        )
      ).toBe(true);
    });

    it('deve retornar array vazio para count inválido ou negativo', () => {
      expect(generateProposicoes(-3)).toEqual([]);
      expect(generateProposicoes(Number.POSITIVE_INFINITY)).toEqual([]);
    });

    it('deve cobrir campos opcionais e fallbacks de contrato', () => {
      expect(PROPOSICOES_FIXTURES.some((proposicao) => proposicao.autor_id === undefined)).toBe(true);
      expect(PROPOSICOES_FIXTURES.some((proposicao) => proposicao.autor_id !== undefined)).toBe(true);
      expect(PROPOSICOES_FIXTURES.some((proposicao) => proposicao.ementa_simplificada === undefined)).toBe(true);
      expect(PROPOSICOES_FIXTURES.some((proposicao) => proposicao.ementa_simplificada !== undefined)).toBe(true);

      const alvo = PROPOSICOES_FIXTURES[20];
      expect(alvo).toBeDefined();
      expect(getProposicaoById(PROPOSICOES_FIXTURES, alvo?.id ?? -1)).toEqual(alvo);
    });
  });

  describe('votações e votos', () => {
    it('deve manter votações ordenadas e placar consistente com o total da Câmara', () => {
      const votacoes = generateVotacoes(50);

      for (let index = 0; index < votacoes.length - 1; index += 1) {
        const atual = new Date(votacoes[index]?.data_hora ?? 0);
        const proxima = new Date(votacoes[index + 1]?.data_hora ?? 0);
        expect(atual.getTime()).toBeGreaterThanOrEqual(proxima.getTime());
      }

      votacoes.forEach((votacao) => {
        const total = votacao.placar.votos_sim + votacao.placar.votos_nao + votacao.placar.votos_outros;
        expect(total).toBe(513);

        if (votacao.resultado === ResultadoVotacao.APROVADO) {
          expect(votacao.placar.votos_sim).toBeGreaterThanOrEqual(votacao.placar.votos_nao);
        }

        if (votacao.resultado === ResultadoVotacao.REJEITADO) {
          expect(votacao.placar.votos_nao).toBeGreaterThan(votacao.placar.votos_sim);
        }

        if (votacao.resultado === ResultadoVotacao.APROVADO_COM_SUBSTITUTIVO) {
          expect(votacao.id % 10).toBe(0);
        }
      });
    });

    it('deve manter coerência entre votos individuais e placar agregado da votação', () => {
      const amostraIds = [1, 2, 3, 10];

      amostraIds.forEach((votacaoId) => {
        const placar = buildPlacarFromVotacao(votacaoId);
        const votacao = getVotacaoById(VOTACOES_FIXTURES, votacaoId);

        expect(votacao).toBeDefined();
        expect(votacao?.placar).toEqual(placar);
      });
    });

    it('deve garantir coerência para votações com resultado aprovado com substitutivo', () => {
      const substitutivas = VOTACOES_FIXTURES.filter(
        (votacao) => votacao.resultado === ResultadoVotacao.APROVADO_COM_SUBSTITUTIVO
      );

      expect(substitutivas.length).toBeGreaterThan(0);
      substitutivas.forEach((votacao) => {
        expect(votacao.id % 10).toBe(0);
        expect(votacao.placar.votos_sim).toBeGreaterThanOrEqual(votacao.placar.votos_nao);
      });
    });

    it('deve retornar array vazio para count inválido ou negativo', () => {
      expect(generateVotacoes(-1)).toEqual([]);
      expect(generateVotacoes(Number.NEGATIVE_INFINITY)).toEqual([]);
    });

    it('deve gerar votos válidos com deputado aninhado e utilitários de busca', () => {
      const votacaoId = 11;
      const votos = generateVotos(votacaoId);
      const validos = new Set(Object.values(TipoVoto));

      expect(votos).toHaveLength(513);
      expect(votos.every((voto) => voto.votacao_id === votacaoId)).toBe(true);
      expect(votos.every((voto) => voto.deputado?.id === voto.deputado_id)).toBe(true);
      expect(votos.every((voto) => validos.has(voto.voto))).toBe(true);

      const votoAlvo = votos[100];
      expect(votoAlvo).toBeDefined();
      expect(getVotoById(votos, votoAlvo?.id ?? -1)).toEqual(votoAlvo);

      const contagem = countVotosByTipo(votos, votacaoId);
      expect(contagem.sim + contagem.nao + contagem.outros).toBe(513);
      expect(contagem.sim + contagem.nao).toBeGreaterThan(contagem.outros);
    });
  });

  describe('novas entidades e integridade referencial', () => {
    it('deve garantir integridade entre categorias cívicas e proposições-categorias', () => {
      const idsCategorias = new Set(CATEGORIAS_CIVICAS_FIXTURES.map((categoria) => categoria.id));
      const idsProposicoes = new Set(PROPOSICOES_FIXTURES.map((proposicao) => proposicao.id));

      PROPOSICOES_CATEGORIAS_FIXTURES.forEach((relacao) => {
        expect(idsCategorias.has(relacao.categoria_id)).toBe(true);
        expect(idsProposicoes.has(relacao.proposicao_id)).toBe(true);
        expect(['manual', 'automatica']).toContain(relacao.origem);
        expect(relacao.created_at).toContain('T');

        if (relacao.origem === 'automatica') {
          expect(relacao.confianca).toBeGreaterThanOrEqual(0);
          expect(relacao.confianca).toBeLessThanOrEqual(1);
        }
      });

      const categoriasDaPrimeira = getCategoriasByProposicaoId(1);
      expect(categoriasDaPrimeira.length).toBeGreaterThan(0);
      expect(getCategoriaCivicaById(1)?.codigo).toBe('saude-publica');
      expect(getCategoriaCivicaById(9999)).toBeUndefined();
    });

    it('deve garantir integridade entre votações e proposições vinculadas', () => {
      const idsVotacoes = new Set(VOTACOES_FIXTURES.map((votacao) => votacao.id));
      const idsProposicoes = new Set(PROPOSICOES_FIXTURES.map((proposicao) => proposicao.id));

      VOTACOES_PROPOSICOES_FIXTURES.forEach((relacao) => {
        expect(idsVotacoes.has(relacao.votacao_id)).toBe(true);
        expect(idsProposicoes.has(relacao.proposicao_id)).toBe(true);
        expect(relacao.created_at).toContain('T');
      });

      const agrupadoPorVotacao = new Map<number, number>();
      const secundarios = VOTACOES_PROPOSICOES_FIXTURES.filter((item) => !item.eh_principal).length;

      VOTACOES_PROPOSICOES_FIXTURES.forEach((item) => {
        if (item.eh_principal) {
          agrupadoPorVotacao.set(item.votacao_id, (agrupadoPorVotacao.get(item.votacao_id) ?? 0) + 1);
        }
      });

      idsVotacoes.forEach((idVotacao) => {
        expect(agrupadoPorVotacao.get(idVotacao)).toBe(1);
      });

      expect(secundarios).toBeGreaterThan(0);
      expect(getProposicoesByVotacaoId(4).length).toBeGreaterThan(1);
    });

    it('deve garantir orientações por votação com valores legislativos esperados', () => {
      const idsVotacoes = new Set(VOTACOES_FIXTURES.map((votacao) => votacao.id));
      const orientacoesValidas = new Set(['Sim', 'Não', 'Liberado', 'Obstrução']);

      ORIENTACOES_FIXTURES.forEach((orientacao) => {
        expect(idsVotacoes.has(orientacao.votacao_id)).toBe(true);
        expect(orientacao.sigla_bancada.length).toBeGreaterThanOrEqual(2);
        expect(orientacoesValidas.has(orientacao.orientacao)).toBe(true);
      });

      const orientacoesVotacao1 = getOrientacoesByVotacaoId(1);
      expect(orientacoesVotacao1.length).toBe(10);
      expect(orientacoesVotacao1.some((item) => item.orientacao === 'Sim')).toBe(true);
      expect(orientacoesVotacao1.some((item) => item.orientacao === 'Não')).toBe(true);
    });
  });

  describe('edge cases de contratos opcionais e relacionamentos ausentes', () => {
    it('deve conter votações com campos opcionais ausentes sem invalidar o contrato', () => {
      expect(VOTACOES_FIXTURES.some((votacao) => votacao.sigla_orgao === undefined)).toBe(true);
      expect(VOTACOES_FIXTURES.some((votacao) => votacao.descricao === undefined)).toBe(true);
      expect(VOTACOES_FIXTURES.every((votacao) => typeof votacao.eh_nominal === 'boolean')).toBe(true);
    });

    it('deve preservar proposições sem classificação cívica para cenários de fallback', () => {
      const proposicoesClassificadas = new Set(
        PROPOSICOES_CATEGORIAS_FIXTURES.map((proposicaoCategoria) => proposicaoCategoria.proposicao_id)
      );

      const semClassificacao = PROPOSICOES_FIXTURES.filter(
        (proposicao) => !proposicoesClassificadas.has(proposicao.id)
      );

      expect(semClassificacao.length).toBeGreaterThan(0);
      expect(semClassificacao.every((proposicao) => proposicao.id > 60)).toBe(true);
    });
  });
});
