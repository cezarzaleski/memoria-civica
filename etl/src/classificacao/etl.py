"""Pipeline ETL para classificação cívica de proposições legislativas.

Fase 3 do pipeline (Enriquecimento): lê proposições do banco,
aplica classificação por regex via ClassificadorCivico, e persiste
os vínculos proposição-categoria. Step NÃO-CRÍTICO: falha gera
warning mas não interrompe o pipeline principal.
"""

import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.proposicoes.models import Proposicao
from src.shared.database import get_db

from .engine import ClassificadorCivico
from .patterns import CIVIC_PATTERNS
from .repository import CategoriaCivicaRepository, ProposicaoCategoriaRepository
from .schemas import ProposicaoCategoriaCreate

logger = logging.getLogger(__name__)


def run_classificacao_etl(db: Session | None = None) -> int:
    """Executa o pipeline ETL de classificação cívica de proposições.

    Orquestra:
    1. Seed idempotente das categorias cívicas
    2. Busca de proposições com ementa não-nula
    3. Classificação via regex (ClassificadorCivico)
    4. Limpeza de classificações anteriores de origem "regra"
    5. Persistência das novas classificações via bulk_upsert

    Step NÃO-CRÍTICO: falha gera warning mas não interrompe o pipeline.

    Args:
        db: Sessão opcional (se None, usa get_db())

    Returns:
        Quantidade de pares (proposição, categoria) criados
    """
    logger.info("Iniciando ETL classificacao civica...")

    if db is None:
        with get_db() as db:
            return _run_classificacao_etl_impl(db)
    else:
        return _run_classificacao_etl_impl(db)


def _run_classificacao_etl_impl(db: Session) -> int:
    """Implementação interna do ETL de classificação cívica.

    Args:
        db: Sessão de banco de dados

    Returns:
        Quantidade de pares (proposição, categoria) criados
    """
    # 1. Seed idempotente das categorias cívicas
    cat_repo = CategoriaCivicaRepository(db)
    seed_count = cat_repo.seed()
    if seed_count > 0:
        logger.info(f"Seed: {seed_count} categorias civicas inseridas")
    else:
        logger.info("Seed: categorias civicas ja existem")

    # 2. Construir mapa codigo → id das categorias
    todas_categorias = cat_repo.get_all()
    codigo_para_id: dict[str, int] = {c.codigo: c.id for c in todas_categorias}

    if not codigo_para_id:
        logger.warning("Nenhuma categoria civica encontrada apos seed — abortando classificacao")
        return 0

    logger.info(f"Categorias disponiveis: {len(codigo_para_id)}")

    # 3. Buscar proposições com ementa não-nula
    stmt = select(Proposicao).where(
        Proposicao.ementa.isnot(None),
        Proposicao.ementa != "",
    )
    proposicoes = db.execute(stmt).scalars().all()

    total_proposicoes = len(proposicoes)
    if total_proposicoes == 0:
        logger.info("Nenhuma proposicao com ementa encontrada — nada a classificar")
        return 0

    logger.info(f"Proposicoes com ementa: {total_proposicoes}")

    # 4. Classificar proposições com o engine de regex
    classificador = ClassificadorCivico(CIVIC_PATTERNS)

    novas_classificacoes: list[ProposicaoCategoriaCreate] = []
    proposicoes_classificadas = 0
    proposicoes_sem_match = 0

    for prop in proposicoes:
        try:
            matches = classificador.classificar(prop.ementa or "")

            if matches:
                proposicoes_classificadas += 1
                for match in matches:
                    categoria_id = codigo_para_id.get(match.categoria_codigo)
                    if categoria_id is None:
                        logger.warning(
                            f"Categoria '{match.categoria_codigo}' nao encontrada "
                            f"no banco — ignorando match para proposicao {prop.id}"
                        )
                        continue

                    novas_classificacoes.append(
                        ProposicaoCategoriaCreate(
                            proposicao_id=prop.id,
                            categoria_id=categoria_id,
                            origem="regra",
                            confianca=match.confianca,
                        )
                    )
            else:
                proposicoes_sem_match += 1

        except Exception as e:
            logger.warning(f"Erro ao classificar proposicao {prop.id}: {e}")
            proposicoes_sem_match += 1

    logger.info(
        f"Classificacao: {proposicoes_classificadas} proposicoes classificadas, "
        f"{proposicoes_sem_match} sem match"
    )

    # 5. Limpar classificações anteriores de origem "regra"
    pc_repo = ProposicaoCategoriaRepository(db)
    deleted = pc_repo.delete_by_origem("regra")
    if deleted > 0:
        logger.info(f"Removidas {deleted} classificacoes anteriores de origem 'regra'")

    # 6. Persistir novas classificações
    if novas_classificacoes:
        loaded = pc_repo.bulk_upsert(novas_classificacoes)
        logger.info(
            f"ETL classificacao concluido: {loaded} pares (proposicao, categoria) criados"
        )
        return loaded
    else:
        logger.info("ETL classificacao concluido: nenhuma classificacao gerada")
        return 0
