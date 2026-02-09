"""Repository pattern para persistência do domínio de Proposições.

Encapsula operações CRUD e operações em lote como bulk_upsert
no banco de dados, isolando a lógica de acesso de dados.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Proposicao
from .schemas import ProposicaoCreate


class ProposicaoRepository:
    """Repository para operações com a tabela proposicoes.

    Padrão Repository que encapsula queries e garante que a lógica
    de acesso a dados fica centralizada e testável.

    Attributes:
        db: Sessão SQLAlchemy injetada via dependency injection
    """

    def __init__(self, db: Session) -> None:
        """Inicializa o repository com uma sessão de banco de dados.

        Args:
            db: Sessão SQLAlchemy para executar queries

        Examples:
            >>> from src.shared.database import SessionLocal
            >>> db = SessionLocal()
            >>> repo = ProposicaoRepository(db)
        """
        self.db = db

    def create(self, proposicao: ProposicaoCreate) -> Proposicao:
        """Cria e persiste uma nova proposição.

        Args:
            proposicao: Schema com dados validados da proposição

        Returns:
            Proposicao: Instância persistida com id do banco de dados

        Examples:
            >>> from src.proposicoes.schemas import ProposicaoCreate
            >>> prop_create = ProposicaoCreate(
            ...     id=1, tipo="PL", numero=123, ano=2024,
            ...     ementa="Lei de educação", autor_id=456
            ... )
            >>> created = repo.create(prop_create)
            >>> created.id
            1
        """
        db_proposicao = Proposicao(
            id=proposicao.id,
            tipo=proposicao.tipo,
            numero=proposicao.numero,
            ano=proposicao.ano,
            ementa=proposicao.ementa,
            autor_id=proposicao.autor_id,
        )
        self.db.add(db_proposicao)
        self.db.commit()
        self.db.refresh(db_proposicao)
        return db_proposicao

    def get_by_id(self, proposicao_id: int) -> Proposicao | None:
        """Busca uma proposição pelo ID.

        Args:
            proposicao_id: ID da proposição a buscar

        Returns:
            Proposicao se encontrada, None caso contrário

        Examples:
            >>> prop = repo.get_by_id(1)
            >>> prop.tipo if prop else "Não encontrada"
            'PL'
        """
        stmt = select(Proposicao).where(Proposicao.id == proposicao_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_tipo(self, tipo: str) -> list[Proposicao]:
        """Busca todas as proposições de um tipo.

        Args:
            tipo: Tipo da proposição (PL, PEC, MP, etc)

        Returns:
            Lista de proposições do tipo especificado

        Examples:
            >>> props = repo.get_by_tipo("PL")
            >>> len(props) > 0
            True
        """
        stmt = select(Proposicao).where(Proposicao.tipo == tipo)
        return self.db.execute(stmt).scalars().all()

    def get_all(self) -> list[Proposicao]:
        """Busca todas as proposições.

        Returns:
            Lista com todas as proposições persistidas

        Examples:
            >>> todas = repo.get_all()
            >>> len(todas) > 0
            True
        """
        stmt = select(Proposicao)
        return self.db.execute(stmt).scalars().all()

    def bulk_upsert(self, proposicoes: list[ProposicaoCreate]) -> int:
        """Insere ou atualiza múltiplas proposições (upsert).

        Opera com idempotência: pode ser chamado múltiplas vezes com
        o mesmo CSV sem criar duplicatas. Usa a estratégia de deletar
        existentes e reinserir para evitar conflitos.

        Args:
            proposicoes: Lista de schemas ProposicaoCreate validados

        Returns:
            Quantidade de proposições inseridas/atualizadas

        Examples:
            >>> from src.proposicoes.schemas import ProposicaoCreate
            >>> props = [
            ...     ProposicaoCreate(
            ...         id=1, tipo="PL", numero=123,
            ...         ano=2024, ementa="Lei 1", autor_id=None
            ...     ),
            ...     ProposicaoCreate(
            ...         id=2, tipo="PEC", numero=1,
            ...         ano=2024, ementa="Emenda 1", autor_id=456
            ...     ),
            ... ]
            >>> count = repo.bulk_upsert(props)
            >>> count
            2
        """
        if not proposicoes:
            return 0

        # IDs das proposições a inserir
        ids = [p.id for p in proposicoes]

        # Deletar proposições existentes com esses IDs (upsert strategy)
        stmt_delete = select(Proposicao).where(Proposicao.id.in_(ids))
        existing = self.db.execute(stmt_delete).scalars().all()
        for existing_prop in existing:
            self.db.delete(existing_prop)

        # Inserir novas proposições
        db_proposicoes = [
            Proposicao(
                id=p.id,
                tipo=p.tipo,
                numero=p.numero,
                ano=p.ano,
                ementa=p.ementa,
                autor_id=p.autor_id,
            )
            for p in proposicoes
        ]
        self.db.add_all(db_proposicoes)
        self.db.commit()

        return len(db_proposicoes)

    def delete_by_id(self, proposicao_id: int) -> bool:
        """Deleta uma proposição pelo ID.

        Args:
            proposicao_id: ID da proposição a deletar

        Returns:
            True se deletou algo, False se não encontrou

        Examples:
            >>> deleted = repo.delete_by_id(1)
            >>> deleted
            True
        """
        stmt = select(Proposicao).where(Proposicao.id == proposicao_id)
        proposicao = self.db.execute(stmt).scalar_one_or_none()
        if proposicao:
            self.db.delete(proposicao)
            self.db.commit()
            return True
        return False
