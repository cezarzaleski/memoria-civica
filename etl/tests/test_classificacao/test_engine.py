"""Testes para engine de classificação cívica.

Valida ClassificadorCivico com >= 3 ementas por categoria (27+ testes),
desambiguação, ementas vazias/nulas e determinismo.
"""

import time

import pytest

from src.classificacao.engine import CategoriaMatch, ClassificadorCivico
from src.classificacao.patterns import CIVIC_PATTERNS


@pytest.fixture
def classificador():
    """Fixture que retorna um ClassificadorCivico inicializado com CIVIC_PATTERNS."""
    return ClassificadorCivico(CIVIC_PATTERNS)


class TestCategoriaMatch:
    """Testes para o dataclass CategoriaMatch."""

    def test_create_with_defaults(self):
        """Test: CategoriaMatch tem confiança padrão 1.0."""
        match = CategoriaMatch(categoria_codigo="GASTOS_PUBLICOS", padrao_matchado=r"test")
        assert match.confianca == 1.0

    def test_create_with_custom_confianca(self):
        """Test: CategoriaMatch aceita confiança personalizada."""
        match = CategoriaMatch(categoria_codigo="GASTOS_PUBLICOS", padrao_matchado=r"test", confianca=0.8)
        assert match.confianca == 0.8


class TestClassificadorGastosPublicos:
    """Testes para classificação na categoria GASTOS_PUBLICOS."""

    def test_credito_suplementar(self, classificador):
        """Test: ementa sobre crédito suplementar classifica como GASTOS_PUBLICOS."""
        matches = classificador.classificar("Abre crédito suplementar ao Orçamento da União")
        codigos = [m.categoria_codigo for m in matches]
        assert "GASTOS_PUBLICOS" in codigos

    def test_precatorios(self, classificador):
        """Test: ementa sobre precatórios classifica como GASTOS_PUBLICOS."""
        matches = classificador.classificar("Dispõe sobre o pagamento de precatórios federais")
        codigos = [m.categoria_codigo for m in matches]
        assert "GASTOS_PUBLICOS" in codigos

    def test_responsabilidade_fiscal(self, classificador):
        """Test: ementa sobre responsabilidade fiscal classifica como GASTOS_PUBLICOS."""
        matches = classificador.classificar("Altera a Lei de Responsabilidade Fiscal")
        codigos = [m.categoria_codigo for m in matches]
        assert "GASTOS_PUBLICOS" in codigos


class TestClassificadorTributacaoAumento:
    """Testes para classificação na categoria TRIBUTACAO_AUMENTO."""

    def test_aumento_imposto(self, classificador):
        """Test: ementa sobre aumento de imposto classifica como TRIBUTACAO_AUMENTO."""
        matches = classificador.classificar("Aumenta a alíquota do imposto sobre importação")
        codigos = [m.categoria_codigo for m in matches]
        assert "TRIBUTACAO_AUMENTO" in codigos

    def test_majoracao_tributo(self, classificador):
        """Test: ementa sobre majoração de tributo classifica como TRIBUTACAO_AUMENTO."""
        matches = classificador.classificar("Dispõe sobre a majoração de tributos federais")
        codigos = [m.categoria_codigo for m in matches]
        assert "TRIBUTACAO_AUMENTO" in codigos

    def test_criacao_contribuicao(self, classificador):
        """Test: ementa sobre criação de contribuição classifica como TRIBUTACAO_AUMENTO."""
        matches = classificador.classificar("Cria contribuição social sobre grandes fortunas")
        codigos = [m.categoria_codigo for m in matches]
        assert "TRIBUTACAO_AUMENTO" in codigos


class TestClassificadorTributacaoIsencao:
    """Testes para classificação na categoria TRIBUTACAO_ISENCAO."""

    def test_isencao_tributaria(self, classificador):
        """Test: ementa sobre isenção tributária classifica como TRIBUTACAO_ISENCAO."""
        matches = classificador.classificar("Concede isenção tributária para micro e pequenas empresas")
        codigos = [m.categoria_codigo for m in matches]
        assert "TRIBUTACAO_ISENCAO" in codigos

    def test_desoneracão(self, classificador):
        """Test: ementa sobre desoneração classifica como TRIBUTACAO_ISENCAO."""
        matches = classificador.classificar("Estende a desoneração da folha de pagamento")
        codigos = [m.categoria_codigo for m in matches]
        assert "TRIBUTACAO_ISENCAO" in codigos

    def test_incentivo_fiscal(self, classificador):
        """Test: ementa sobre incentivo fiscal classifica como TRIBUTACAO_ISENCAO."""
        matches = classificador.classificar("Prorroga o incentivo fiscal para a Zona Franca de Manaus")
        codigos = [m.categoria_codigo for m in matches]
        assert "TRIBUTACAO_ISENCAO" in codigos


class TestClassificadorBeneficiosCategorias:
    """Testes para classificação na categoria BENEFICIOS_CATEGORIAS."""

    def test_servidor_publico(self, classificador):
        """Test: ementa sobre servidores públicos classifica como BENEFICIOS_CATEGORIAS."""
        matches = classificador.classificar("Reajuste salarial para servidores públicos federais")
        codigos = [m.categoria_codigo for m in matches]
        assert "BENEFICIOS_CATEGORIAS" in codigos

    def test_piso_salarial(self, classificador):
        """Test: ementa sobre piso salarial classifica como BENEFICIOS_CATEGORIAS."""
        matches = classificador.classificar("Institui piso salarial nacional para enfermeiros")
        codigos = [m.categoria_codigo for m in matches]
        assert "BENEFICIOS_CATEGORIAS" in codigos

    def test_aposentadoria_militar(self, classificador):
        """Test: ementa sobre aposentadoria de militar classifica como BENEFICIOS_CATEGORIAS."""
        matches = classificador.classificar("Altera regras de aposentadoria dos militares das Forças Armadas")
        codigos = [m.categoria_codigo for m in matches]
        assert "BENEFICIOS_CATEGORIAS" in codigos


class TestClassificadorDireitosSociais:
    """Testes para classificação na categoria DIREITOS_SOCIAIS."""

    def test_saude_publica(self, classificador):
        """Test: ementa sobre saúde pública classifica como DIREITOS_SOCIAIS."""
        matches = classificador.classificar("Amplia o investimento em saúde pública")
        codigos = [m.categoria_codigo for m in matches]
        assert "DIREITOS_SOCIAIS" in codigos

    def test_sus(self, classificador):
        """Test: ementa sobre SUS classifica como DIREITOS_SOCIAIS."""
        matches = classificador.classificar("Dispõe sobre o financiamento do SUS")
        codigos = [m.categoria_codigo for m in matches]
        assert "DIREITOS_SOCIAIS" in codigos

    def test_salario_minimo(self, classificador):
        """Test: ementa sobre salário mínimo classifica como DIREITOS_SOCIAIS."""
        matches = classificador.classificar("Política de valorização do salário-mínimo")
        codigos = [m.categoria_codigo for m in matches]
        assert "DIREITOS_SOCIAIS" in codigos


class TestClassificadorSegurancaJustica:
    """Testes para classificação na categoria SEGURANCA_JUSTICA."""

    def test_codigo_penal(self, classificador):
        """Test: ementa sobre código penal classifica como SEGURANCA_JUSTICA."""
        matches = classificador.classificar("Altera o Código Penal para tipificar novos crimes")
        codigos = [m.categoria_codigo for m in matches]
        assert "SEGURANCA_JUSTICA" in codigos

    def test_seguranca_publica(self, classificador):
        """Test: ementa sobre segurança pública classifica como SEGURANCA_JUSTICA."""
        matches = classificador.classificar("Plano Nacional de Segurança Pública")
        codigos = [m.categoria_codigo for m in matches]
        assert "SEGURANCA_JUSTICA" in codigos

    def test_arma_de_fogo(self, classificador):
        """Test: ementa sobre arma de fogo classifica como SEGURANCA_JUSTICA."""
        matches = classificador.classificar("Regulamenta a posse e porte de armas de fogo")
        codigos = [m.categoria_codigo for m in matches]
        assert "SEGURANCA_JUSTICA" in codigos


class TestClassificadorMeioAmbiente:
    """Testes para classificação na categoria MEIO_AMBIENTE."""

    def test_meio_ambiente(self, classificador):
        """Test: ementa sobre meio ambiente classifica como MEIO_AMBIENTE."""
        matches = classificador.classificar("Dispõe sobre a proteção do meio ambiente")
        codigos = [m.categoria_codigo for m in matches]
        assert "MEIO_AMBIENTE" in codigos

    def test_licenciamento_ambiental(self, classificador):
        """Test: ementa sobre licenciamento ambiental classifica como MEIO_AMBIENTE."""
        matches = classificador.classificar("Simplifica o licenciamento ambiental de obras")
        codigos = [m.categoria_codigo for m in matches]
        assert "MEIO_AMBIENTE" in codigos

    def test_energia_renovavel(self, classificador):
        """Test: ementa sobre energia renovável classifica como MEIO_AMBIENTE."""
        matches = classificador.classificar("Incentiva a geração de energia renovável")
        codigos = [m.categoria_codigo for m in matches]
        assert "MEIO_AMBIENTE" in codigos


class TestClassificadorRegulacaoEconomica:
    """Testes para classificação na categoria REGULACAO_ECONOMICA."""

    def test_banco_central(self, classificador):
        """Test: ementa sobre Banco Central classifica como REGULACAO_ECONOMICA."""
        matches = classificador.classificar("Dispõe sobre a autonomia do Banco Central")
        codigos = [m.categoria_codigo for m in matches]
        assert "REGULACAO_ECONOMICA" in codigos

    def test_privatizacao(self, classificador):
        """Test: ementa sobre privatização classifica como REGULACAO_ECONOMICA."""
        matches = classificador.classificar("Autoriza a privatização de empresas estatais")
        codigos = [m.categoria_codigo for m in matches]
        assert "REGULACAO_ECONOMICA" in codigos

    def test_marco_regulatorio(self, classificador):
        """Test: ementa sobre marco regulatório classifica como REGULACAO_ECONOMICA."""
        matches = classificador.classificar("Institui o novo marco regulatório de saneamento básico")
        codigos = [m.categoria_codigo for m in matches]
        assert "REGULACAO_ECONOMICA" in codigos


class TestClassificadorPoliticaInstitucional:
    """Testes para classificação na categoria POLITICA_INSTITUCIONAL."""

    def test_cpi(self, classificador):
        """Test: ementa sobre CPI classifica como POLITICA_INSTITUCIONAL."""
        matches = classificador.classificar("Cria CPI para investigar irregularidades")
        codigos = [m.categoria_codigo for m in matches]
        assert "POLITICA_INSTITUCIONAL" in codigos

    def test_reforma_eleitoral(self, classificador):
        """Test: ementa sobre reforma eleitoral classifica como POLITICA_INSTITUCIONAL."""
        matches = classificador.classificar("Altera as regras da reforma eleitoral")
        codigos = [m.categoria_codigo for m in matches]
        assert "POLITICA_INSTITUCIONAL" in codigos

    def test_fundo_partidario(self, classificador):
        """Test: ementa sobre fundo partidário classifica como POLITICA_INSTITUCIONAL."""
        matches = classificador.classificar("Regulamenta a distribuição do fundo partidário")
        codigos = [m.categoria_codigo for m in matches]
        assert "POLITICA_INSTITUCIONAL" in codigos


class TestDesambiguacao:
    """Testes para regras de desambiguação."""

    def test_aposentadoria_servidor_vs_social(self, classificador):
        """Test: 'aposentadoria de servidor público' prioriza BENEFICIOS_CATEGORIAS sobre DIREITOS_SOCIAIS."""
        matches = classificador.classificar(
            "Altera regras de aposentadoria de servidor público da previdência social"
        )
        codigos = [m.categoria_codigo for m in matches]
        assert "BENEFICIOS_CATEGORIAS" in codigos
        assert "DIREITOS_SOCIAIS" not in codigos

    def test_previdencia_social_generica(self, classificador):
        """Test: 'previdência social' sem categoria específica classifica como DIREITOS_SOCIAIS."""
        matches = classificador.classificar("Reforma da previdência social para todos os trabalhadores")
        codigos = [m.categoria_codigo for m in matches]
        assert "DIREITOS_SOCIAIS" in codigos

    def test_isencao_vs_aumento(self, classificador):
        """Test: 'isenção tributária' com menção a aumento prioriza TRIBUTACAO_ISENCAO."""
        matches = classificador.classificar(
            "Cria contribuição social com isenção tributária para microempresas"
        )
        codigos = [m.categoria_codigo for m in matches]
        assert "TRIBUTACAO_ISENCAO" in codigos
        assert "TRIBUTACAO_AUMENTO" not in codigos


class TestEdgeCases:
    """Testes para casos limite."""

    def test_ementa_vazia(self, classificador):
        """Test: ementa vazia retorna lista vazia."""
        matches = classificador.classificar("")
        assert matches == []

    def test_ementa_none_like(self, classificador):
        """Test: ementa None-like (string vazia) retorna lista vazia."""
        matches = classificador.classificar("")
        assert matches == []

    def test_ementa_sem_match(self, classificador):
        """Test: ementa sem match retorna lista vazia."""
        matches = classificador.classificar("Homenagem ao dia do professor")
        assert matches == []

    def test_determinismo(self, classificador):
        """Test: mesma ementa sempre produz mesmo resultado."""
        ementa = "Abre crédito suplementar ao Orçamento Geral da União"
        result1 = classificador.classificar(ementa)
        result2 = classificador.classificar(ementa)
        assert len(result1) == len(result2)
        assert [m.categoria_codigo for m in result1] == [m.categoria_codigo for m in result2]
        assert [m.padrao_matchado for m in result1] == [m.padrao_matchado for m in result2]

    def test_multiplas_categorias(self, classificador):
        """Test: ementa que toca múltiplas categorias retorna múltiplos matches."""
        matches = classificador.classificar(
            "Dispõe sobre segurança pública com medidas de proteção do meio ambiente"
        )
        codigos = [m.categoria_codigo for m in matches]
        assert "SEGURANCA_JUSTICA" in codigos
        assert "MEIO_AMBIENTE" in codigos

    def test_case_insensitive(self, classificador):
        """Test: classificação é case-insensitive."""
        matches_lower = classificador.classificar("crédito suplementar ao orçamento")
        matches_upper = classificador.classificar("CRÉDITO SUPLEMENTAR AO ORÇAMENTO")
        assert len(matches_lower) > 0
        assert len(matches_upper) > 0
        assert [m.categoria_codigo for m in matches_lower] == [m.categoria_codigo for m in matches_upper]

    def test_keywords_ajuda_classificacao(self, classificador):
        """Test: keywords adicionais ajudam na classificação."""
        matches_sem = classificador.classificar("Projeto de Lei 123/2024")
        matches_com = classificador.classificar("Projeto de Lei 123/2024", keywords="meio ambiente sustentabilidade")
        codigos_sem = [m.categoria_codigo for m in matches_sem]
        codigos_com = [m.categoria_codigo for m in matches_com]
        assert "MEIO_AMBIENTE" not in codigos_sem
        assert "MEIO_AMBIENTE" in codigos_com

    def test_nao_duplica_categoria(self, classificador):
        """Test: mesma categoria não aparece mais de uma vez."""
        matches = classificador.classificar(
            "Abre crédito suplementar e crédito especial ao orçamento público com dotação orçamentária"
        )
        codigos = [m.categoria_codigo for m in matches]
        assert codigos.count("GASTOS_PUBLICOS") == 1


class TestClassificadorPatternInvalido:
    """Testes para comportamento com padrões inválidos."""

    def test_padrao_invalido_ignorado(self):
        """Test: padrão regex inválido é ignorado sem exceção."""
        patterns = {
            "GASTOS_PUBLICOS": [r"cr[ée]dito\s+suplementar", r"[invalid"],
        }
        classificador = ClassificadorCivico(patterns)
        matches = classificador.classificar("Abre crédito suplementar")
        codigos = [m.categoria_codigo for m in matches]
        assert "GASTOS_PUBLICOS" in codigos

    def test_categorias_sem_padroes(self):
        """Test: categoria com lista vazia é aceita sem erros."""
        patterns = {
            "VAZIA": [],
            "GASTOS_PUBLICOS": [r"cr[ée]dito\s+suplementar"],
        }
        classificador = ClassificadorCivico(patterns)
        matches = classificador.classificar("Abre crédito suplementar")
        codigos = [m.categoria_codigo for m in matches]
        assert "GASTOS_PUBLICOS" in codigos
        assert "VAZIA" not in codigos


class TestPerformance:
    """Testes de performance do classificador."""

    def test_5000_ementas_under_5_seconds(self, classificador):
        """Test: classificação de 5000 ementas completa em menos de 5 segundos."""
        ementas = [
            "Abre crédito suplementar ao orçamento da união",
            "Dispõe sobre isenção tributária para microempresas",
            "Altera o Código Penal para tipificar novos crimes",
            "Proteção do meio ambiente e licenciamento ambiental",
            "Dispõe sobre a autonomia do Banco Central",
            "Homenagem ao dia do professor",
            "Altera regras de aposentadoria dos servidores públicos",
            "Política de valorização do salário-mínimo",
            "Cria CPI para investigar irregularidades",
            "Regulamenta a posse e porte de armas de fogo",
        ] * 500  # 5000 ementas

        start = time.perf_counter()
        for ementa in ementas:
            classificador.classificar(ementa)
        elapsed = time.perf_counter() - start

        assert elapsed < 5.0, f"Classificação de 5000 ementas levou {elapsed:.2f}s (limite: 5s)"
