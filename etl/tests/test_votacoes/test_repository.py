"""Testes para Repositories do domínio de Votações.

Validam operações CRUD, get_by_proposicao, get_by_votacao, e bulk operations.
"""

from datetime import datetime

from src.votacoes.models import Votacao, Voto
from src.votacoes.schemas import VotacaoCreate, VotoCreate


class TestVotacaoRepository:
    """Testes para VotacaoRepository."""

    def test_create_persists_votacao(self, votacao_repository, db_session):
        """Test: create() persiste votação e retorna com id."""
        votacao_create = VotacaoCreate(
            id=1,
            proposicao_id=123,
            data_hora=datetime(2024, 1, 15, 14, 30, 0),
            resultado="APROVADO",
        )

        resultado = votacao_repository.create(votacao_create)

        assert resultado.id == 1
        assert resultado.proposicao_id == 123
        assert resultado.data_hora == datetime(2024, 1, 15, 14, 30, 0)
        assert resultado.resultado == "APROVADO"

        # Verificar que foi persistida no banco
        from_db = db_session.query(Votacao).filter(Votacao.id == 1).first()
        assert from_db is not None
        assert from_db.proposicao_id == 123

    def test_get_by_id_returns_existing(self, votacao_repository):
        """Test: get_by_id() retorna votação existente."""
        # Criar primeiro
        votacao_create = VotacaoCreate(
            id=2,
            proposicao_id=456,
            data_hora=datetime(2024, 1, 16, 10, 15, 0),
            resultado="REJEITADO",
        )
        votacao_repository.create(votacao_create)

        # Buscar
        resultado = votacao_repository.get_by_id(2)

        assert resultado is not None
        assert resultado.id == 2
        assert resultado.proposicao_id == 456
        assert resultado.resultado == "REJEITADO"

    def test_get_by_id_returns_none_for_nonexistent(self, votacao_repository):
        """Test: get_by_id() retorna None para id inexistente."""
        resultado = votacao_repository.get_by_id(99999)
        assert resultado is None

    def test_get_by_proposicao_returns_votacoes(self, votacao_repository):
        """Test: get_by_proposicao() retorna votações de uma proposição."""
        # Criar votações para diferentes proposições
        votacoes = [
            VotacaoCreate(
                id=100,
                proposicao_id=111,
                data_hora=datetime(2024, 1, 15, 14, 30, 0),
                resultado="APROVADO",
            ),
            VotacaoCreate(
                id=101,
                proposicao_id=111,
                data_hora=datetime(2024, 1, 16, 10, 15, 0),
                resultado="REJEITADO",
            ),
            VotacaoCreate(
                id=102,
                proposicao_id=222,
                data_hora=datetime(2024, 1, 17, 16, 45, 0),
                resultado="APROVADO",
            ),
        ]
        for v in votacoes:
            votacao_repository.create(v)

        # Buscar votações de proposicao 111
        votacoes_111 = votacao_repository.get_by_proposicao(111)

        assert len(votacoes_111) == 2
        assert all(v.proposicao_id == 111 for v in votacoes_111)

    def test_get_all_returns_all_votacoes(self, votacao_repository):
        """Test: get_all() retorna todas as votações."""
        votacoes = [
            VotacaoCreate(
                id=200,
                proposicao_id=100,
                data_hora=datetime(2024, 1, 15, 14, 30, 0),
                resultado="APROVADO",
            ),
            VotacaoCreate(
                id=201,
                proposicao_id=101,
                data_hora=datetime(2024, 1, 16, 10, 15, 0),
                resultado="REJEITADO",
            ),
        ]
        for v in votacoes:
            votacao_repository.create(v)

        # Buscar todas
        todas = votacao_repository.get_all()

        assert len(todas) == 2
        assert all(isinstance(v, Votacao) for v in todas)

    def test_bulk_upsert_inserts_multiple(self, votacao_repository):
        """Test: bulk_upsert() insere múltiplas votações."""
        votacoes = [
            VotacaoCreate(
                id=300,
                proposicao_id=1,
                data_hora=datetime(2024, 1, 15, 14, 30, 0),
                resultado="APROVADO",
            ),
            VotacaoCreate(
                id=301,
                proposicao_id=2,
                data_hora=datetime(2024, 1, 16, 10, 15, 0),
                resultado="REJEITADO",
            ),
        ]

        count = votacao_repository.bulk_upsert(votacoes)

        assert count == 2

        # Verificar que foram inseridas
        todas = votacao_repository.get_all()
        assert len(todas) == 2

    def test_bulk_upsert_idempotent(self, votacao_repository):
        """Test: bulk_upsert() não duplica em re-execução (idempotência)."""
        votacoes = [
            VotacaoCreate(
                id=400,
                proposicao_id=1,
                data_hora=datetime(2024, 1, 15, 14, 30, 0),
                resultado="APROVADO",
            ),
        ]

        # Primeira execução
        count1 = votacao_repository.bulk_upsert(votacoes)
        assert count1 == 1

        # Segunda execução (deveria atualizar, não duplicar)
        count2 = votacao_repository.bulk_upsert(votacoes)
        assert count2 == 1

        # Total deve ser 1, não 2
        todas = votacao_repository.get_all()
        assert len(todas) == 1

    def test_delete_by_id_removes_votacao(self, votacao_repository):
        """Test: delete_by_id() remove votação."""
        # Criar votação
        votacao_create = VotacaoCreate(
            id=500,
            proposicao_id=1,
            data_hora=datetime(2024, 1, 15, 14, 30, 0),
            resultado="APROVADO",
        )
        votacao_repository.create(votacao_create)

        # Deletar
        deleted = votacao_repository.delete_by_id(500)

        assert deleted is True

        # Verificar que foi deletada
        resultado = votacao_repository.get_by_id(500)
        assert resultado is None

    def test_delete_by_id_returns_false_for_nonexistent(self, votacao_repository):
        """Test: delete_by_id() retorna False para id inexistente."""
        deleted = votacao_repository.delete_by_id(99999)
        assert deleted is False


class TestVotoRepository:
    """Testes para VotoRepository."""

    def test_create_persists_voto(self, voto_repository, db_session):
        """Test: create() persiste voto e retorna com id."""
        voto_create = VotoCreate(
            id=1,
            votacao_id=123,
            deputado_id=456,
            voto="SIM",
        )

        resultado = voto_repository.create(voto_create)

        assert resultado.id == 1
        assert resultado.votacao_id == 123
        assert resultado.deputado_id == 456
        assert resultado.voto == "SIM"

        # Verificar que foi persistido no banco
        from_db = db_session.query(Voto).filter(Voto.id == 1).first()
        assert from_db is not None
        assert from_db.votacao_id == 123

    def test_get_by_id_returns_existing(self, voto_repository):
        """Test: get_by_id() retorna voto existente."""
        # Criar primeiro
        voto_create = VotoCreate(
            id=2,
            votacao_id=456,
            deputado_id=789,
            voto="NAO",
        )
        voto_repository.create(voto_create)

        # Buscar
        resultado = voto_repository.get_by_id(2)

        assert resultado is not None
        assert resultado.id == 2
        assert resultado.votacao_id == 456
        assert resultado.voto == "NAO"

    def test_get_by_id_returns_none_for_nonexistent(self, voto_repository):
        """Test: get_by_id() retorna None para id inexistente."""
        resultado = voto_repository.get_by_id(99999)
        assert resultado is None

    def test_get_by_votacao_returns_votos(self, voto_repository):
        """Test: get_by_votacao() retorna votos de uma votação."""
        # Criar votos para diferentes votações
        votos = [
            VotoCreate(id=100, votacao_id=111, deputado_id=1, voto="SIM"),
            VotoCreate(id=101, votacao_id=111, deputado_id=2, voto="NAO"),
            VotoCreate(id=102, votacao_id=222, deputado_id=3, voto="ABSTENCAO"),
        ]
        for v in votos:
            voto_repository.create(v)

        # Buscar votos de votação 111
        votos_111 = voto_repository.get_by_votacao(111)

        assert len(votos_111) == 2
        assert all(v.votacao_id == 111 for v in votos_111)

    def test_get_by_deputado_returns_votos(self, voto_repository):
        """Test: get_by_deputado() retorna votos de um deputado."""
        # Criar votos de diferentes deputados
        votos = [
            VotoCreate(id=200, votacao_id=1, deputado_id=555, voto="SIM"),
            VotoCreate(id=201, votacao_id=2, deputado_id=555, voto="NAO"),
            VotoCreate(id=202, votacao_id=3, deputado_id=666, voto="ABSTENCAO"),
        ]
        for v in votos:
            voto_repository.create(v)

        # Buscar votos de deputado 555
        votos_555 = voto_repository.get_by_deputado(555)

        assert len(votos_555) == 2
        assert all(v.deputado_id == 555 for v in votos_555)

    def test_get_all_returns_all_votos(self, voto_repository):
        """Test: get_all() retorna todos os votos."""
        votos = [
            VotoCreate(id=300, votacao_id=1, deputado_id=1, voto="SIM"),
            VotoCreate(id=301, votacao_id=2, deputado_id=2, voto="NAO"),
        ]
        for v in votos:
            voto_repository.create(v)

        # Buscar todos
        todos = voto_repository.get_all()

        assert len(todos) == 2
        assert all(isinstance(v, Voto) for v in todos)

    def test_bulk_insert_inserts_multiple(self, voto_repository):
        """Test: bulk_insert() insere múltiplos votos."""
        votos = [
            VotoCreate(id=400, votacao_id=1, deputado_id=1, voto="SIM"),
            VotoCreate(id=401, votacao_id=1, deputado_id=2, voto="NAO"),
            VotoCreate(id=402, votacao_id=1, deputado_id=3, voto="ABSTENCAO"),
        ]

        count = voto_repository.bulk_insert(votos)

        assert count == 3

        # Verificar que foram inseridos
        todos = voto_repository.get_all()
        assert len(todos) == 3

    def test_delete_by_id_removes_voto(self, voto_repository):
        """Test: delete_by_id() remove voto."""
        # Criar voto
        voto_create = VotoCreate(
            id=500,
            votacao_id=1,
            deputado_id=1,
            voto="SIM",
        )
        voto_repository.create(voto_create)

        # Deletar
        deleted = voto_repository.delete_by_id(500)

        assert deleted is True

        # Verificar que foi deletado
        resultado = voto_repository.get_by_id(500)
        assert resultado is None

    def test_delete_by_id_returns_false_for_nonexistent(self, voto_repository):
        """Test: delete_by_id() retorna False para id inexistente."""
        deleted = voto_repository.delete_by_id(99999)
        assert deleted is False
