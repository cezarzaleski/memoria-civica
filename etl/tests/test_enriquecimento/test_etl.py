"""Testes unitários para o pipeline ETL de enriquecimento LLM.

Todos os testes usam mocked LLMClient e SQLite in-memory.
"""

import logging
from unittest.mock import MagicMock, patch

from sqlalchemy import select

from src.classificacao.models import CategoriaCivica, ProposicaoCategoria
from src.enriquecimento.etl import run_enriquecimento_etl
from src.enriquecimento.models import EnriquecimentoLLM
from src.enriquecimento.prompts import PROMPT_VERSION
from src.proposicoes.models import Proposicao
from src.shared.llm_client import EnriquecimentoOutput, LLMResult


def _make_proposicao(db_session, *, id_: int, tipo: str = "PL", numero: int = 100, ano: int = 2024, ementa: str = "Ementa teste"):
    """Helper para criar proposição no banco de teste."""
    prop = Proposicao(id=id_, tipo=tipo, numero=numero, ano=ano, ementa=ementa)
    db_session.add(prop)
    db_session.commit()
    return prop


def _make_llm_result(*, confianca: float = 0.8, tokens_input: int = 100, tokens_output: int = 50):
    """Helper para criar LLMResult padrão."""
    output = EnriquecimentoOutput(
        headline="Título acessível da proposição",
        resumo_simples="Resumo simples para o cidadão",
        impacto_cidadao=["Impacto 1", "Impacto 2"],
        confianca=confianca,
    )
    return LLMResult(output=output, tokens_input=tokens_input, tokens_output=tokens_output)


def _make_categoria(db_session, *, codigo: str = "GASTOS_PUBLICOS", nome: str = "Gastos Públicos"):
    """Helper para criar categoria cívica no banco de teste."""
    cat = CategoriaCivica(codigo=codigo, nome=nome)
    db_session.add(cat)
    db_session.commit()
    return cat


def _make_proposicao_categoria(db_session, *, proposicao_id: int, categoria_id: int, origem: str = "regra"):
    """Helper para criar vínculo proposição-categoria no banco de teste."""
    pc = ProposicaoCategoria(proposicao_id=proposicao_id, categoria_id=categoria_id, origem=origem)
    db_session.add(pc)
    db_session.commit()
    return pc


class TestSkipConditions:
    """Testes para condições de skip do pipeline."""

    @patch("src.enriquecimento.etl.settings")
    def test_skip_when_llm_disabled(self, mock_settings, db_session, caplog):
        mock_settings.LLM_ENABLED = False

        with caplog.at_level(logging.INFO):
            result = run_enriquecimento_etl(db=db_session)

        assert result == 0
        assert "LLM_ENABLED=False" in caplog.text

    @patch("src.enriquecimento.etl.settings")
    def test_skip_when_api_key_missing(self, mock_settings, db_session, caplog):
        mock_settings.LLM_ENABLED = True
        mock_settings.LLM_API_KEY = None

        with caplog.at_level(logging.WARNING):
            result = run_enriquecimento_etl(db=db_session)

        assert result == 0
        assert "LLM_API_KEY" in caplog.text

    @patch("src.enriquecimento.etl.OpenAIClient")
    @patch("src.enriquecimento.etl.settings")
    def test_returns_zero_when_no_pending(self, mock_settings, mock_client_cls, db_session, caplog):
        mock_settings.LLM_ENABLED = True
        mock_settings.LLM_API_KEY = "test-key"
        mock_settings.LLM_MODEL = "gpt-4o-mini"

        with caplog.at_level(logging.INFO):
            result = run_enriquecimento_etl(db=db_session)

        assert result == 0
        assert "Nenhuma proposição pendente" in caplog.text


class TestSuccessfulProcessing:
    """Testes para processamento bem-sucedido."""

    @patch("src.enriquecimento.etl.time.sleep")
    @patch("src.enriquecimento.etl.OpenAIClient")
    @patch("src.enriquecimento.etl.settings")
    def test_processes_single_proposition_successfully(self, mock_settings, mock_client_cls, mock_sleep, db_session):
        mock_settings.LLM_ENABLED = True
        mock_settings.LLM_API_KEY = "test-key"
        mock_settings.LLM_MODEL = "gpt-4o-mini"
        mock_settings.LLM_BATCH_SIZE = 10
        mock_settings.LLM_CONFIDENCE_THRESHOLD = 0.5

        _make_proposicao(db_session, id_=1)

        mock_client = MagicMock()
        mock_client.model = "gpt-4o-mini"
        mock_client.enriquecer_proposicao.return_value = _make_llm_result()
        mock_client_cls.return_value = mock_client

        result = run_enriquecimento_etl(db=db_session)

        assert result == 1
        mock_client.enriquecer_proposicao.assert_called_once()

        # Verificar persistência no banco
        enriquecimentos = db_session.execute(select(EnriquecimentoLLM)).scalars().all()
        assert len(enriquecimentos) == 1
        assert enriquecimentos[0].proposicao_id == 1

    @patch("src.enriquecimento.etl.time.sleep")
    @patch("src.enriquecimento.etl.OpenAIClient")
    @patch("src.enriquecimento.etl.settings")
    def test_processes_batch_of_propositions(self, mock_settings, mock_client_cls, mock_sleep, db_session):
        mock_settings.LLM_ENABLED = True
        mock_settings.LLM_API_KEY = "test-key"
        mock_settings.LLM_MODEL = "gpt-4o-mini"
        mock_settings.LLM_BATCH_SIZE = 10
        mock_settings.LLM_CONFIDENCE_THRESHOLD = 0.5

        for i in range(5):
            _make_proposicao(db_session, id_=i + 1, numero=100 + i)

        mock_client = MagicMock()
        mock_client.model = "gpt-4o-mini"
        mock_client.enriquecer_proposicao.return_value = _make_llm_result()
        mock_client_cls.return_value = mock_client

        result = run_enriquecimento_etl(db=db_session)

        assert result == 5
        assert mock_client.enriquecer_proposicao.call_count == 5

    @patch("src.enriquecimento.etl.time.sleep")
    @patch("src.enriquecimento.etl.OpenAIClient")
    @patch("src.enriquecimento.etl.settings")
    def test_respects_batch_size_config(self, mock_settings, mock_client_cls, mock_sleep, db_session):
        mock_settings.LLM_ENABLED = True
        mock_settings.LLM_API_KEY = "test-key"
        mock_settings.LLM_MODEL = "gpt-4o-mini"
        mock_settings.LLM_BATCH_SIZE = 2
        mock_settings.LLM_CONFIDENCE_THRESHOLD = 0.5

        for i in range(5):
            _make_proposicao(db_session, id_=i + 1, numero=100 + i)

        mock_client = MagicMock()
        mock_client.model = "gpt-4o-mini"
        mock_client.enriquecer_proposicao.return_value = _make_llm_result()
        mock_client_cls.return_value = mock_client

        result = run_enriquecimento_etl(db=db_session)

        assert result == 5
        assert mock_client.enriquecer_proposicao.call_count == 5

    @patch("src.enriquecimento.etl.time.sleep")
    @patch("src.enriquecimento.etl.OpenAIClient")
    @patch("src.enriquecimento.etl.settings")
    def test_does_not_reprocess_already_enriched(self, mock_settings, mock_client_cls, mock_sleep, db_session):
        mock_settings.LLM_ENABLED = True
        mock_settings.LLM_API_KEY = "test-key"
        mock_settings.LLM_MODEL = "gpt-4o-mini"
        mock_settings.LLM_BATCH_SIZE = 10
        mock_settings.LLM_CONFIDENCE_THRESHOLD = 0.5

        _make_proposicao(db_session, id_=1)
        _make_proposicao(db_session, id_=2, numero=200)

        # Proposição 1 já enriquecida na versão atual
        existing = EnriquecimentoLLM(
            proposicao_id=1,
            modelo="gpt-4o-mini",
            versao_prompt=PROMPT_VERSION,
            headline="Já existente",
            resumo_simples="Já existente",
            impacto_cidadao="[]",
            confianca=0.9,
        )
        db_session.add(existing)
        db_session.commit()

        mock_client = MagicMock()
        mock_client.model = "gpt-4o-mini"
        mock_client.enriquecer_proposicao.return_value = _make_llm_result()
        mock_client_cls.return_value = mock_client

        result = run_enriquecimento_etl(db=db_session)

        # Apenas proposição 2 deve ser processada
        assert result == 1
        assert mock_client.enriquecer_proposicao.call_count == 1


class TestErrorHandling:
    """Testes para tratamento de erros por proposição."""

    @patch("src.enriquecimento.etl.time.sleep")
    @patch("src.enriquecimento.etl.OpenAIClient")
    @patch("src.enriquecimento.etl.settings")
    def test_skips_proposition_on_llm_value_error(self, mock_settings, mock_client_cls, mock_sleep, db_session, caplog):
        mock_settings.LLM_ENABLED = True
        mock_settings.LLM_API_KEY = "test-key"
        mock_settings.LLM_MODEL = "gpt-4o-mini"
        mock_settings.LLM_BATCH_SIZE = 10
        mock_settings.LLM_CONFIDENCE_THRESHOLD = 0.5

        _make_proposicao(db_session, id_=1)
        _make_proposicao(db_session, id_=2, numero=200)

        mock_client = MagicMock()
        mock_client.model = "gpt-4o-mini"
        mock_client.enriquecer_proposicao.side_effect = [
            ValueError("JSON inválido"),
            _make_llm_result(),
        ]
        mock_client_cls.return_value = mock_client

        with caplog.at_level(logging.WARNING):
            result = run_enriquecimento_etl(db=db_session)

        assert result == 1
        assert "ValueError" in caplog.text

    @patch("src.enriquecimento.etl.time.sleep")
    @patch("src.enriquecimento.etl.OpenAIClient")
    @patch("src.enriquecimento.etl.settings")
    def test_skips_proposition_on_generic_exception(self, mock_settings, mock_client_cls, mock_sleep, db_session, caplog):
        mock_settings.LLM_ENABLED = True
        mock_settings.LLM_API_KEY = "test-key"
        mock_settings.LLM_MODEL = "gpt-4o-mini"
        mock_settings.LLM_BATCH_SIZE = 10
        mock_settings.LLM_CONFIDENCE_THRESHOLD = 0.5

        _make_proposicao(db_session, id_=1)

        mock_client = MagicMock()
        mock_client.model = "gpt-4o-mini"
        mock_client.enriquecer_proposicao.side_effect = RuntimeError("Erro inesperado")
        mock_client_cls.return_value = mock_client

        with caplog.at_level(logging.WARNING):
            result = run_enriquecimento_etl(db=db_session)

        assert result == 0
        assert "RuntimeError" in caplog.text


class TestCategoryLookup:
    """Testes para busca de categorias regex existentes."""

    @patch("src.enriquecimento.etl.time.sleep")
    @patch("src.enriquecimento.etl.OpenAIClient")
    @patch("src.enriquecimento.etl.settings")
    def test_passes_regex_categories_to_llm(self, mock_settings, mock_client_cls, mock_sleep, db_session):
        mock_settings.LLM_ENABLED = True
        mock_settings.LLM_API_KEY = "test-key"
        mock_settings.LLM_MODEL = "gpt-4o-mini"
        mock_settings.LLM_BATCH_SIZE = 10
        mock_settings.LLM_CONFIDENCE_THRESHOLD = 0.5

        prop = _make_proposicao(db_session, id_=1)
        cat = _make_categoria(db_session, codigo="GASTOS_PUBLICOS")
        _make_proposicao_categoria(db_session, proposicao_id=prop.id, categoria_id=cat.id)

        mock_client = MagicMock()
        mock_client.model = "gpt-4o-mini"
        mock_client.enriquecer_proposicao.return_value = _make_llm_result()
        mock_client_cls.return_value = mock_client

        run_enriquecimento_etl(db=db_session)

        call_kwargs = mock_client.enriquecer_proposicao.call_args
        assert call_kwargs.kwargs.get("categorias") == ["GASTOS_PUBLICOS"] or \
            (call_kwargs.args[4] if len(call_kwargs.args) > 4 else call_kwargs.kwargs.get("categorias")) == ["GASTOS_PUBLICOS"]

    @patch("src.enriquecimento.etl.time.sleep")
    @patch("src.enriquecimento.etl.OpenAIClient")
    @patch("src.enriquecimento.etl.settings")
    def test_passes_none_categories_when_no_regex_match(self, mock_settings, mock_client_cls, mock_sleep, db_session):
        mock_settings.LLM_ENABLED = True
        mock_settings.LLM_API_KEY = "test-key"
        mock_settings.LLM_MODEL = "gpt-4o-mini"
        mock_settings.LLM_BATCH_SIZE = 10
        mock_settings.LLM_CONFIDENCE_THRESHOLD = 0.5

        _make_proposicao(db_session, id_=1)

        mock_client = MagicMock()
        mock_client.model = "gpt-4o-mini"
        mock_client.enriquecer_proposicao.return_value = _make_llm_result()
        mock_client_cls.return_value = mock_client

        run_enriquecimento_etl(db=db_session)

        call_kwargs = mock_client.enriquecer_proposicao.call_args
        categorias_arg = call_kwargs.kwargs.get("categorias")
        assert categorias_arg is None


class TestUpsertParameters:
    """Testes para parâmetros corretos no upsert."""

    @patch("src.enriquecimento.etl.time.sleep")
    @patch("src.enriquecimento.etl.OpenAIClient")
    @patch("src.enriquecimento.etl.settings")
    def test_upsert_called_with_correct_parameters(self, mock_settings, mock_client_cls, mock_sleep, db_session):
        mock_settings.LLM_ENABLED = True
        mock_settings.LLM_API_KEY = "test-key"
        mock_settings.LLM_MODEL = "gpt-4o-mini"
        mock_settings.LLM_BATCH_SIZE = 10
        mock_settings.LLM_CONFIDENCE_THRESHOLD = 0.5

        _make_proposicao(db_session, id_=42)

        llm_result = _make_llm_result(tokens_input=150, tokens_output=80)
        mock_client = MagicMock()
        mock_client.model = "gpt-4o-mini"
        mock_client.enriquecer_proposicao.return_value = llm_result
        mock_client_cls.return_value = mock_client

        run_enriquecimento_etl(db=db_session)

        # Verificar que o resultado foi persistido corretamente
        enriquecimento = db_session.execute(
            select(EnriquecimentoLLM).where(EnriquecimentoLLM.proposicao_id == 42)
        ).scalar_one()

        assert enriquecimento.proposicao_id == 42
        assert enriquecimento.modelo == "gpt-4o-mini"
        assert enriquecimento.versao_prompt == PROMPT_VERSION
        assert enriquecimento.tokens_input == 150
        assert enriquecimento.tokens_output == 80
        assert enriquecimento.headline == "Título acessível da proposição"

    @patch("src.enriquecimento.etl.time.sleep")
    @patch("src.enriquecimento.etl.OpenAIClient")
    @patch("src.enriquecimento.etl.settings")
    def test_confidence_threshold_passed_to_upsert(self, mock_settings, mock_client_cls, mock_sleep, db_session):
        mock_settings.LLM_ENABLED = True
        mock_settings.LLM_API_KEY = "test-key"
        mock_settings.LLM_MODEL = "gpt-4o-mini"
        mock_settings.LLM_BATCH_SIZE = 10
        mock_settings.LLM_CONFIDENCE_THRESHOLD = 0.7

        _make_proposicao(db_session, id_=1)

        # Confiança 0.6 < threshold 0.7 → necessita_revisao = True
        llm_result = _make_llm_result(confianca=0.6)
        mock_client = MagicMock()
        mock_client.model = "gpt-4o-mini"
        mock_client.enriquecer_proposicao.return_value = llm_result
        mock_client_cls.return_value = mock_client

        run_enriquecimento_etl(db=db_session)

        enriquecimento = db_session.execute(
            select(EnriquecimentoLLM).where(EnriquecimentoLLM.proposicao_id == 1)
        ).scalar_one()

        assert enriquecimento.necessita_revisao is True
        assert enriquecimento.confianca == 0.6


class TestSummaryLogging:
    """Testes para logging de resumo."""

    @patch("src.enriquecimento.etl.time.sleep")
    @patch("src.enriquecimento.etl.OpenAIClient")
    @patch("src.enriquecimento.etl.settings")
    def test_logs_summary_with_totals(self, mock_settings, mock_client_cls, mock_sleep, db_session, caplog):
        mock_settings.LLM_ENABLED = True
        mock_settings.LLM_API_KEY = "test-key"
        mock_settings.LLM_MODEL = "gpt-4o-mini"
        mock_settings.LLM_BATCH_SIZE = 10
        mock_settings.LLM_CONFIDENCE_THRESHOLD = 0.5

        _make_proposicao(db_session, id_=1)
        _make_proposicao(db_session, id_=2, numero=200)

        mock_client = MagicMock()
        mock_client.model = "gpt-4o-mini"
        mock_client.enriquecer_proposicao.side_effect = [
            _make_llm_result(tokens_input=100, tokens_output=50),
            ValueError("Erro"),
        ]
        mock_client_cls.return_value = mock_client

        with caplog.at_level(logging.INFO):
            run_enriquecimento_etl(db=db_session)

        assert "pendentes=2" in caplog.text
        assert "processados=1" in caplog.text
        assert "erros=1" in caplog.text
        assert "tokens_input=100" in caplog.text
        assert "tokens_output=50" in caplog.text


class TestRateLimitDelay:
    """Testes para delay entre chamadas LLM."""

    @patch("src.enriquecimento.etl.time.sleep")
    @patch("src.enriquecimento.etl.OpenAIClient")
    @patch("src.enriquecimento.etl.settings")
    def test_rate_limit_delay_between_calls(self, mock_settings, mock_client_cls, mock_sleep, db_session):
        mock_settings.LLM_ENABLED = True
        mock_settings.LLM_API_KEY = "test-key"
        mock_settings.LLM_MODEL = "gpt-4o-mini"
        mock_settings.LLM_BATCH_SIZE = 10
        mock_settings.LLM_CONFIDENCE_THRESHOLD = 0.5

        _make_proposicao(db_session, id_=1)
        _make_proposicao(db_session, id_=2, numero=200)

        mock_client = MagicMock()
        mock_client.model = "gpt-4o-mini"
        mock_client.enriquecer_proposicao.return_value = _make_llm_result()
        mock_client_cls.return_value = mock_client

        run_enriquecimento_etl(db=db_session)

        # Deve haver pelo menos 1 sleep(0.5) entre as 2 chamadas
        mock_sleep.assert_called_with(0.5)
        assert mock_sleep.call_count >= 1
