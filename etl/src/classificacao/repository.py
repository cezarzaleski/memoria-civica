"""Repository pattern para persistência do domínio de Classificação Cívica.

Encapsula operações de acesso a dados para categorias cívicas e
vínculos proposição-categoria, usando INSERT...ON CONFLICT DO UPDATE
(PostgreSQL) para upsert idempotente.
"""

import logging

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from .models import CategoriaCivica, ProposicaoCategoria
from .schemas import ProposicaoCategoriaCreate

logger = logging.getLogger(__name__)

# Dados de seed para as 9 categorias cívicas
CATEGORIAS_SEED = [
    {"codigo": "GASTOS_PUBLICOS", "nome": "Gastos Públicos", "descricao": None, "icone": "💰"},
    {"codigo": "TRIBUTACAO_AUMENTO", "nome": "Aumento de Tributos", "descricao": None, "icone": "📈"},
    {"codigo": "TRIBUTACAO_ISENCAO", "nome": "Isenção Tributária", "descricao": None, "icone": "🏷️"},
    {"codigo": "BENEFICIOS_CATEGORIAS", "nome": "Benefícios para Categorias", "descricao": None, "icone": "👔"},
    {"codigo": "DIREITOS_SOCIAIS", "nome": "Direitos Sociais", "descricao": None, "icone": "🏥"},
    {"codigo": "SEGURANCA_JUSTICA", "nome": "Segurança e Justiça", "descricao": None, "icone": "⚖️"},
    {"codigo": "MEIO_AMBIENTE", "nome": "Meio Ambiente", "descricao": None, "icone": "🌿"},
    {"codigo": "REGULACAO_ECONOMICA", "nome": "Regulação Econômica", "descricao": None, "icone": "🏭"},
    {"codigo": "POLITICA_INSTITUCIONAL", "nome": "Política Institucional", "descricao": None, "icone": "🏛️"},
]


class CategoriaCivicaRepository:
    """Repository para operações com a tabela categorias_civicas.

    Gerencia a tabela lookup de categorias de impacto cívico,
    incluindo seed idempotente das 9 categorias padrão.

    Attributes:
        db: Sessão SQLAlchemy injetada via dependency injection
    """

    def __init__(self, db: Session) -> None:
        """Inicializa o repository com uma sessão de banco de dados.

        Args:
            db: Sessão SQLAlchemy para executar queries
        """
        self.db = db

    def get_all(self) -> list[CategoriaCivica]:
        """Retorna todas as categorias cívicas.

        Returns:
            Lista com todas as categorias cívicas persistidas
        """
        stmt = select(CategoriaCivica)
        return self.db.execute(stmt).scalars().all()

    def get_by_codigo(self, codigo: str) -> CategoriaCivica | None:
        """Busca uma categoria pelo código.

        Args:
            codigo: Código da categoria (ex: "GASTOS_PUBLICOS")

        Returns:
            CategoriaCivica se encontrada, None caso contrário
        """
        stmt = select(CategoriaCivica).where(CategoriaCivica.codigo == codigo)
        return self.db.execute(stmt).scalar_one_or_none()

    def seed(self) -> int:
        """Popula tabela lookup com 9 categorias cívicas.

        Idempotente via INSERT...ON CONFLICT(codigo) DO NOTHING.
        Seguro para ser chamado múltiplas vezes sem duplicar dados.

        Returns:
            Quantidade de categorias inseridas (0 se já existiam)
        """
        stmt = pg_insert(CategoriaCivica).values(CATEGORIAS_SEED)
        stmt = stmt.on_conflict_do_nothing(index_elements=["codigo"])
        result = self.db.execute(stmt)
        self.db.commit()
        return result.rowcount


class ProposicaoCategoriaRepository:
    """Repository para operações com a junction table proposicoes_categorias.

    Usa INSERT...ON CONFLICT DO UPDATE (PostgreSQL) para bulk upsert
    idempotente de classificações proposição-categoria.

    Attributes:
        db: Sessão SQLAlchemy injetada via dependency injection
    """

    def __init__(self, db: Session) -> None:
        """Inicializa o repository com uma sessão de banco de dados.

        Args:
            db: Sessão SQLAlchemy para executar queries
        """
        self.db = db

    def bulk_upsert(self, records: list[ProposicaoCategoriaCreate]) -> int:
        """Insere ou atualiza classificações proposição-categoria em lote.

        Usa INSERT...ON CONFLICT(proposicao_id, categoria_id, origem) DO UPDATE
        para garantir idempotência sem CASCADE deletes.

        Args:
            records: Lista de schemas ProposicaoCategoriaCreate validados

        Returns:
            Quantidade de registros processados
        """
        if not records:
            return 0

        values = [record.model_dump() for record in records]
        stmt = pg_insert(ProposicaoCategoria).values(values)
        stmt = stmt.on_conflict_do_update(
            index_elements=["proposicao_id", "categoria_id", "origem"],
            set_={"confianca": stmt.excluded.confianca},
        )
        self.db.execute(stmt)
        self.db.commit()
        return len(values)

    def get_by_proposicao(self, proposicao_id: int) -> list[ProposicaoCategoria]:
        """Retorna todas as categorias de uma proposição.

        Args:
            proposicao_id: ID da proposição

        Returns:
            Lista de ProposicaoCategoria da proposição especificada
        """
        stmt = select(ProposicaoCategoria).where(ProposicaoCategoria.proposicao_id == proposicao_id)
        return self.db.execute(stmt).scalars().all()

    def get_by_categoria(self, categoria_id: int) -> list[ProposicaoCategoria]:
        """Retorna todas as proposições de uma categoria.

        Args:
            categoria_id: ID da categoria

        Returns:
            Lista de ProposicaoCategoria da categoria especificada
        """
        stmt = select(ProposicaoCategoria).where(ProposicaoCategoria.categoria_id == categoria_id)
        return self.db.execute(stmt).scalars().all()

    def delete_by_origem(self, origem: str) -> int:
        """Remove classificações por origem para re-classificação.

        Útil para limpar classificações de uma origem específica (ex: "regra")
        antes de re-classificar, preservando classificações de outras origens
        (ex: "llm").

        Args:
            origem: Origem das classificações a remover (ex: "regra", "llm")

        Returns:
            Quantidade de registros removidos
        """
        stmt = delete(ProposicaoCategoria).where(ProposicaoCategoria.origem == origem)
        result = self.db.execute(stmt)
        self.db.commit()
        return result.rowcount
