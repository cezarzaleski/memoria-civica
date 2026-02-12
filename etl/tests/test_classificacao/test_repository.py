"""Testes para Repositories do domínio de Classificação Cívica.

Validam operações de query, seed, bulk_upsert e delete_by_origem.
Testes de query usam inserção direta via ORM (SQLite-compatível).
Testes de bulk_upsert e seed requerem PostgreSQL (INSERT...ON CONFLICT).
"""

import pytest

from src.classificacao.models import CategoriaCivica, ProposicaoCategoria
from src.classificacao.repository import CATEGORIAS_SEED


class TestCategoriaCivicaRepository:
    """Testes para CategoriaCivicaRepository."""

    def test_get_all_returns_empty_initially(self, categoria_civica_repository):
        """Test: get_all() retorna lista vazia quando sem dados."""
        resultado = categoria_civica_repository.get_all()
        assert resultado == []

    def test_get_all_returns_all_categorias(self, categoria_civica_repository, db_session):
        """Test: get_all() retorna todas as categorias inseridas."""
        categorias = [
            CategoriaCivica(codigo="CAT_A", nome="Categoria A"),
            CategoriaCivica(codigo="CAT_B", nome="Categoria B"),
        ]
        db_session.add_all(categorias)
        db_session.commit()

        resultado = categoria_civica_repository.get_all()

        assert len(resultado) == 2
        assert all(isinstance(c, CategoriaCivica) for c in resultado)

    def test_get_by_codigo_returns_existing(self, categoria_civica_repository, db_session):
        """Test: get_by_codigo() retorna categoria existente."""
        cat = CategoriaCivica(codigo="GASTOS_PUBLICOS", nome="Gastos Públicos", icone="💰")
        db_session.add(cat)
        db_session.commit()

        resultado = categoria_civica_repository.get_by_codigo("GASTOS_PUBLICOS")

        assert resultado is not None
        assert resultado.codigo == "GASTOS_PUBLICOS"
        assert resultado.nome == "Gastos Públicos"
        assert resultado.icone == "💰"

    def test_get_by_codigo_returns_none_for_nonexistent(self, categoria_civica_repository):
        """Test: get_by_codigo() retorna None para código inexistente."""
        resultado = categoria_civica_repository.get_by_codigo("INEXISTENTE")
        assert resultado is None

    @pytest.mark.integration
    def test_seed_inserts_all_categories(self, categoria_civica_repository, db_session):
        """Test: seed() insere todas as 9 categorias cívicas (requer PostgreSQL)."""
        if "sqlite" in str(db_session.bind.url):
            pytest.skip("INSERT...ON CONFLICT requer PostgreSQL")

        count = categoria_civica_repository.seed()

        assert count == len(CATEGORIAS_SEED)
        todas = categoria_civica_repository.get_all()
        assert len(todas) == len(CATEGORIAS_SEED)

    @pytest.mark.integration
    def test_seed_is_idempotent(self, categoria_civica_repository, db_session):
        """Test: seed() é idempotente — re-execução não duplica (requer PostgreSQL)."""
        if "sqlite" in str(db_session.bind.url):
            pytest.skip("INSERT...ON CONFLICT requer PostgreSQL")

        categoria_civica_repository.seed()
        count2 = categoria_civica_repository.seed()

        assert count2 == 0
        todas = categoria_civica_repository.get_all()
        assert len(todas) == len(CATEGORIAS_SEED)

    def test_categorias_seed_data_is_complete(self):
        """Test: CATEGORIAS_SEED contém exatamente 9 categorias com dados obrigatórios."""
        assert len(CATEGORIAS_SEED) == 9
        for cat in CATEGORIAS_SEED:
            assert "codigo" in cat
            assert "nome" in cat
            assert len(cat["codigo"]) > 0
            assert len(cat["nome"]) > 0


class TestProposicaoCategoriaRepository:
    """Testes para ProposicaoCategoriaRepository.

    Testes de query usam inserção direta via ORM (SQLite-compatível).
    Testes de bulk_upsert requerem PostgreSQL (INSERT...ON CONFLICT).
    """

    def test_get_by_proposicao_returns_categorias(self, proposicao_categoria_repository, db_session):
        """Test: get_by_proposicao() retorna categorias de uma proposição."""
        pcs = [
            ProposicaoCategoria(proposicao_id=100, categoria_id=1, origem="regra", confianca=1.0),
            ProposicaoCategoria(proposicao_id=100, categoria_id=2, origem="regra", confianca=1.0),
            ProposicaoCategoria(proposicao_id=200, categoria_id=1, origem="regra", confianca=1.0),
        ]
        db_session.add_all(pcs)
        db_session.commit()

        resultado = proposicao_categoria_repository.get_by_proposicao(100)

        assert len(resultado) == 2
        assert all(pc.proposicao_id == 100 for pc in resultado)

    def test_get_by_proposicao_returns_empty_for_nonexistent(self, proposicao_categoria_repository):
        """Test: get_by_proposicao() retorna lista vazia para proposição inexistente."""
        resultado = proposicao_categoria_repository.get_by_proposicao(99999)
        assert resultado == []

    def test_get_by_categoria_returns_proposicoes(self, proposicao_categoria_repository, db_session):
        """Test: get_by_categoria() retorna proposições de uma categoria."""
        pcs = [
            ProposicaoCategoria(proposicao_id=100, categoria_id=5, origem="regra", confianca=1.0),
            ProposicaoCategoria(proposicao_id=200, categoria_id=5, origem="regra", confianca=1.0),
            ProposicaoCategoria(proposicao_id=300, categoria_id=6, origem="regra", confianca=1.0),
        ]
        db_session.add_all(pcs)
        db_session.commit()

        resultado = proposicao_categoria_repository.get_by_categoria(5)

        assert len(resultado) == 2
        assert all(pc.categoria_id == 5 for pc in resultado)

    def test_get_by_categoria_returns_empty_for_nonexistent(self, proposicao_categoria_repository):
        """Test: get_by_categoria() retorna lista vazia para categoria inexistente."""
        resultado = proposicao_categoria_repository.get_by_categoria(99999)
        assert resultado == []

    def test_delete_by_origem_removes_matching(self, proposicao_categoria_repository, db_session):
        """Test: delete_by_origem() remove apenas classificações da origem especificada."""
        pcs = [
            ProposicaoCategoria(proposicao_id=100, categoria_id=1, origem="regra", confianca=1.0),
            ProposicaoCategoria(proposicao_id=100, categoria_id=2, origem="regra", confianca=1.0),
            ProposicaoCategoria(proposicao_id=100, categoria_id=3, origem="llm", confianca=0.85),
        ]
        db_session.add_all(pcs)
        db_session.commit()

        deleted = proposicao_categoria_repository.delete_by_origem("regra")

        assert deleted == 2

        # Verificar que classificações "llm" foram preservadas
        restantes = proposicao_categoria_repository.get_by_proposicao(100)
        assert len(restantes) == 1
        assert restantes[0].origem == "llm"
        assert restantes[0].confianca == 0.85

    def test_delete_by_origem_returns_zero_when_none_found(self, proposicao_categoria_repository):
        """Test: delete_by_origem() retorna 0 quando nenhum registro encontrado."""
        deleted = proposicao_categoria_repository.delete_by_origem("inexistente")
        assert deleted == 0

    def test_delete_by_origem_preserves_other_origins(self, proposicao_categoria_repository, db_session):
        """Test: delete_by_origem('regra') preserva classificações 'llm'."""
        pcs = [
            ProposicaoCategoria(proposicao_id=100, categoria_id=1, origem="llm", confianca=0.9),
            ProposicaoCategoria(proposicao_id=200, categoria_id=2, origem="llm", confianca=0.8),
        ]
        db_session.add_all(pcs)
        db_session.commit()

        deleted = proposicao_categoria_repository.delete_by_origem("regra")

        assert deleted == 0
        all_records = proposicao_categoria_repository.get_by_proposicao(100)
        assert len(all_records) == 1

    def test_bulk_upsert_returns_zero_for_empty_list(self, proposicao_categoria_repository):
        """Test: bulk_upsert() retorna 0 para lista vazia."""
        count = proposicao_categoria_repository.bulk_upsert([])
        assert count == 0

    @pytest.mark.integration
    def test_bulk_upsert_inserts_records(self, proposicao_categoria_repository, db_session):
        """Test: bulk_upsert() insere registros (requer PostgreSQL)."""
        if "sqlite" in str(db_session.bind.url):
            pytest.skip("INSERT...ON CONFLICT requer PostgreSQL")

        from src.classificacao.schemas import ProposicaoCategoriaCreate

        records = [
            ProposicaoCategoriaCreate(proposicao_id=1, categoria_id=1, origem="regra", confianca=1.0),
            ProposicaoCategoriaCreate(proposicao_id=1, categoria_id=2, origem="regra", confianca=1.0),
        ]
        count = proposicao_categoria_repository.bulk_upsert(records)

        assert count == 2
        resultado = proposicao_categoria_repository.get_by_proposicao(1)
        assert len(resultado) == 2

    @pytest.mark.integration
    def test_bulk_upsert_idempotent(self, proposicao_categoria_repository, db_session):
        """Test: bulk_upsert() é idempotente — re-execução atualiza sem duplicar (requer PostgreSQL)."""
        if "sqlite" in str(db_session.bind.url):
            pytest.skip("INSERT...ON CONFLICT requer PostgreSQL")

        from src.classificacao.schemas import ProposicaoCategoriaCreate

        records = [
            ProposicaoCategoriaCreate(proposicao_id=1, categoria_id=1, origem="regra", confianca=1.0),
        ]

        proposicao_categoria_repository.bulk_upsert(records)
        proposicao_categoria_repository.bulk_upsert(records)

        resultado = proposicao_categoria_repository.get_by_proposicao(1)
        assert len(resultado) == 1
