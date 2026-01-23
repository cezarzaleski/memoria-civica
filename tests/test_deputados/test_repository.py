"""Testes para Repository do domínio de Deputados.

Validam operações CRUD e bulk_upsert, incluindo idempotência.
"""


from src.deputados.models import Deputado
from src.deputados.schemas import DeputadoCreate


class TestDeputadoRepository:
    """Testes para DeputadoRepository."""

    def test_create_persists_deputado(self, deputado_repository, db_session):
        """Test: create() persiste deputado e retorna com id."""
        deputado_create = DeputadoCreate(
            id=100,
            nome="João Silva",
            partido="PT",
            uf="SP",
            foto_url="https://example.com/joao.jpg",
            email="joao@camara.leg.br",
        )

        resultado = deputado_repository.create(deputado_create)

        assert resultado.id == 100
        assert resultado.nome == "João Silva"
        assert resultado.partido == "PT"
        assert resultado.uf == "SP"
        assert resultado.foto_url == "https://example.com/joao.jpg"
        assert resultado.email == "joao@camara.leg.br"

        # Verificar que foi persistido no banco
        from_db = db_session.query(Deputado).filter(Deputado.id == 100).first()
        assert from_db is not None
        assert from_db.nome == "João Silva"

    def test_get_by_id_returns_existing(self, deputado_repository):
        """Test: get_by_id() retorna deputado existente."""
        # Criar primeiro
        deputado_create = DeputadoCreate(
            id=101,
            nome="Maria Santos",
            partido="PDT",
            uf="RJ",
        )
        deputado_repository.create(deputado_create)

        # Buscar
        resultado = deputado_repository.get_by_id(101)

        assert resultado is not None
        assert resultado.id == 101
        assert resultado.nome == "Maria Santos"
        assert resultado.partido == "PDT"
        assert resultado.uf == "RJ"

    def test_get_by_id_returns_none_for_nonexistent(self, deputado_repository):
        """Test: get_by_id() retorna None para id inexistente."""
        resultado = deputado_repository.get_by_id(99999)
        assert resultado is None

    def test_get_by_uf_returns_deputados_from_state(self, deputado_repository):
        """Test: get_by_uf() retorna deputados do estado."""
        # Criar alguns deputados
        deputados = [
            DeputadoCreate(id=201, nome="Carlos Oliveira", partido="PSDB", uf="SP"),
            DeputadoCreate(id=202, nome="Ana Costa", partido="PMDB", uf="SP"),
            DeputadoCreate(id=203, nome="Pedro Lima", partido="PP", uf="MG"),
        ]
        for d in deputados:
            deputado_repository.create(d)

        # Buscar por UF
        sp_deputados = deputado_repository.get_by_uf("SP")

        assert len(sp_deputados) == 2
        assert all(d.uf == "SP" for d in sp_deputados)

    def test_get_all_returns_all_deputados(self, deputado_repository):
        """Test: get_all() retorna todos os deputados."""
        # Criar alguns deputados
        deputados = [
            DeputadoCreate(id=301, nome="João", partido="PT", uf="SP"),
            DeputadoCreate(id=302, nome="Maria", partido="PDT", uf="RJ"),
            DeputadoCreate(id=303, nome="Carlos", partido="PSDB", uf="MG"),
        ]
        for d in deputados:
            deputado_repository.create(d)

        # Buscar todos
        todos = deputado_repository.get_all()

        assert len(todos) == 3
        assert all(isinstance(d, Deputado) for d in todos)

    def test_bulk_upsert_inserts_multiple(self, deputado_repository):
        """Test: bulk_upsert() insere múltiplos deputados."""
        deputados = [
            DeputadoCreate(id=401, nome="Abilio Brunini", partido="PSDB", uf="MT"),
            DeputadoCreate(id=402, nome="Acácio Favacho", partido="PDT", uf="AP"),
            DeputadoCreate(id=403, nome="Adail Filho", partido="PODEMOS", uf="AM"),
        ]

        count = deputado_repository.bulk_upsert(deputados)

        assert count == 3

        # Verificar que foram inseridos
        todos = deputado_repository.get_all()
        assert len(todos) == 3

    def test_bulk_upsert_idempotent(self, deputado_repository):
        """Test: bulk_upsert() não duplica em re-execução (idempotência)."""
        deputados = [
            DeputadoCreate(id=501, nome="Adilson Barroso", partido="PSDB", uf="MG"),
            DeputadoCreate(id=502, nome="Adolfo Viana", partido="PT", uf="BA"),
        ]

        # Primeira execução
        count1 = deputado_repository.bulk_upsert(deputados)
        assert count1 == 2

        # Segunda execução (deveria atualizar, não duplicar)
        count2 = deputado_repository.bulk_upsert(deputados)
        assert count2 == 2

        # Total deve ser 2, não 4
        todos = deputado_repository.get_all()
        assert len(todos) == 2

    def test_bulk_upsert_overwrites_existing(self, deputado_repository):
        """Test: bulk_upsert() sobrescreve deputados existentes."""
        # Inserir primeiro
        deputado1 = DeputadoCreate(id=601, nome="Nome Original", partido="PT", uf="SP")
        deputado_repository.create(deputado1)

        # Bulk upsert com mesmo ID mas dados diferentes
        deputado_atualizado = DeputadoCreate(
            id=601,
            nome="Nome Atualizado",
            partido="PSB",
            uf="RJ",
        )
        count = deputado_repository.bulk_upsert([deputado_atualizado])

        assert count == 1

        # Verificar que foi atualizado
        resultado = deputado_repository.get_by_id(601)
        assert resultado.nome == "Nome Atualizado"
        assert resultado.partido == "PSB"
        assert resultado.uf == "RJ"

    def test_bulk_upsert_empty_list(self, deputado_repository):
        """Test: bulk_upsert() com lista vazia retorna 0."""
        count = deputado_repository.bulk_upsert([])
        assert count == 0

    def test_delete_by_id_removes_deputado(self, deputado_repository):
        """Test: delete_by_id() remove deputado."""
        # Criar
        deputado = DeputadoCreate(id=701, nome="Adriana Ventura", partido="PSDB", uf="SP")
        deputado_repository.create(deputado)

        # Deletar
        deleted = deputado_repository.delete_by_id(701)
        assert deleted is True

        # Verificar que foi removido
        resultado = deputado_repository.get_by_id(701)
        assert resultado is None

    def test_delete_by_id_returns_false_for_nonexistent(self, deputado_repository):
        """Test: delete_by_id() retorna False para id inexistente."""
        deleted = deputado_repository.delete_by_id(88888)
        assert deleted is False
