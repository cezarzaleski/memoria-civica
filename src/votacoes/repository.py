"""Repository pattern para persistência do domínio de Votações.

Encapsula operações CRUD e operações em lote como bulk_upsert
no banco de dados, isolando a lógica de acesso de dados.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Votacao, Voto
from .schemas import VotacaoCreate, VotoCreate


class VotacaoRepository:
    """Repository para operações com a tabela votacoes.

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
            >>> repo = VotacaoRepository(db)
        """
        self.db = db

    def create(self, votacao: VotacaoCreate) -> Votacao:
        """Cria e persiste uma nova votação.

        Args:
            votacao: Schema com dados validados da votação

        Returns:
            Votacao: Instância persistida com id do banco de dados

        Examples:
            >>> from src.votacoes.schemas import VotacaoCreate, ResultadoVotacao
            >>> from datetime import datetime
            >>> votacao_create = VotacaoCreate(
            ...     id=1, proposicao_id=123,
            ...     data_hora=datetime(2024, 1, 15, 14, 30, 0),
            ...     resultado=ResultadoVotacao.APROVADO
            ... )
            >>> created = repo.create(votacao_create)
            >>> created.id
            1
        """
        db_votacao = Votacao(
            id=votacao.id,
            proposicao_id=votacao.proposicao_id,
            data_hora=votacao.data_hora,
            resultado=votacao.resultado,
        )
        self.db.add(db_votacao)
        self.db.commit()
        self.db.refresh(db_votacao)
        return db_votacao

    def get_by_id(self, votacao_id: int) -> Votacao | None:
        """Busca uma votação pelo ID.

        Args:
            votacao_id: ID da votação a buscar

        Returns:
            Votacao se encontrada, None caso contrário

        Examples:
            >>> votacao = repo.get_by_id(1)
            >>> votacao.resultado if votacao else "Não encontrada"
            'Aprovado'
        """
        stmt = select(Votacao).where(Votacao.id == votacao_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_proposicao(self, proposicao_id: int) -> list[Votacao]:
        """Busca todas as votações de uma proposição.

        Args:
            proposicao_id: ID da proposição

        Returns:
            Lista de votações da proposição especificada

        Examples:
            >>> votacoes = repo.get_by_proposicao(123)
            >>> len(votacoes) > 0
            True
        """
        stmt = select(Votacao).where(Votacao.proposicao_id == proposicao_id)
        return self.db.execute(stmt).scalars().all()

    def get_all(self) -> list[Votacao]:
        """Busca todas as votações.

        Returns:
            Lista com todas as votações persistidas

        Examples:
            >>> todas = repo.get_all()
            >>> len(todas) > 0
            True
        """
        stmt = select(Votacao)
        return self.db.execute(stmt).scalars().all()

    def bulk_upsert(self, votacoes: list[VotacaoCreate]) -> int:
        """Insere ou atualiza múltiplas votações (upsert).

        Opera com idempotência: pode ser chamado múltiplas vezes com
        o mesmo CSV sem criar duplicatas. Usa a estratégia de deletar
        existentes e reinserir para evitar conflitos.

        Args:
            votacoes: Lista de schemas VotacaoCreate validados

        Returns:
            Quantidade de votações inseridas/atualizadas

        Examples:
            >>> from src.votacoes.schemas import VotacaoCreate, ResultadoVotacao
            >>> from datetime import datetime
            >>> votacoes = [
            ...     VotacaoCreate(
            ...         id=1, proposicao_id=123,
            ...         data_hora=datetime(2024, 1, 15, 14, 30, 0),
            ...         resultado=ResultadoVotacao.APROVADO
            ...     ),
            ... ]
            >>> count = repo.bulk_upsert(votacoes)
            >>> count
            1
        """
        if not votacoes:
            return 0

        # IDs das votações a inserir
        ids = [v.id for v in votacoes]

        # Deletar votações existentes com esses IDs (upsert strategy)
        stmt_delete = select(Votacao).where(Votacao.id.in_(ids))
        existing = self.db.execute(stmt_delete).scalars().all()
        for existing_votacao in existing:
            self.db.delete(existing_votacao)

        # Inserir novas votações
        db_votacoes = [
            Votacao(
                id=v.id,
                proposicao_id=v.proposicao_id,
                data_hora=v.data_hora,
                resultado=v.resultado,
            )
            for v in votacoes
        ]
        self.db.add_all(db_votacoes)
        self.db.commit()

        return len(db_votacoes)

    def delete_by_id(self, votacao_id: int) -> bool:
        """Deleta uma votação pelo ID.

        Args:
            votacao_id: ID da votação a deletar

        Returns:
            True se deletou algo, False se não encontrou

        Examples:
            >>> deleted = repo.delete_by_id(1)
            >>> deleted
            True
        """
        stmt = select(Votacao).where(Votacao.id == votacao_id)
        votacao = self.db.execute(stmt).scalar_one_or_none()
        if votacao:
            self.db.delete(votacao)
            self.db.commit()
            return True
        return False


class VotoRepository:
    """Repository para operações com a tabela votos.

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
            >>> repo = VotoRepository(db)
        """
        self.db = db

    def create(self, voto: VotoCreate) -> Voto:
        """Cria e persiste um novo voto.

        Args:
            voto: Schema com dados validados do voto

        Returns:
            Voto: Instância persistida com id do banco de dados

        Examples:
            >>> from src.votacoes.schemas import VotoCreate, TipoVoto
            >>> voto_create = VotoCreate(
            ...     id=1, votacao_id=123, deputado_id=456,
            ...     voto=TipoVoto.SIM
            ... )
            >>> created = repo.create(voto_create)
            >>> created.id
            1
        """
        db_voto = Voto(
            id=voto.id,
            votacao_id=voto.votacao_id,
            deputado_id=voto.deputado_id,
            voto=voto.voto,
        )
        self.db.add(db_voto)
        self.db.commit()
        self.db.refresh(db_voto)
        return db_voto

    def get_by_id(self, voto_id: int) -> Voto | None:
        """Busca um voto pelo ID.

        Args:
            voto_id: ID do voto a buscar

        Returns:
            Voto se encontrado, None caso contrário

        Examples:
            >>> voto = repo.get_by_id(1)
            >>> voto.voto if voto else "Não encontrado"
            'Sim'
        """
        stmt = select(Voto).where(Voto.id == voto_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_votacao(self, votacao_id: int) -> list[Voto]:
        """Busca todos os votos de uma votação.

        Args:
            votacao_id: ID da votação

        Returns:
            Lista de votos da votação especificada

        Examples:
            >>> votos = repo.get_by_votacao(123)
            >>> len(votos) > 0
            True
        """
        stmt = select(Voto).where(Voto.votacao_id == votacao_id)
        return self.db.execute(stmt).scalars().all()

    def get_by_deputado(self, deputado_id: int) -> list[Voto]:
        """Busca todos os votos de um deputado.

        Args:
            deputado_id: ID do deputado

        Returns:
            Lista de votos do deputado especificado

        Examples:
            >>> votos = repo.get_by_deputado(456)
            >>> len(votos) > 0
            True
        """
        stmt = select(Voto).where(Voto.deputado_id == deputado_id)
        return self.db.execute(stmt).scalars().all()

    def get_all(self) -> list[Voto]:
        """Busca todos os votos.

        Returns:
            Lista com todos os votos persistidos

        Examples:
            >>> todos = repo.get_all()
            >>> len(todos) > 0
            True
        """
        stmt = select(Voto)
        return self.db.execute(stmt).scalars().all()

    def bulk_insert(self, votos: list[VotoCreate]) -> int:
        """Insere múltiplos votos em lote.

        Otimizado para inserção em massa sem necessidade de idempotência
        (votos normalmente não são duplicados de forma natural).

        Args:
            votos: Lista de schemas VotoCreate validados

        Returns:
            Quantidade de votos inseridos

        Examples:
            >>> from src.votacoes.schemas import VotoCreate, TipoVoto
            >>> votos = [
            ...     VotoCreate(id=1, votacao_id=123, deputado_id=456, voto=TipoVoto.SIM),
            ...     VotoCreate(id=2, votacao_id=123, deputado_id=789, voto=TipoVoto.NAO),
            ... ]
            >>> count = repo.bulk_insert(votos)
            >>> count
            2
        """
        if not votos:
            return 0

        db_votos = [
            Voto(
                id=v.id,
                votacao_id=v.votacao_id,
                deputado_id=v.deputado_id,
                voto=v.voto,
            )
            for v in votos
        ]
        self.db.add_all(db_votos)
        self.db.commit()

        return len(db_votos)

    def delete_by_id(self, voto_id: int) -> bool:
        """Deleta um voto pelo ID.

        Args:
            voto_id: ID do voto a deletar

        Returns:
            True se deletou algo, False se não encontrou

        Examples:
            >>> deleted = repo.delete_by_id(1)
            >>> deleted
            True
        """
        stmt = select(Voto).where(Voto.id == voto_id)
        voto = self.db.execute(stmt).scalar_one_or_none()
        if voto:
            self.db.delete(voto)
            self.db.commit()
            return True
        return False
