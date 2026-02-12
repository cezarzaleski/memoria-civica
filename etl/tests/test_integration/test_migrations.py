"""Testes para migrations Alembic 005-008.

Validam o encadeamento de revisões, a estrutura dos scripts de migração,
e que upgrade/downgrade estão corretamente definidos.
"""

import importlib
from pathlib import Path

import pytest

# Caminhos para os scripts de migração
MIGRATIONS_DIR = Path(__file__).parent.parent.parent / "alembic" / "versions"


class TestMigrationChain:
    """Testes para o encadeamento correto das migrations."""

    def _load_migration(self, filename: str):
        """Helper para carregar um módulo de migração."""
        filepath = MIGRATIONS_DIR / filename
        spec = importlib.util.spec_from_file_location(filename.replace(".py", ""), filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_migration_005_chains_from_004(self):
        """Test: Migration 005 tem down_revision='004'."""
        mod = self._load_migration("005_alter_votacoes_add_columns.py")
        assert mod.revision == "005"
        assert mod.down_revision == "004"

    def test_migration_006_chains_from_005(self):
        """Test: Migration 006 tem down_revision='005'."""
        mod = self._load_migration("006_add_votacoes_proposicoes_table.py")
        assert mod.revision == "006"
        assert mod.down_revision == "005"

    def test_migration_007_chains_from_006(self):
        """Test: Migration 007 tem down_revision='006'."""
        mod = self._load_migration("007_add_categorias_civicas_table.py")
        assert mod.revision == "007"
        assert mod.down_revision == "006"

    def test_migration_008_chains_from_007(self):
        """Test: Migration 008 tem down_revision='007'."""
        mod = self._load_migration("008_add_orientacoes_proposicoes_categorias.py")
        assert mod.revision == "008"
        assert mod.down_revision == "007"

    def test_full_chain_004_to_008(self):
        """Test: Cadeia completa 004 → 005 → 006 → 007 → 008 está correta."""
        expected_chain = [
            ("005", "004"),
            ("006", "005"),
            ("007", "006"),
            ("008", "007"),
        ]

        files = [
            "005_alter_votacoes_add_columns.py",
            "006_add_votacoes_proposicoes_table.py",
            "007_add_categorias_civicas_table.py",
            "008_add_orientacoes_proposicoes_categorias.py",
        ]

        for filename, (expected_rev, expected_down) in zip(files, expected_chain, strict=True):
            mod = self._load_migration(filename)
            assert mod.revision == expected_rev, f"{filename}: revision expected {expected_rev}, got {mod.revision}"
            assert (
                mod.down_revision == expected_down
            ), f"{filename}: down_revision expected {expected_down}, got {mod.down_revision}"


class TestMigrationStructure:
    """Testes para validar que as migrations têm upgrade e downgrade."""

    def _load_migration(self, filename: str):
        """Helper para carregar um módulo de migração."""
        filepath = MIGRATIONS_DIR / filename
        spec = importlib.util.spec_from_file_location(filename.replace(".py", ""), filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    @pytest.mark.parametrize(
        "filename",
        [
            "005_alter_votacoes_add_columns.py",
            "006_add_votacoes_proposicoes_table.py",
            "007_add_categorias_civicas_table.py",
            "008_add_orientacoes_proposicoes_categorias.py",
        ],
    )
    def test_migration_has_upgrade_function(self, filename):
        """Test: Migration tem função upgrade()."""
        mod = self._load_migration(filename)
        assert hasattr(mod, "upgrade")
        assert callable(mod.upgrade)

    @pytest.mark.parametrize(
        "filename",
        [
            "005_alter_votacoes_add_columns.py",
            "006_add_votacoes_proposicoes_table.py",
            "007_add_categorias_civicas_table.py",
            "008_add_orientacoes_proposicoes_categorias.py",
        ],
    )
    def test_migration_has_downgrade_function(self, filename):
        """Test: Migration tem função downgrade()."""
        mod = self._load_migration(filename)
        assert hasattr(mod, "downgrade")
        assert callable(mod.downgrade)


class TestMigration007SeedData:
    """Testes para validar os dados seed da migration 007."""

    def _load_migration(self, filename: str):
        """Helper para carregar um módulo de migração."""
        filepath = MIGRATIONS_DIR / filename
        spec = importlib.util.spec_from_file_location(filename.replace(".py", ""), filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_migration_007_has_9_categories(self):
        """Test: Migration 007 define exatamente 9 categorias para seed."""
        mod = self._load_migration("007_add_categorias_civicas_table.py")
        assert hasattr(mod, "CATEGORIAS_SEED")
        assert len(mod.CATEGORIAS_SEED) == 9

    def test_migration_007_seed_has_required_fields(self):
        """Test: Cada categoria seed tem codigo, nome, descricao e icone."""
        mod = self._load_migration("007_add_categorias_civicas_table.py")
        required_fields = {"codigo", "nome", "descricao", "icone"}

        for cat in mod.CATEGORIAS_SEED:
            assert required_fields.issubset(cat.keys()), f"Categoria {cat.get('codigo')} faltando campos"

    def test_migration_007_seed_codigos_are_unique(self):
        """Test: Códigos das categorias são únicos."""
        mod = self._load_migration("007_add_categorias_civicas_table.py")
        codigos = [cat["codigo"] for cat in mod.CATEGORIAS_SEED]
        assert len(codigos) == len(set(codigos)), "Códigos duplicados encontrados"

    def test_migration_007_expected_categories(self):
        """Test: Migration 007 contém as 9 categorias esperadas."""
        mod = self._load_migration("007_add_categorias_civicas_table.py")
        expected_codigos = {
            "GASTOS_PUBLICOS",
            "TRIBUTACAO_AUMENTO",
            "TRIBUTACAO_ISENCAO",
            "BENEFICIOS_CATEGORIAS",
            "DIREITOS_SOCIAIS",
            "SEGURANCA_JUSTICA",
            "MEIO_AMBIENTE",
            "REGULACAO_ECONOMICA",
            "POLITICA_INSTITUCIONAL",
        }
        actual_codigos = {cat["codigo"] for cat in mod.CATEGORIAS_SEED}
        assert actual_codigos == expected_codigos


class TestMigrationSchemaApply:
    """Testes para validar que as migrations criam as tabelas corretamente via SQLAlchemy."""

    def test_all_tables_created_via_metadata(self, db_session):
        """Test: Todas as tabelas novas são criadas via Base.metadata.create_all()."""
        # Importar todos os models para garantir que estão registrados em Base.metadata
        from src.classificacao.models import CategoriaCivica, ProposicaoCategoria
        from src.votacoes.models import Orientacao, VotacaoProposicao

        # db_session já foi criada com Base.metadata.create_all() pelo conftest
        # Verificar que as tabelas existem fazendo queries simples
        result_vp = db_session.query(VotacaoProposicao).all()
        assert result_vp == []  # Tabela existe, vazia

        result_o = db_session.query(Orientacao).all()
        assert result_o == []

        result_cc = db_session.query(CategoriaCivica).all()
        assert result_cc == []

        result_pc = db_session.query(ProposicaoCategoria).all()
        assert result_pc == []
