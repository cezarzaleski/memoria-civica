"""Repository pattern para persistência do domínio de Deputados.

Encapsula operações CRUD e operações em lote como bulk_upsert
no banco de dados, isolando a lógica de acesso de dados.
"""


from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Deputado
from .schemas import DeputadoCreate


class DeputadoRepository:
    """Repository para operações com a tabela deputados.

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
            >>> repo = DeputadoRepository(db)
        """
        self.db = db

    def create(self, deputado: DeputadoCreate) -> Deputado:
        """Cria e persiste um novo deputado.

        Args:
            deputado: Schema com dados validados do deputado

        Returns:
            Deputado: Instância persistida com id do banco de dados

        Examples:
            >>> from src.deputados.schemas import DeputadoCreate
            >>> dep_create = DeputadoCreate(
            ...     id=123, nome="João", partido="PT", uf="SP"
            ... )
            >>> created = repo.create(dep_create)
            >>> created.id
            123
        """
        db_deputado = Deputado(
            id=deputado.id,
            nome=deputado.nome,
            partido=deputado.partido,
            uf=deputado.uf,
            foto_url=deputado.foto_url,
            email=deputado.email,
        )
        self.db.add(db_deputado)
        self.db.commit()
        self.db.refresh(db_deputado)
        return db_deputado

    def get_by_id(self, deputado_id: int) -> Deputado | None:
        """Busca um deputado pelo ID.

        Args:
            deputado_id: ID do deputado a buscar

        Returns:
            Deputado se encontrado, None caso contrário

        Examples:
            >>> dep = repo.get_by_id(123)
            >>> dep.nome if dep else "Não encontrado"
            'João Silva'
        """
        stmt = select(Deputado).where(Deputado.id == deputado_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_uf(self, uf: str) -> list[Deputado]:
        """Busca todos os deputados de uma UF.

        Args:
            uf: Unidade federativa (2 caracteres)

        Returns:
            Lista de deputados da UF

        Examples:
            >>> deps = repo.get_by_uf("SP")
            >>> len(deps) > 0
            True
        """
        stmt = select(Deputado).where(Deputado.uf == uf)
        return self.db.execute(stmt).scalars().all()

    def get_all(self) -> list[Deputado]:
        """Busca todos os deputados.

        Returns:
            Lista com todos os deputados persistidos

        Examples:
            >>> todos = repo.get_all()
            >>> len(todos) > 0
            True
        """
        stmt = select(Deputado)
        return self.db.execute(stmt).scalars().all()

    def bulk_upsert(self, deputados: list[DeputadoCreate]) -> int:
        """Insere ou atualiza múltiplos deputados (upsert).

        Opera com idempotência: pode ser chamado múltiplas vezes com
        o mesmo CSV sem criar duplicatas. Usa a estratégia de deletar
        existentes e reinserir para evitar conflitos.

        Args:
            deputados: Lista de schemas DeputadoCreate validados

        Returns:
            Quantidade de deputados inseridos/atualizados

        Examples:
            >>> deps = [
            ...     DeputadoCreate(id=1, nome="João", partido="PT", uf="SP"),
            ...     DeputadoCreate(id=2, nome="Maria", partido="PDT", uf="RJ"),
            ... ]
            >>> count = repo.bulk_upsert(deps)
            >>> count
            2
        """
        if not deputados:
            return 0

        # IDs dos deputados a inserir
        ids = [d.id for d in deputados]

        # Deletar deputados existentes com esses IDs (upsert strategy)
        stmt_delete = select(Deputado).where(Deputado.id.in_(ids))
        existing = self.db.execute(stmt_delete).scalars().all()
        for existing_dep in existing:
            self.db.delete(existing_dep)

        # Inserir novos deputados
        db_deputados = [
            Deputado(
                id=d.id,
                nome=d.nome,
                partido=d.partido,
                uf=d.uf,
                foto_url=d.foto_url,
                email=d.email,
            )
            for d in deputados
        ]
        self.db.add_all(db_deputados)
        self.db.commit()

        return len(db_deputados)

    def delete_by_id(self, deputado_id: int) -> bool:
        """Deleta um deputado pelo ID.

        Args:
            deputado_id: ID do deputado a deletar

        Returns:
            True se deletou algo, False se não encontrou

        Examples:
            >>> deleted = repo.delete_by_id(123)
            >>> deleted
            True
        """
        stmt = select(Deputado).where(Deputado.id == deputado_id)
        deputado = self.db.execute(stmt).scalar_one_or_none()
        if deputado:
            self.db.delete(deputado)
            self.db.commit()
            return True
        return False
