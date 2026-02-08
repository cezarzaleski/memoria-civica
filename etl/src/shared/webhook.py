"""Módulo de notificações via webhook para alertas de erros.

Este módulo fornece funcionalidades para enviar notificações HTTP POST
para um endpoint webhook configurado, permitindo monitoramento automatizado
de falhas no script de download.

A entrega de webhook é "fire and forget" - falhas na entrega são logadas
mas não causam falha no processo principal.

Example:
    from src.shared.webhook import send_webhook_notification, WebhookResult

    result = send_webhook_notification(
        stage="download_deputados",
        message="Erro de conexão ao baixar deputados.csv"
    )
    if result.success:
        print("Notificação enviada com sucesso")
    elif result.skipped:
        print("Webhook não configurado, notificação ignorada")
    else:
        print(f"Falha na entrega: {result.error}")
"""

import logging
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Optional

import requests

from src.shared.config import settings

logger = logging.getLogger(__name__)

# Constantes
DEFAULT_TIMEOUT = 10  # segundos - tempo máximo de espera para entrega do webhook


@dataclass
class WebhookResult:
    """Resultado de uma operação de envio de webhook.

    Attributes:
        success: True se o webhook foi enviado com sucesso (status 2xx)
        skipped: True se o webhook não foi enviado porque URL não está configurada
        error: Mensagem de erro (None se sucesso ou skipped)
        status_code: Código HTTP da resposta (None se falhou antes da requisição ou skipped)
        response_time_ms: Tempo de resposta em milissegundos (None se falhou ou skipped)
    """

    success: bool
    skipped: bool
    error: Optional[str]  # noqa: UP045
    status_code: Optional[int] = None  # noqa: UP045
    response_time_ms: Optional[float] = None  # noqa: UP045


def _build_payload(stage: str, message: str, timestamp: str | None = None) -> dict:
    """Constrói o payload JSON para o webhook.

    Args:
        stage: Nome da etapa/fase onde ocorreu o erro (ex: "download_deputados")
        message: Mensagem descritiva do erro
        timestamp: Timestamp ISO 8601 (opcional, gerado automaticamente se não fornecido)

    Returns:
        Dicionário com payload estruturado para o webhook
    """
    if timestamp is None:
        timestamp = datetime.now(UTC).isoformat()

    return {
        "etapa": stage,
        "mensagem": message,
        "timestamp": timestamp,
    }


def _is_valid_url(url: str) -> bool:
    """Verifica se a URL é válida para webhook.

    Args:
        url: URL a ser validada

    Returns:
        True se a URL é válida (começa com http:// ou https://)
    """
    return url.startswith("http://") or url.startswith("https://")


def send_webhook_notification(
    stage: str,
    message: str,
    timeout: int = DEFAULT_TIMEOUT,
    timestamp: Optional[str] = None,  # noqa: UP045
) -> WebhookResult:
    """Envia notificação de erro via webhook HTTP POST.

    Esta função é segura para falhas - erros na entrega do webhook são
    logados mas não propagam exceções, permitindo que o processo principal
    continue sua execução.

    Args:
        stage: Nome da etapa/fase onde ocorreu o erro (ex: "download_deputados", "etl_transform")
        message: Mensagem descritiva do erro para diagnóstico
        timeout: Timeout em segundos para a requisição HTTP (padrão: 10)
        timestamp: Timestamp ISO 8601 opcional (gerado automaticamente se não fornecido)

    Returns:
        WebhookResult indicando sucesso, skip ou falha da entrega

    Example:
        # Notificar erro de download
        result = send_webhook_notification(
            stage="download_proposicoes",
            message="Timeout ao baixar proposicoes-2025.csv após 3 tentativas"
        )

        # Com timestamp customizado
        result = send_webhook_notification(
            stage="etl_load",
            message="Erro de integridade no banco de dados",
            timestamp="2024-01-15T10:30:00Z"
        )
    """
    # Verificar se webhook está configurado
    webhook_url = getattr(settings, "WEBHOOK_URL", None)

    if not webhook_url:
        logger.debug("WEBHOOK_URL não configurada, notificação ignorada")
        return WebhookResult(
            success=False,
            skipped=True,
            error=None,
        )

    # Validar formato da URL
    if not _is_valid_url(webhook_url):
        error_msg = f"URL de webhook inválida: {webhook_url}"
        logger.error(error_msg)
        return WebhookResult(
            success=False,
            skipped=False,
            error=error_msg,
        )

    # Construir payload
    payload = _build_payload(stage, message, timestamp)

    logger.info(
        "Enviando notificação webhook: etapa=%s, mensagem=%s",
        stage,
        message[:100] + "..." if len(message) > 100 else message,
    )

    try:
        start_time = time.time()

        response = requests.post(
            webhook_url,
            json=payload,
            timeout=timeout,
            headers={"Content-Type": "application/json"},
        )

        response_time_ms = (time.time() - start_time) * 1000

        # Verificar status de sucesso (2xx)
        if 200 <= response.status_code < 300:
            logger.info(
                "Webhook entregue com sucesso: status=%d, tempo=%.2fms",
                response.status_code,
                response_time_ms,
            )
            return WebhookResult(
                success=True,
                skipped=False,
                error=None,
                status_code=response.status_code,
                response_time_ms=response_time_ms,
            )

        # Status não-2xx
        error_msg = f"Webhook retornou status {response.status_code}: {response.reason}"
        logger.warning(
            "Webhook retornou erro: status=%d, reason=%s, tempo=%.2fms",
            response.status_code,
            response.reason,
            response_time_ms,
        )
        return WebhookResult(
            success=False,
            skipped=False,
            error=error_msg,
            status_code=response.status_code,
            response_time_ms=response_time_ms,
        )

    except requests.exceptions.Timeout:
        error_msg = f"Timeout ao enviar webhook após {timeout}s"
        logger.warning(error_msg)
        return WebhookResult(
            success=False,
            skipped=False,
            error=error_msg,
        )

    except requests.exceptions.ConnectionError as e:
        error_msg = f"Erro de conexão ao enviar webhook: {e}"
        logger.warning(error_msg)
        return WebhookResult(
            success=False,
            skipped=False,
            error=error_msg,
        )

    except requests.exceptions.RequestException as e:
        error_msg = f"Erro ao enviar webhook: {e}"
        logger.warning(error_msg)
        return WebhookResult(
            success=False,
            skipped=False,
            error=error_msg,
        )

    except Exception as e:
        error_msg = f"Erro inesperado ao enviar webhook: {e}"
        logger.error(error_msg)
        return WebhookResult(
            success=False,
            skipped=False,
            error=error_msg,
        )
