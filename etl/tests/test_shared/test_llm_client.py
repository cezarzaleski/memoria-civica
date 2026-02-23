"""Testes unitários para src/shared/llm_client.py.

Testa EnriquecimentoOutput, LLMClient abstrato e OpenAIClient com mock do SDK OpenAI.
"""

import json
from unittest.mock import MagicMock, patch

import pytest
from openai import APITimeoutError, RateLimitError
from pydantic import ValidationError

from src.shared.llm_client import EnriquecimentoOutput, LLMClient, LLMResult, OpenAIClient


# ---------------------------------------------------------------------------
# EnriquecimentoOutput
# ---------------------------------------------------------------------------
class TestEnriquecimentoOutput:
    """Testes para o schema Pydantic EnriquecimentoOutput."""

    def test_valid_data_accepted(self):
        """Dados válidos com todos os campos são aceitos."""
        output = EnriquecimentoOutput(
            headline="Projeto aumenta salário mínimo",
            resumo_simples="O projeto propõe um aumento do salário mínimo.",
            impacto_cidadao=["Aumento na renda dos trabalhadores"],
            confianca=0.85,
        )
        assert output.headline == "Projeto aumenta salário mínimo"
        assert output.confianca == 0.85

    def test_confianca_above_1_rejected(self):
        """Confiança acima de 1.0 é rejeitada."""
        with pytest.raises(ValidationError):
            EnriquecimentoOutput(
                headline="Test",
                resumo_simples="Test",
                impacto_cidadao=["Test"],
                confianca=1.5,
            )

    def test_confianca_below_0_rejected(self):
        """Confiança abaixo de 0.0 é rejeitada."""
        with pytest.raises(ValidationError):
            EnriquecimentoOutput(
                headline="Test",
                resumo_simples="Test",
                impacto_cidadao=["Test"],
                confianca=-0.1,
            )

    def test_confianca_boundary_0(self):
        """Confiança 0.0 (boundary inferior) é aceita."""
        output = EnriquecimentoOutput(
            headline="Test",
            resumo_simples="Test",
            impacto_cidadao=[],
            confianca=0.0,
        )
        assert output.confianca == 0.0

    def test_confianca_boundary_1(self):
        """Confiança 1.0 (boundary superior) é aceita."""
        output = EnriquecimentoOutput(
            headline="Test",
            resumo_simples="Test",
            impacto_cidadao=[],
            confianca=1.0,
        )
        assert output.confianca == 1.0

    def test_impacto_cidadao_must_be_list_of_strings(self):
        """impacto_cidadao deve ser lista de strings."""
        output = EnriquecimentoOutput(
            headline="Test",
            resumo_simples="Test",
            impacto_cidadao=["item1", "item2"],
            confianca=0.5,
        )
        assert output.impacto_cidadao == ["item1", "item2"]

    def test_impacto_cidadao_empty_list(self):
        """impacto_cidadao aceita lista vazia."""
        output = EnriquecimentoOutput(
            headline="Test",
            resumo_simples="Test",
            impacto_cidadao=[],
            confianca=0.5,
        )
        assert output.impacto_cidadao == []

    def test_missing_required_fields(self):
        """Campos obrigatórios faltando são rejeitados."""
        with pytest.raises(ValidationError):
            EnriquecimentoOutput()

    def test_missing_headline_rejected(self):
        """Falta de headline é rejeitada."""
        with pytest.raises(ValidationError):
            EnriquecimentoOutput(
                resumo_simples="Test",
                impacto_cidadao=["Test"],
                confianca=0.5,
            )


# ---------------------------------------------------------------------------
# LLMClient (Abstract)
# ---------------------------------------------------------------------------
class TestLLMClient:
    """Testes para a classe abstrata LLMClient."""

    def test_cannot_instantiate_directly(self):
        """Não é possível instanciar LLMClient diretamente (ABC enforcement)."""
        with pytest.raises(TypeError):
            LLMClient()

    def test_subclass_must_implement_enriquecer_proposicao(self):
        """Subclasse sem implementar enriquecer_proposicao falha ao instanciar."""

        class IncompleteClient(LLMClient):
            pass

        with pytest.raises(TypeError):
            IncompleteClient()

    def test_subclass_with_implementation_works(self):
        """Subclasse com implementação completa pode ser instanciada."""

        class MockClient(LLMClient):
            def enriquecer_proposicao(self, tipo, numero, ano, ementa, categorias=None):
                return LLMResult(
                    output=EnriquecimentoOutput(
                        headline="Test",
                        resumo_simples="Test",
                        impacto_cidadao=[],
                        confianca=1.0,
                    ),
                    tokens_input=10,
                    tokens_output=20,
                )

        client = MockClient()
        assert isinstance(client, LLMClient)


# ---------------------------------------------------------------------------
# Helpers para mock do OpenAI SDK
# ---------------------------------------------------------------------------
def _make_mock_response(content_dict: dict, prompt_tokens: int = 100, completion_tokens: int = 50):
    """Cria um mock de resposta da API OpenAI."""
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[0].message.content = json.dumps(content_dict)
    response.usage.prompt_tokens = prompt_tokens
    response.usage.completion_tokens = completion_tokens
    return response


VALID_OUTPUT = {
    "headline": "Projeto aumenta salário mínimo para R$ 2.000",
    "resumo_simples": "O projeto de lei propõe um aumento gradual do salário mínimo.",
    "impacto_cidadao": ["Aumento na renda mínima", "Possível impacto nos preços"],
    "confianca": 0.85,
}


# ---------------------------------------------------------------------------
# OpenAIClient
# ---------------------------------------------------------------------------
class TestOpenAIClient:
    """Testes para OpenAIClient com mock do SDK OpenAI."""

    @patch("src.shared.llm_client.OpenAI")
    def test_happy_path_returns_enrichment_output(self, mock_openai_cls):
        """Happy path: resposta válida da API é parseada em EnriquecimentoOutput."""
        mock_client_instance = MagicMock()
        mock_openai_cls.return_value = mock_client_instance
        mock_client_instance.chat.completions.create.return_value = _make_mock_response(VALID_OUTPUT)

        client = OpenAIClient(api_key="test-key")
        result = client.enriquecer_proposicao(
            tipo="PL",
            numero=1234,
            ano=2024,
            ementa="Altera disposições sobre o salário mínimo.",
        )

        assert isinstance(result, LLMResult)
        assert isinstance(result.output, EnriquecimentoOutput)
        assert result.output.headline == VALID_OUTPUT["headline"]
        assert result.output.confianca == 0.85
        assert result.output.impacto_cidadao == VALID_OUTPUT["impacto_cidadao"]

    @patch("src.shared.llm_client.OpenAI")
    def test_token_usage_extracted(self, mock_openai_cls):
        """Token usage é extraído corretamente da resposta da API."""
        mock_client_instance = MagicMock()
        mock_openai_cls.return_value = mock_client_instance
        mock_client_instance.chat.completions.create.return_value = _make_mock_response(
            VALID_OUTPUT, prompt_tokens=150, completion_tokens=75
        )

        client = OpenAIClient(api_key="test-key")
        result = client.enriquecer_proposicao("PL", 1, 2024, "Ementa teste")

        assert result.tokens_input == 150
        assert result.tokens_output == 75

    @patch("src.shared.llm_client.time.sleep")
    @patch("src.shared.llm_client.OpenAI")
    def test_rate_limit_triggers_retry(self, mock_openai_cls, mock_sleep):
        """RateLimitError dispara retry com exponential backoff."""
        mock_client_instance = MagicMock()
        mock_openai_cls.return_value = mock_client_instance

        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.headers = {}
        rate_limit_error = RateLimitError(
            message="Rate limited",
            response=mock_response,
            body=None,
        )

        mock_client_instance.chat.completions.create.side_effect = [
            rate_limit_error,
            _make_mock_response(VALID_OUTPUT),
        ]

        client = OpenAIClient(api_key="test-key")
        result = client.enriquecer_proposicao("PL", 1, 2024, "Ementa")

        assert isinstance(result, LLMResult)
        mock_sleep.assert_called_once_with(1)  # 2^0 = 1

    @patch("src.shared.llm_client.time.sleep")
    @patch("src.shared.llm_client.OpenAI")
    def test_timeout_triggers_retry(self, mock_openai_cls, mock_sleep):
        """APITimeoutError dispara retry com exponential backoff."""
        mock_client_instance = MagicMock()
        mock_openai_cls.return_value = mock_client_instance

        mock_request = MagicMock()
        timeout_error = APITimeoutError(request=mock_request)

        mock_client_instance.chat.completions.create.side_effect = [
            timeout_error,
            _make_mock_response(VALID_OUTPUT),
        ]

        client = OpenAIClient(api_key="test-key")
        result = client.enriquecer_proposicao("PL", 1, 2024, "Ementa")

        assert isinstance(result, LLMResult)
        mock_sleep.assert_called_once_with(1)  # 2^0 = 1

    @patch("src.shared.llm_client.time.sleep")
    @patch("src.shared.llm_client.OpenAI")
    def test_max_retries_exhausted_raises(self, mock_openai_cls, mock_sleep):
        """Após retries esgotados, exceção é propagada ao chamador."""
        mock_client_instance = MagicMock()
        mock_openai_cls.return_value = mock_client_instance

        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.headers = {}
        rate_limit_error = RateLimitError(
            message="Rate limited",
            response=mock_response,
            body=None,
        )

        mock_client_instance.chat.completions.create.side_effect = [
            rate_limit_error,
            rate_limit_error,
            rate_limit_error,
        ]

        client = OpenAIClient(api_key="test-key")
        with pytest.raises(RateLimitError):
            client.enriquecer_proposicao("PL", 1, 2024, "Ementa")

        assert mock_sleep.call_count == 3
        mock_sleep.assert_any_call(1)  # 2^0
        mock_sleep.assert_any_call(2)  # 2^1
        mock_sleep.assert_any_call(4)  # 2^2

    @patch("src.shared.llm_client.OpenAI")
    def test_invalid_json_raises_value_error(self, mock_openai_cls):
        """JSON inválido da resposta do LLM lança ValueError."""
        mock_client_instance = MagicMock()
        mock_openai_cls.return_value = mock_client_instance

        response = MagicMock()
        response.choices = [MagicMock()]
        response.choices[0].message.content = "not valid json {"
        response.usage.prompt_tokens = 100
        response.usage.completion_tokens = 50
        mock_client_instance.chat.completions.create.return_value = response

        client = OpenAIClient(api_key="test-key")
        with pytest.raises(ValueError, match="JSON válido"):
            client.enriquecer_proposicao("PL", 1, 2024, "Ementa")

    @patch("src.shared.llm_client.OpenAI")
    def test_pydantic_validation_failure_raises_value_error(self, mock_openai_cls):
        """Falha de validação Pydantic na resposta do LLM lança ValueError."""
        mock_client_instance = MagicMock()
        mock_openai_cls.return_value = mock_client_instance

        invalid_data = {"headline": "Test", "confianca": 2.0}  # confianca fora do range, campos faltando
        mock_client_instance.chat.completions.create.return_value = _make_mock_response(invalid_data)

        client = OpenAIClient(api_key="test-key")
        with pytest.raises(ValueError, match="validação"):
            client.enriquecer_proposicao("PL", 1, 2024, "Ementa")

    @patch("src.shared.llm_client.OpenAI")
    def test_api_key_passed_to_client(self, mock_openai_cls):
        """API key é passada corretamente para o client OpenAI."""
        OpenAIClient(api_key="sk-test-12345")
        mock_openai_cls.assert_called_once_with(api_key="sk-test-12345")

    @patch("src.shared.llm_client.OpenAI")
    def test_default_model_is_gpt4o_mini(self, mock_openai_cls):
        """Modelo padrão é gpt-4o-mini."""
        client = OpenAIClient(api_key="test-key")
        assert client.model == "gpt-4o-mini"

    @patch("src.shared.llm_client.OpenAI")
    def test_model_configurable_via_constructor(self, mock_openai_cls):
        """Modelo é configurável via parâmetro do construtor."""
        client = OpenAIClient(api_key="test-key", model="gpt-4o")
        assert client.model == "gpt-4o"

    @patch("src.shared.llm_client.OpenAI")
    def test_response_format_json_object(self, mock_openai_cls):
        """response_format é configurado como {"type": "json_object"} na chamada da API."""
        mock_client_instance = MagicMock()
        mock_openai_cls.return_value = mock_client_instance
        mock_client_instance.chat.completions.create.return_value = _make_mock_response(VALID_OUTPUT)

        client = OpenAIClient(api_key="test-key")
        client.enriquecer_proposicao("PL", 1, 2024, "Ementa")

        call_kwargs = mock_client_instance.chat.completions.create.call_args.kwargs
        assert call_kwargs["response_format"] == {"type": "json_object"}

    @patch("src.shared.llm_client.OpenAI")
    def test_temperature_and_max_tokens(self, mock_openai_cls):
        """temperature é 0.3 e max_tokens é 800 na chamada da API."""
        mock_client_instance = MagicMock()
        mock_openai_cls.return_value = mock_client_instance
        mock_client_instance.chat.completions.create.return_value = _make_mock_response(VALID_OUTPUT)

        client = OpenAIClient(api_key="test-key")
        client.enriquecer_proposicao("PL", 1, 2024, "Ementa")

        call_kwargs = mock_client_instance.chat.completions.create.call_args.kwargs
        assert call_kwargs["temperature"] == 0.3
        assert call_kwargs["max_tokens"] == 800

    @patch("src.shared.llm_client.OpenAI")
    def test_categorias_included_in_prompt(self, mock_openai_cls):
        """Categorias são incluídas no prompt quando fornecidas."""
        mock_client_instance = MagicMock()
        mock_openai_cls.return_value = mock_client_instance
        mock_client_instance.chat.completions.create.return_value = _make_mock_response(VALID_OUTPUT)

        client = OpenAIClient(api_key="test-key")
        client.enriquecer_proposicao("PL", 1, 2024, "Ementa", categorias=["Saúde", "Educação"])

        call_kwargs = mock_client_instance.chat.completions.create.call_args.kwargs
        user_message = call_kwargs["messages"][1]["content"]
        assert "Saúde" in user_message
        assert "Educação" in user_message
