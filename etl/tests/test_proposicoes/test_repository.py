"""Testes para Repository do domínio de Proposições.

Validam operações CRUD, get_by_tipo e bulk_upsert, incluindo idempotência.
"""

from src.proposicoes.models import Proposicao
from src.proposicoes.schemas import ProposicaoCreate


class TestProposicaoRepository:
    """Testes para ProposicaoRepository."""

    def test_create_persists_proposicao(self, proposicao_repository, db_session):
        """Test: create() persiste proposição e retorna com id."""
        proposicao_create = ProposicaoCreate(
            id=1,
            tipo="PL",
            numero=123,
            ano=2024,
            ementa="Lei que trata de educação pública",
            autor_id=456,
        )

        resultado = proposicao_repository.create(proposicao_create)

        assert resultado.id == 1
        assert resultado.tipo == "PL"
        assert resultado.numero == 123
        assert resultado.ano == 2024
        assert resultado.ementa == "Lei que trata de educação pública"
        assert resultado.autor_id == 456

        # Verificar que foi persistido no banco
        from_db = db_session.query(Proposicao).filter(Proposicao.id == 1).first()
        assert from_db is not None
        assert from_db.tipo == "PL"

    def test_get_by_id_returns_existing(self, proposicao_repository):
        """Test: get_by_id() retorna proposição existente."""
        # Criar primeiro
        proposicao_create = ProposicaoCreate(
            id=2,
            tipo="PEC",
            numero=1,
            ano=2024,
            ementa="Emenda constitucional",
        )
        proposicao_repository.create(proposicao_create)

        # Buscar
        resultado = proposicao_repository.get_by_id(2)

        assert resultado is not None
        assert resultado.id == 2
        assert resultado.tipo == "PEC"
        assert resultado.numero == 1

    def test_get_by_id_returns_none_for_nonexistent(self, proposicao_repository):
        """Test: get_by_id() retorna None para id inexistente."""
        resultado = proposicao_repository.get_by_id(99999)
        assert resultado is None

    def test_get_by_tipo_returns_proposicoes_of_type(self, proposicao_repository):
        """Test: get_by_tipo() retorna proposições do tipo."""
        # Criar algumas proposições
        proposicoes = [
            ProposicaoCreate(
                id=100,
                tipo="PL",
                numero=1,
                ano=2024,
                ementa="Lei 1",
            ),
            ProposicaoCreate(
                id=101,
                tipo="PL",
                numero=2,
                ano=2024,
                ementa="Lei 2",
            ),
            ProposicaoCreate(
                id=102,
                tipo="PEC",
                numero=1,
                ano=2024,
                ementa="Emenda",
            ),
        ]
        for p in proposicoes:
            proposicao_repository.create(p)

        # Buscar por tipo
        pl_proposicoes = proposicao_repository.get_by_tipo("PL")

        assert len(pl_proposicoes) == 2
        assert all(p.tipo == "PL" for p in pl_proposicoes)

    def test_get_all_returns_all_proposicoes(self, proposicao_repository):
        """Test: get_all() retorna todas as proposições."""
        # Criar algumas proposições
        proposicoes = [
            ProposicaoCreate(
                id=200,
                tipo="PL",
                numero=100,
                ano=2024,
                ementa="Lei 1",
            ),
            ProposicaoCreate(
                id=201,
                tipo="PEC",
                numero=1,
                ano=2024,
                ementa="Emenda",
            ),
            ProposicaoCreate(
                id=202,
                tipo="MP",
                numero=1,
                ano=2024,
                ementa="Medida provisória",
            ),
        ]
        for p in proposicoes:
            proposicao_repository.create(p)

        # Buscar todas
        todas = proposicao_repository.get_all()

        assert len(todas) == 3
        assert all(isinstance(p, Proposicao) for p in todas)

    def test_bulk_upsert_inserts_multiple(self, proposicao_repository):
        """Test: bulk_upsert() insere múltiplas proposições."""
        proposicoes = [
            ProposicaoCreate(
                id=300,
                tipo="PL",
                numero=1,
                ano=2024,
                ementa="Lei 1",
            ),
            ProposicaoCreate(
                id=301,
                tipo="PLP",
                numero=1,
                ano=2024,
                ementa="Lei complementar",
            ),
            ProposicaoCreate(
                id=302,
                tipo="PDC",
                numero=1,
                ano=2024,
                ementa="Decreto legislativo",
            ),
        ]

        count = proposicao_repository.bulk_upsert(proposicoes)

        assert count == 3

        # Verificar que foram inseridas
        todas = proposicao_repository.get_all()
        assert len(todas) == 3

    def test_bulk_upsert_idempotent(self, proposicao_repository):
        """Test: bulk_upsert() não duplica em re-execução (idempotência)."""
        proposicoes = [
            ProposicaoCreate(
                id=400,
                tipo="PL",
                numero=50,
                ano=2024,
                ementa="Lei 50",
            ),
            ProposicaoCreate(
                id=401,
                tipo="MP",
                numero=1,
                ano=2024,
                ementa="Medida",
            ),
        ]

        # Primeira execução
        count1 = proposicao_repository.bulk_upsert(proposicoes)
        assert count1 == 2

        # Segunda execução (deveria atualizar, não duplicar)
        count2 = proposicao_repository.bulk_upsert(proposicoes)
        assert count2 == 2

        # Total deve ser 2, não 4
        todas = proposicao_repository.get_all()
        assert len(todas) == 2

    def test_bulk_upsert_overwrites_existing(self, proposicao_repository):
        """Test: bulk_upsert() sobrescreve proposições existentes."""
        # Inserir primeiro
        proposicao1 = ProposicaoCreate(
            id=500,
            tipo="PL",
            numero=100,
            ano=2024,
            ementa="Ementa original",
        )
        proposicao_repository.create(proposicao1)

        # Bulk upsert com mesmo ID mas dados diferentes
        proposicao_atualizada = ProposicaoCreate(
            id=500,
            tipo="PEC",
            numero=200,
            ano=2025,
            ementa="Ementa atualizada",
        )
        count = proposicao_repository.bulk_upsert([proposicao_atualizada])

        assert count == 1

        # Verificar que foi atualizada
        resultado = proposicao_repository.get_by_id(500)
        assert resultado.tipo == "PEC"
        assert resultado.numero == 200
        assert resultado.ementa == "Ementa atualizada"

    def test_bulk_upsert_empty_list(self, proposicao_repository):
        """Test: bulk_upsert() com lista vazia retorna 0."""
        count = proposicao_repository.bulk_upsert([])
        assert count == 0

    def test_delete_by_id_removes_proposicao(self, proposicao_repository):
        """Test: delete_by_id() remove proposição."""
        # Criar
        proposicao = ProposicaoCreate(
            id=600,
            tipo="PL",
            numero=1,
            ano=2024,
            ementa="Lei 1",
        )
        proposicao_repository.create(proposicao)

        # Deletar
        deleted = proposicao_repository.delete_by_id(600)
        assert deleted is True

        # Verificar que foi removida
        resultado = proposicao_repository.get_by_id(600)
        assert resultado is None

    def test_delete_by_id_returns_false_for_nonexistent(self, proposicao_repository):
        """Test: delete_by_id() retorna False para id inexistente."""
        deleted = proposicao_repository.delete_by_id(88888)
        assert deleted is False

    def test_proposicao_with_null_autor_id(self, proposicao_repository):
        """Test: proposição sem autor (autor_id=NULL) é aceita."""
        proposicao = ProposicaoCreate(
            id=700,
            tipo="MP",
            numero=1,
            ano=2024,
            ementa="Medida provisória órfã",
            autor_id=None,
        )
        resultado = proposicao_repository.create(proposicao)

        assert resultado.autor_id is None

        # Verificar que foi persistida
        from_db = proposicao_repository.get_by_id(700)
        assert from_db is not None
        assert from_db.autor_id is None
