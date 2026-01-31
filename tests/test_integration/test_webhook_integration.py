"""Testes de integração para src/shared/webhook.py.

Testa o envio de notificações via webhook com um servidor HTTP mock real.
"""

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import ClassVar
from unittest.mock import patch

import pytest

from src.shared.webhook import send_webhook_notification


class WebhookMockHandler(BaseHTTPRequestHandler):
    """Handler HTTP para mock de webhook."""

    # Armazena as requisições recebidas para verificação
    received_requests: ClassVar[list[dict]] = []
    response_status: ClassVar[int] = 200
    response_body: ClassVar[str] = '{"status": "ok"}'

    def do_POST(self):
        """Processa requisições POST."""
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        # Armazena a requisição para verificação posterior
        request_data = {
            "path": self.path,
            "headers": dict(self.headers),
            "body": json.loads(body) if body else None,
        }
        WebhookMockHandler.received_requests.append(request_data)

        # Envia resposta
        self.send_response(self.response_status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(self.response_body.encode())

    def log_message(self, format, *args):
        """Suprime logs do servidor."""
        pass


@pytest.fixture
def mock_webhook_server():
    """Fixture que inicia um servidor HTTP mock para testes de webhook."""
    # Limpa requisições anteriores
    WebhookMockHandler.received_requests = []
    WebhookMockHandler.response_status = 200
    WebhookMockHandler.response_body = '{"status": "ok"}'

    # Encontra uma porta disponível
    server = HTTPServer(("127.0.0.1", 0), WebhookMockHandler)
    port = server.server_address[1]
    url = f"http://127.0.0.1:{port}/webhook"

    # Inicia servidor em thread separada
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    yield {
        "server": server,
        "url": url,
        "port": port,
        "handler": WebhookMockHandler,
    }

    # Cleanup
    server.shutdown()


@pytest.mark.integration
class TestWebhookIntegration:
    """Testes de integração para envio de webhook."""

    def test_delivers_webhook_to_real_http_server(self, mock_webhook_server):
        """Testa entrega de webhook para servidor HTTP real."""
        webhook_url = mock_webhook_server["url"]

        with patch("src.shared.webhook.settings") as mock_settings:
            mock_settings.WEBHOOK_URL = webhook_url

            result = send_webhook_notification(
                stage="download_deputados",
                message="Erro de conexão ao baixar deputados.csv",
            )

        assert result.success is True
        assert result.status_code == 200
        assert result.response_time_ms is not None
        assert result.response_time_ms > 0

    def test_sends_correct_json_payload(self, mock_webhook_server):
        """Testa que payload JSON enviado tem estrutura correta."""
        webhook_url = mock_webhook_server["url"]
        handler = mock_webhook_server["handler"]

        with patch("src.shared.webhook.settings") as mock_settings:
            mock_settings.WEBHOOK_URL = webhook_url

            send_webhook_notification(
                stage="download_proposicoes",
                message="Timeout ao baixar proposicoes-2025.csv",
                timestamp="2024-01-15T10:30:00Z",
            )

        # Verifica requisição recebida
        assert len(handler.received_requests) == 1
        request = handler.received_requests[0]

        # Verifica path
        assert request["path"] == "/webhook"

        # Verifica body
        body = request["body"]
        assert body["etapa"] == "download_proposicoes"
        assert body["mensagem"] == "Timeout ao baixar proposicoes-2025.csv"
        assert body["timestamp"] == "2024-01-15T10:30:00Z"

    def test_sends_content_type_json_header(self, mock_webhook_server):
        """Testa que header Content-Type: application/json é enviado."""
        webhook_url = mock_webhook_server["url"]
        handler = mock_webhook_server["handler"]

        with patch("src.shared.webhook.settings") as mock_settings:
            mock_settings.WEBHOOK_URL = webhook_url

            send_webhook_notification(stage="test", message="test")

        assert len(handler.received_requests) == 1
        request = handler.received_requests[0]
        assert request["headers"]["Content-Type"] == "application/json"

    def test_handles_non_200_response(self, mock_webhook_server):
        """Testa tratamento de resposta não-200."""
        webhook_url = mock_webhook_server["url"]
        handler = mock_webhook_server["handler"]

        # Configura servidor para retornar 500
        handler.response_status = 500
        handler.response_body = '{"error": "Internal Server Error"}'

        with patch("src.shared.webhook.settings") as mock_settings:
            mock_settings.WEBHOOK_URL = webhook_url

            result = send_webhook_notification(
                stage="test_stage",
                message="test message",
            )

        assert result.success is False
        assert result.status_code == 500
        assert "500" in result.error

    def test_generates_timestamp_when_not_provided(self, mock_webhook_server):
        """Testa que timestamp é gerado automaticamente."""
        webhook_url = mock_webhook_server["url"]
        handler = mock_webhook_server["handler"]

        with patch("src.shared.webhook.settings") as mock_settings:
            mock_settings.WEBHOOK_URL = webhook_url

            send_webhook_notification(
                stage="auto_timestamp_test",
                message="test without timestamp",
            )

        assert len(handler.received_requests) == 1
        body = handler.received_requests[0]["body"]
        assert "timestamp" in body
        assert body["timestamp"] is not None
        # Verifica formato ISO 8601
        assert "T" in body["timestamp"]

    def test_multiple_notifications_delivered_sequentially(self, mock_webhook_server):
        """Testa que múltiplas notificações são entregues corretamente."""
        webhook_url = mock_webhook_server["url"]
        handler = mock_webhook_server["handler"]

        with patch("src.shared.webhook.settings") as mock_settings:
            mock_settings.WEBHOOK_URL = webhook_url

            # Envia 3 notificações
            send_webhook_notification(stage="stage_1", message="message_1")
            send_webhook_notification(stage="stage_2", message="message_2")
            send_webhook_notification(stage="stage_3", message="message_3")

        # Verifica que todas foram recebidas
        assert len(handler.received_requests) == 3

        stages = [req["body"]["etapa"] for req in handler.received_requests]
        assert "stage_1" in stages
        assert "stage_2" in stages
        assert "stage_3" in stages


@pytest.mark.integration
class TestWebhookDownloadIntegration:
    """Testes de integração para webhook no contexto de download."""

    def test_webhook_triggered_on_download_error_scenario(self, mock_webhook_server, tmp_path):
        """Testa que webhook é acionado em cenário de erro de download."""
        webhook_url = mock_webhook_server["url"]
        handler = mock_webhook_server["handler"]

        with patch("src.shared.webhook.settings") as mock_settings:
            mock_settings.WEBHOOK_URL = webhook_url

            # Simula notificação de erro de download (como seria chamada pelo download_camara.py)
            result = send_webhook_notification(
                stage="download_deputados",
                message="Erro HTTP: 503 - Service Unavailable",
            )

        assert result.success is True
        assert len(handler.received_requests) == 1

        body = handler.received_requests[0]["body"]
        assert body["etapa"] == "download_deputados"
        assert "503" in body["mensagem"]

    def test_webhook_failure_does_not_raise_exception(self, mock_webhook_server):
        """Testa que falha de webhook não levanta exceção (fire and forget)."""
        # Usa URL inválida que vai falhar
        invalid_url = "http://127.0.0.1:99999/invalid"

        with patch("src.shared.webhook.settings") as mock_settings:
            mock_settings.WEBHOOK_URL = invalid_url

            # Não deve levantar exceção
            result = send_webhook_notification(
                stage="test_stage",
                message="test message",
            )

        # Deve retornar erro mas não levantar exceção
        assert result.success is False
        assert result.error is not None
