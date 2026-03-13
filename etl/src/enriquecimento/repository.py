"""Repository para acesso a dados do domínio de Enriquecimento LLM.

Fornece operações de upsert idempotente e queries especializadas para
a tabela enriquecimentos_llm, incluindo busca de proposições pendentes
de enriquecimento e consulta por proposição.
"""

import json
import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.enriquecimento.models import EnriquecimentoLLM
from src.proposicoes.models import Proposicao
from src.shared.llm_client import EnriquecimentoOutput

logger = logging.getLogger(__name__)


class EnriquecimentoRepository:
    """Repository para operações de dados em enriquecimentos_llm.

    Encapsula o acesso ao banco de dados para o domínio de enriquecimento,
    oferecendo upsert idempotente e queries especializadas para o pipeline ETL.

    Attributes:
        db: Sessão SQLAlchemy injetada via dependency injection
    """

    def __init__(self, db: Session) -> None:
        """Inicializa o repository com uma sessão de banco de dados.

        Args:
            db: Sessão SQLAlchemy para executar queries
        """
        self.db = db

    def upsert(
        self,
        proposicao_id: int,
        resultado: EnriquecimentoOutput,
        modelo: str,
        versao_prompt: str,
        tokens_input: int | None = None,
        tokens_output: int | None = None,
        confianca_threshold: float = 0.5,
    ) -> EnriquecimentoLLM:
        """Insere ou atualiza um enriquecimento LLM de forma idempotente.

        Busca registro existente pela constraint UNIQUE (proposicao_id, versao_prompt).
        Se encontrado, atualiza os campos. Se não, insere novo registro.
        Abordagem dialect-agnostic (funciona com SQLite e PostgreSQL).

        Args:
            proposicao_id: ID da proposição enriquecida.
            resultado: Output estruturado do LLM.
            modelo: Nome do modelo LLM utilizado.
            versao_prompt: Versão do prompt utilizado.
            tokens_input: Tokens de entrada consumidos (opcional).
            tokens_output: Tokens de saída consumidos (opcional).
            confianca_threshold: Threshold de confiança para necessita_revisao.

        Returns:
            EnriquecimentoLLM: Registro inserido ou atualizado.
        """
        impacto_json = json.dumps(resultado.impacto_cidadao, ensure_ascii=False)
        necessita_revisao = resultado.confianca < confianca_threshold

        existing = (
            self.db.execute(
                select(EnriquecimentoLLM).where(
                    EnriquecimentoLLM.proposicao_id == proposicao_id,
                    EnriquecimentoLLM.versao_prompt == versao_prompt,
                )
            )
            .scalar_one_or_none()
        )

        if existing:
            existing.modelo = modelo
            existing.headline = resultado.headline
            existing.resumo_simples = resultado.resumo_simples
            existing.impacto_cidadao = impacto_json
            existing.confianca = resultado.confianca
            existing.necessita_revisao = necessita_revisao
            existing.tokens_input = tokens_input
            existing.tokens_output = tokens_output
            record = existing
        else:
            record = EnriquecimentoLLM(
                proposicao_id=proposicao_id,
                modelo=modelo,
                versao_prompt=versao_prompt,
                headline=resultado.headline,
                resumo_simples=resultado.resumo_simples,
                impacto_cidadao=impacto_json,
                confianca=resultado.confianca,
                necessita_revisao=necessita_revisao,
                tokens_input=tokens_input,
                tokens_output=tokens_output,
            )
            self.db.add(record)

        self.db.commit()
        self.db.refresh(record)

        logger.info(
            "Upsert enriquecimento: proposicao_id=%d, versao_prompt=%s, confianca=%.2f",
            proposicao_id,
            versao_prompt,
            resultado.confianca,
        )

        return record

    def get_pendentes(self, versao_prompt: str) -> list[Proposicao]:
        """Retorna proposições que ainda não possuem enriquecimento na versão especificada.

        Usa subquery NOT IN para filtrar proposições sem enriquecimento
        para a versão de prompt informada.

        Args:
            versao_prompt: Versão do prompt a verificar.

        Returns:
            Lista de Proposicao sem enriquecimento na versão especificada.
        """
        subquery = (
            select(EnriquecimentoLLM.proposicao_id)
            .where(EnriquecimentoLLM.versao_prompt == versao_prompt)
            .scalar_subquery()
        )

        stmt = select(Proposicao).where(Proposicao.id.not_in(subquery))

        result = self.db.execute(stmt).scalars().all()

        logger.info(
            "Proposições pendentes para versao_prompt=%s: %d encontradas",
            versao_prompt,
            len(result),
        )

        return list(result)

    def get_by_proposicao(self, proposicao_id: int) -> EnriquecimentoLLM | None:
        """Retorna o enriquecimento mais recente de uma proposição.

        Busca pelo enriquecimento com maior gerado_em para a proposição
        informada, retornando None se não existir.

        Args:
            proposicao_id: ID da proposição.

        Returns:
            EnriquecimentoLLM mais recente ou None se não encontrado.
        """
        stmt = (
            select(EnriquecimentoLLM)
            .where(EnriquecimentoLLM.proposicao_id == proposicao_id)
            .order_by(EnriquecimentoLLM.gerado_em.desc())
            .limit(1)
        )
        return self.db.execute(stmt).scalar_one_or_none()
