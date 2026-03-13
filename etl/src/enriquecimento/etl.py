"""Pipeline ETL batch para enriquecimento LLM de proposições legislativas.

Orquestra o pipeline de enriquecimento: filtra proposições pendentes,
processa em lotes via OpenAIClient, aplica threshold de confiança,
e persiste resultados via EnriquecimentoRepository. Step NÃO-CRÍTICO:
falha gera warning mas não interrompe o pipeline principal.
"""

import logging
import time

from sqlalchemy.orm import Session

from src.classificacao.repository import ProposicaoCategoriaRepository
from src.enriquecimento.prompts import PROMPT_VERSION
from src.enriquecimento.repository import EnriquecimentoRepository
from src.shared.config import settings
from src.shared.database import get_db
from src.shared.llm_client import OpenAIClient

logger = logging.getLogger(__name__)

RATE_LIMIT_DELAY = 0.5
"""Delay em segundos entre chamadas LLM para respeitar rate limits."""


def run_enriquecimento_etl(db: Session | None = None) -> int:
    """Executa o pipeline ETL de enriquecimento LLM de proposições.

    Orquestra:
    1. Verificação de feature flag (LLM_ENABLED) e API key
    2. Query de proposições pendentes (sem enriquecimento na versão atual)
    3. Processamento em lotes via OpenAIClient
    4. Upsert de resultados com threshold de confiança
    5. Log de resumo com totais

    Step NÃO-CRÍTICO: falha gera warning mas não interrompe o pipeline.

    Args:
        db: Sessão opcional (se None, usa get_db())

    Returns:
        Quantidade de proposições enriquecidas com sucesso.
    """
    if db is None:
        with get_db() as db:
            return _run_enriquecimento_etl_impl(db)
    else:
        return _run_enriquecimento_etl_impl(db)


def _run_enriquecimento_etl_impl(db: Session) -> int:
    """Implementação interna do ETL de enriquecimento LLM.

    Args:
        db: Sessão de banco de dados

    Returns:
        Quantidade de proposições enriquecidas com sucesso.
    """
    logger.info("Iniciando ETL enriquecimento LLM...")

    # 1. Verificar feature flag
    if not settings.LLM_ENABLED:
        logger.info("LLM_ENABLED=False — pulando enriquecimento LLM")
        return 0

    # 2. Verificar API key
    if settings.LLM_API_KEY is None:
        logger.warning("LLM_ENABLED=True mas LLM_API_KEY não configurada — pulando enriquecimento LLM")
        return 0

    # 3. Query proposições pendentes
    repo = EnriquecimentoRepository(db)
    pendentes = repo.get_pendentes(versao_prompt=PROMPT_VERSION)

    total_pendentes = len(pendentes)
    if total_pendentes == 0:
        logger.info("Nenhuma proposição pendente de enriquecimento para versao_prompt=%s", PROMPT_VERSION)
        return 0

    logger.info("Proposições pendentes para enriquecimento: %d", total_pendentes)

    # 4. Instanciar client LLM
    client = OpenAIClient(api_key=settings.LLM_API_KEY, model=settings.LLM_MODEL)
    pc_repo = ProposicaoCategoriaRepository(db)

    total_processados = 0
    total_erros = 0
    total_tokens_input = 0
    total_tokens_output = 0

    # 5. Processar em lotes
    batch_size = settings.LLM_BATCH_SIZE
    for batch_start in range(0, total_pendentes, batch_size):
        batch = pendentes[batch_start : batch_start + batch_size]
        logger.info(
            "Processando batch %d-%d de %d",
            batch_start + 1,
            min(batch_start + len(batch), total_pendentes),
            total_pendentes,
        )

        for i, prop in enumerate(batch):
            try:
                # 5.1 Buscar categorias regex existentes
                categorias_existentes = pc_repo.get_by_proposicao(prop.id)
                categorias_nomes: list[str] | None = None
                if categorias_existentes:
                    categorias_nomes = [pc.categoria.codigo for pc in categorias_existentes]

                # 5.2 Chamar LLM
                resultado = client.enriquecer_proposicao(
                    tipo=prop.tipo,
                    numero=prop.numero,
                    ano=prop.ano,
                    ementa=prop.ementa or "",
                    categorias=categorias_nomes,
                )

                # 5.3 Validar headline length (warning only)
                if len(resultado.output.headline) > 120:
                    logger.warning(
                        "Headline excede 120 chars para proposição %d: %d chars",
                        prop.id,
                        len(resultado.output.headline),
                    )

                # 5.4 Upsert resultado
                repo.upsert(
                    proposicao_id=prop.id,
                    resultado=resultado.output,
                    modelo=client.model,
                    versao_prompt=PROMPT_VERSION,
                    tokens_input=resultado.tokens_input,
                    tokens_output=resultado.tokens_output,
                    confianca_threshold=settings.LLM_CONFIDENCE_THRESHOLD,
                )

                total_processados += 1
                total_tokens_input += resultado.tokens_input
                total_tokens_output += resultado.tokens_output

            except Exception as e:
                logger.warning(
                    "Erro ao enriquecer proposição %d: %s: %s",
                    prop.id,
                    type(e).__name__,
                    e,
                )
                total_erros += 1

            # 5.5 Rate limit delay entre chamadas (exceto a última)
            if i < len(batch) - 1 or batch_start + len(batch) < total_pendentes:
                time.sleep(RATE_LIMIT_DELAY)

    # 6. Log de resumo
    logger.info(
        "ETL enriquecimento concluído: pendentes=%d, processados=%d, erros=%d, "
        "tokens_input=%d, tokens_output=%d",
        total_pendentes,
        total_processados,
        total_erros,
        total_tokens_input,
        total_tokens_output,
    )

    return total_processados
