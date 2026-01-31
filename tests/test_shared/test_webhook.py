"""Testes unitários para src/shared/webhook.py.

Testa funcionalidades de envio de notificações via webhook HTTP POST.
"""

import logging
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import requests

from src.shared.webhook import (
    DEFAULT_TIMEOUT,
    WebhookResult,
    _build_payload,
    _is_valid_url,
    send_webhook_notification,
)


class TestWebhookResultDataclass:
    """Testes para a dataclass WebhookResult."""

    def test_webhook_result_has_correct_fields(self):
        """Testa que WebhookResult tem os campos corretos."""
        result = WebhookResult(
            success=True,
            skipped=False,
            error=None,
        )
        assert result.success is True
        assert result.skipped is False
        assert result.error is None
        # Campos com valores padrão
        assert result.status_code is None
        assert result.response_time_ms is None

    def test_webhook_result_success_state(self):
        """Testa estado de sucesso."""
        result = WebhookResult(
            success=True,
            skipped=False,
            error=None,
            status_code=200,
            response_time_ms=150.5,
        )
        assert result.success
        assert not result.skipped
        assert result.error is None
        assert result.status_code == 200
        assert result.response_time_ms == 150.5

    def test_webhook_result_skipped_state(self):
        """Testa estado de skip (URL não configurada)."""
        result = WebhookResult(success=False, skipped=True, error=None)
        assert not result.success
        assert result.skipped
        assert result.error is None

    def test_webhook_result_error_state(self):
        """Testa estado de erro."""
        result = WebhookResult(
            success=False,
            skipped=False,
            error="Connection refused",
            status_code=None,
        )
        assert not result.success
        assert not result.skipped
        assert result.error == "Connection refused"


class TestBuildPayload:
    """Testes para a função _build_payload."""

    def test_builds_payload_with_all_fields(self):
        """Testa que payload contém todos os campos obrigatórios."""
        payload = _build_payload(
            stage="download_deputados",
            message="Erro de conexão",
            timestamp="2024-01-15T10:30:00Z",
        )

        assert payload["etapa"] == "download_deputados"
        assert payload["mensagem"] == "Erro de conexão"
        assert payload["timestamp"] == "2024-01-15T10:30:00Z"

    def test_generates_timestamp_when_not_provided(self):
        """Testa que timestamp é gerado automaticamente quando não fornecido."""
        before = datetime.now(UTC).isoformat()
        payload = _build_payload(stage="test_stage", message="test message")
        after = datetime.now(UTC).isoformat()

        assert "timestamp" in payload
        assert payload["timestamp"] >= before
        assert payload["timestamp"] <= after

    def test_uses_provided_timestamp(self):
        """Testa que usa timestamp fornecido quando disponível."""
        custom_timestamp = "2023-06-01T00:00:00Z"
        payload = _build_payload(
            stage="test_stage",
            message="test message",
            timestamp=custom_timestamp,
        )

        assert payload["timestamp"] == custom_timestamp


class TestIsValidUrl:
    """Testes para a função _is_valid_url."""

    def test_accepts_https_url(self):
        """Testa que aceita URLs HTTPS."""
        assert _is_valid_url("https://hooks.slack.com/services/XXX") is True
        assert _is_valid_url("https://example.com/webhook") is True

    def test_accepts_http_url(self):
        """Testa que aceita URLs HTTP."""
        assert _is_valid_url("http://localhost:8080/webhook") is True
        assert _is_valid_url("http://example.com/api/notify") is True

    def test_rejects_invalid_urls(self):
        """Testa que rejeita URLs inválidas."""
        assert _is_valid_url("ftp://example.com/file") is False
        assert _is_valid_url("file:///path/to/file") is False
        assert _is_valid_url("not-a-url") is False
        assert _is_valid_url("") is False
        assert _is_valid_url("example.com/webhook") is False


class TestSendWebhookNotification:
    """Testes para a função send_webhook_notification."""

    @patch("src.shared.webhook.settings")
    def test_skips_when_webhook_url_not_configured(self, mock_settings):
        """Testa que retorna skipped=True quando WEBHOOK_URL não está configurada."""
        mock_settings.WEBHOOK_URL = None

        result = send_webhook_notification(
            stage="test_stage",
            message="test message",
        )

        assert result.success is False
        assert result.skipped is True
        assert result.error is None

    @patch("src.shared.webhook.settings")
    def test_skips_when_webhook_url_is_empty_string(self, mock_settings):
        """Testa que retorna skipped quando WEBHOOK_URL é string vazia."""
        mock_settings.WEBHOOK_URL = ""

        result = send_webhook_notification(
            stage="test_stage",
            message="test message",
        )

        assert result.success is False
        assert result.skipped is True

    @patch("src.shared.webhook.settings")
    def test_returns_error_for_invalid_url_format(self, mock_settings):
        """Testa que retorna erro para formato de URL inválido."""
        mock_settings.WEBHOOK_URL = "not-a-valid-url"

        result = send_webhook_notification(
            stage="test_stage",
            message="test message",
        )

        assert result.success is False
        assert result.skipped is False
        assert "inválida" in result.error.lower()

    @patch("src.shared.webhook.requests.post")
    @patch("src.shared.webhook.settings")
    def test_successful_delivery_with_200_status(self, mock_settings, mock_post):
        """Testa entrega bem-sucedida com status 200."""
        mock_settings.WEBHOOK_URL = "https://hooks.example.com/webhook"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.reason = "OK"
        mock_post.return_value = mock_response

        result = send_webhook_notification(
            stage="download_deputados",
            message="Erro de conexão",
        )

        assert result.success is True
        assert result.skipped is False
        assert result.error is None
        assert result.status_code == 200
        assert result.response_time_ms is not None

    @patch("src.shared.webhook.requests.post")
    @patch("src.shared.webhook.settings")
    def test_successful_delivery_with_201_status(self, mock_settings, mock_post):
        """Testa entrega bem-sucedida com status 201."""
        mock_settings.WEBHOOK_URL = "https://hooks.example.com/webhook"

        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.reason = "Created"
        mock_post.return_value = mock_response

        result = send_webhook_notification(
            stage="test_stage",
            message="test message",
        )

        assert result.success is True
        assert result.status_code == 201

    @patch("src.shared.webhook.requests.post")
    @patch("src.shared.webhook.settings")
    def test_successful_delivery_with_204_status(self, mock_settings, mock_post):
        """Testa entrega bem-sucedida com status 204 (No Content)."""
        mock_settings.WEBHOOK_URL = "https://hooks.example.com/webhook"

        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_response.reason = "No Content"
        mock_post.return_value = mock_response

        result = send_webhook_notification(
            stage="test_stage",
            message="test message",
        )

        assert result.success is True
        assert result.status_code == 204

    @patch("src.shared.webhook.requests.post")
    @patch("src.shared.webhook.settings")
    def test_sends_correct_json_payload(self, mock_settings, mock_post):
        """Testa que envia payload JSON com estrutura correta."""
        mock_settings.WEBHOOK_URL = "https://hooks.example.com/webhook"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        send_webhook_notification(
            stage="download_proposicoes",
            message="Timeout ao baixar arquivo",
            timestamp="2024-01-15T10:30:00Z",
        )

        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args[1]

        assert call_kwargs["json"]["etapa"] == "download_proposicoes"
        assert call_kwargs["json"]["mensagem"] == "Timeout ao baixar arquivo"
        assert call_kwargs["json"]["timestamp"] == "2024-01-15T10:30:00Z"

    @patch("src.shared.webhook.requests.post")
    @patch("src.shared.webhook.settings")
    def test_uses_content_type_json_header(self, mock_settings, mock_post):
        """Testa que envia header Content-Type: application/json."""
        mock_settings.WEBHOOK_URL = "https://hooks.example.com/webhook"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        send_webhook_notification(stage="test", message="test")

        call_kwargs = mock_post.call_args[1]
        assert call_kwargs["headers"]["Content-Type"] == "application/json"

    @patch("src.shared.webhook.requests.post")
    @patch("src.shared.webhook.settings")
    def test_respects_timeout_parameter(self, mock_settings, mock_post):
        """Testa que respeita parâmetro timeout."""
        mock_settings.WEBHOOK_URL = "https://hooks.example.com/webhook"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        custom_timeout = 5
        send_webhook_notification(
            stage="test",
            message="test",
            timeout=custom_timeout,
        )

        call_kwargs = mock_post.call_args[1]
        assert call_kwargs["timeout"] == custom_timeout

    @patch("src.shared.webhook.requests.post")
    @patch("src.shared.webhook.settings")
    def test_uses_default_timeout(self, mock_settings, mock_post):
        """Testa que usa timeout padrão quando não especificado."""
        mock_settings.WEBHOOK_URL = "https://hooks.example.com/webhook"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        send_webhook_notification(stage="test", message="test")

        call_kwargs = mock_post.call_args[1]
        assert call_kwargs["timeout"] == DEFAULT_TIMEOUT

    def test_default_timeout_is_10_seconds(self):
        """Testa que timeout padrão é 10 segundos."""
        assert DEFAULT_TIMEOUT == 10


class TestWebhookErrorHandling:
    """Testes para tratamento de erros no envio de webhook."""

    @patch("src.shared.webhook.requests.post")
    @patch("src.shared.webhook.settings")
    def test_handles_timeout_error(self, mock_settings, mock_post):
        """Testa tratamento de timeout."""
        mock_settings.WEBHOOK_URL = "https://hooks.example.com/webhook"
        mock_post.side_effect = requests.exceptions.Timeout("Connection timed out")

        result = send_webhook_notification(
            stage="test_stage",
            message="test message",
        )

        assert result.success is False
        assert result.skipped is False
        assert "timeout" in result.error.lower()

    @patch("src.shared.webhook.requests.post")
    @patch("src.shared.webhook.settings")
    def test_handles_connection_error(self, mock_settings, mock_post):
        """Testa tratamento de erro de conexão."""
        mock_settings.WEBHOOK_URL = "https://hooks.example.com/webhook"
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection refused")

        result = send_webhook_notification(
            stage="test_stage",
            message="test message",
        )

        assert result.success is False
        assert result.skipped is False
        assert "conexão" in result.error.lower()

    @patch("src.shared.webhook.requests.post")
    @patch("src.shared.webhook.settings")
    def test_handles_request_exception(self, mock_settings, mock_post):
        """Testa tratamento de RequestException genérica."""
        mock_settings.WEBHOOK_URL = "https://hooks.example.com/webhook"
        mock_post.side_effect = requests.exceptions.RequestException("Request failed")

        result = send_webhook_notification(
            stage="test_stage",
            message="test message",
        )

        assert result.success is False
        assert result.skipped is False
        assert result.error is not None

    @patch("src.shared.webhook.requests.post")
    @patch("src.shared.webhook.settings")
    def test_handles_unexpected_exception(self, mock_settings, mock_post):
        """Testa tratamento de exceção inesperada."""
        mock_settings.WEBHOOK_URL = "https://hooks.example.com/webhook"
        mock_post.side_effect = RuntimeError("Unexpected error")

        result = send_webhook_notification(
            stage="test_stage",
            message="test message",
        )

        assert result.success is False
        assert result.skipped is False
        assert "inesperado" in result.error.lower()


class TestWebhookNon2xxResponses:
    """Testes para respostas HTTP não-2xx."""

    @patch("src.shared.webhook.requests.post")
    @patch("src.shared.webhook.settings")
    def test_handles_400_bad_request(self, mock_settings, mock_post):
        """Testa tratamento de status 400 Bad Request."""
        mock_settings.WEBHOOK_URL = "https://hooks.example.com/webhook"

        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.reason = "Bad Request"
        mock_post.return_value = mock_response

        result = send_webhook_notification(
            stage="test_stage",
            message="test message",
        )

        assert result.success is False
        assert result.skipped is False
        assert result.status_code == 400
        assert "400" in result.error

    @patch("src.shared.webhook.requests.post")
    @patch("src.shared.webhook.settings")
    def test_handles_401_unauthorized(self, mock_settings, mock_post):
        """Testa tratamento de status 401 Unauthorized."""
        mock_settings.WEBHOOK_URL = "https://hooks.example.com/webhook"

        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.reason = "Unauthorized"
        mock_post.return_value = mock_response

        result = send_webhook_notification(
            stage="test_stage",
            message="test message",
        )

        assert result.success is False
        assert result.status_code == 401

    @patch("src.shared.webhook.requests.post")
    @patch("src.shared.webhook.settings")
    def test_handles_404_not_found(self, mock_settings, mock_post):
        """Testa tratamento de status 404 Not Found."""
        mock_settings.WEBHOOK_URL = "https://hooks.example.com/webhook"

        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.reason = "Not Found"
        mock_post.return_value = mock_response

        result = send_webhook_notification(
            stage="test_stage",
            message="test message",
        )

        assert result.success is False
        assert result.status_code == 404

    @patch("src.shared.webhook.requests.post")
    @patch("src.shared.webhook.settings")
    def test_handles_500_internal_server_error(self, mock_settings, mock_post):
        """Testa tratamento de status 500 Internal Server Error."""
        mock_settings.WEBHOOK_URL = "https://hooks.example.com/webhook"

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.reason = "Internal Server Error"
        mock_post.return_value = mock_response

        result = send_webhook_notification(
            stage="test_stage",
            message="test message",
        )

        assert result.success is False
        assert result.status_code == 500

    @patch("src.shared.webhook.requests.post")
    @patch("src.shared.webhook.settings")
    def test_handles_503_service_unavailable(self, mock_settings, mock_post):
        """Testa tratamento de status 503 Service Unavailable."""
        mock_settings.WEBHOOK_URL = "https://hooks.example.com/webhook"

        mock_response = MagicMock()
        mock_response.status_code = 503
        mock_response.reason = "Service Unavailable"
        mock_post.return_value = mock_response

        result = send_webhook_notification(
            stage="test_stage",
            message="test message",
        )

        assert result.success is False
        assert result.status_code == 503


class TestWebhookLogging:
    """Testes para logging do módulo webhook."""

    @patch("src.shared.webhook.settings")
    def test_logs_debug_when_url_not_configured(self, mock_settings, caplog):
        """Testa que loga DEBUG quando URL não está configurada."""
        mock_settings.WEBHOOK_URL = None

        with caplog.at_level(logging.DEBUG):
            send_webhook_notification(stage="test", message="test")

        assert "não configurada" in caplog.text.lower()

    @patch("src.shared.webhook.settings")
    def test_logs_error_for_invalid_url(self, mock_settings, caplog):
        """Testa que loga ERROR para URL inválida."""
        mock_settings.WEBHOOK_URL = "invalid-url"

        with caplog.at_level(logging.ERROR):
            send_webhook_notification(stage="test", message="test")

        assert "inválida" in caplog.text.lower()

    @patch("src.shared.webhook.requests.post")
    @patch("src.shared.webhook.settings")
    def test_logs_info_on_successful_delivery(self, mock_settings, mock_post, caplog):
        """Testa que loga INFO em entrega bem-sucedida."""
        mock_settings.WEBHOOK_URL = "https://hooks.example.com/webhook"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.reason = "OK"
        mock_post.return_value = mock_response

        with caplog.at_level(logging.INFO):
            send_webhook_notification(stage="test", message="test")

        assert "sucesso" in caplog.text.lower()

    @patch("src.shared.webhook.requests.post")
    @patch("src.shared.webhook.settings")
    def test_logs_warning_on_non_2xx_response(self, mock_settings, mock_post, caplog):
        """Testa que loga WARNING em resposta não-2xx."""
        mock_settings.WEBHOOK_URL = "https://hooks.example.com/webhook"

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.reason = "Internal Server Error"
        mock_post.return_value = mock_response

        with caplog.at_level(logging.WARNING):
            send_webhook_notification(stage="test", message="test")

        assert "erro" in caplog.text.lower() or "500" in caplog.text

    @patch("src.shared.webhook.requests.post")
    @patch("src.shared.webhook.settings")
    def test_logs_warning_on_timeout(self, mock_settings, mock_post, caplog):
        """Testa que loga WARNING em timeout."""
        mock_settings.WEBHOOK_URL = "https://hooks.example.com/webhook"
        mock_post.side_effect = requests.exceptions.Timeout()

        with caplog.at_level(logging.WARNING):
            send_webhook_notification(stage="test", message="test")

        assert "timeout" in caplog.text.lower()

    @patch("src.shared.webhook.requests.post")
    @patch("src.shared.webhook.settings")
    def test_logs_response_time(self, mock_settings, mock_post, caplog):
        """Testa que loga tempo de resposta em entrega bem-sucedida."""
        mock_settings.WEBHOOK_URL = "https://hooks.example.com/webhook"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.reason = "OK"
        mock_post.return_value = mock_response

        with caplog.at_level(logging.INFO):
            send_webhook_notification(stage="test", message="test")

        assert "ms" in caplog.text.lower() or "tempo" in caplog.text.lower()


class TestWebhookDoesNotBlockMainProcess:
    """Testes para verificar que falhas de webhook não bloqueiam o processo principal."""

    @patch("src.shared.webhook.requests.post")
    @patch("src.shared.webhook.settings")
    def test_timeout_does_not_raise_exception(self, mock_settings, mock_post):
        """Testa que timeout não levanta exceção."""
        mock_settings.WEBHOOK_URL = "https://hooks.example.com/webhook"
        mock_post.side_effect = requests.exceptions.Timeout()

        # Não deve levantar exceção
        result = send_webhook_notification(stage="test", message="test")

        assert result.success is False
        assert result.error is not None

    @patch("src.shared.webhook.requests.post")
    @patch("src.shared.webhook.settings")
    def test_connection_error_does_not_raise_exception(self, mock_settings, mock_post):
        """Testa que erro de conexão não levanta exceção."""
        mock_settings.WEBHOOK_URL = "https://hooks.example.com/webhook"
        mock_post.side_effect = requests.exceptions.ConnectionError()

        # Não deve levantar exceção
        result = send_webhook_notification(stage="test", message="test")

        assert result.success is False
        assert result.error is not None

    @patch("src.shared.webhook.requests.post")
    @patch("src.shared.webhook.settings")
    def test_any_exception_does_not_raise(self, mock_settings, mock_post):
        """Testa que qualquer exceção não propaga."""
        mock_settings.WEBHOOK_URL = "https://hooks.example.com/webhook"
        mock_post.side_effect = Exception("Unexpected error")

        # Não deve levantar exceção
        result = send_webhook_notification(stage="test", message="test")

        assert result.success is False
        assert result.error is not None
