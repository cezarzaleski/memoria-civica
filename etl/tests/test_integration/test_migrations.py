"""Testes para migrations Alembic 005-009.

Validam o encadeamento de revisões, a estrutura dos scripts de migração,
e que upgrade/downgrade estão corretamente definidos.
"""

import importlib
from pathlib import Path

import pytest
import sqlalchemy as sa

pytestmark = pytest.mark.integration

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

    def test_migration_009_chains_from_008(self):
        """Test: Migration 009 tem down_revision='008'."""
        mod = self._load_migration("009_add_gastos_table.py")
        assert mod.revision == "009"
        assert mod.down_revision == "008"

    def test_full_chain_004_to_009(self):
        """Test: Cadeia completa 004 → 005 → 006 → 007 → 008 → 009 está correta."""
        expected_chain = [
            ("005", "004"),
            ("006", "005"),
            ("007", "006"),
            ("008", "007"),
            ("009", "008"),
        ]

        files = [
            "005_alter_votacoes_add_columns.py",
            "006_add_votacoes_proposicoes_table.py",
            "007_add_categorias_civicas_table.py",
            "008_add_orientacoes_proposicoes_categorias.py",
            "009_add_gastos_table.py",
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
            "009_add_gastos_table.py",
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
            "009_add_gastos_table.py",
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
        from src.gastos.models import Gasto
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

        result_gastos = db_session.query(Gasto).all()
        assert result_gastos == []


class TestMigration009GastosContract:
    """Testes específicos da migration 009 da tabela gastos."""

    def _load_migration(self, filename: str):
        """Helper para carregar um módulo de migração."""
        filepath = MIGRATIONS_DIR / filename
        spec = importlib.util.spec_from_file_location(filename.replace(".py", ""), filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_migration_009_upgrade_creates_expected_table_and_indexes(self, monkeypatch):
        """Test: Upgrade da migration 009 cria tabela/constraints/índices esperados."""
        mod = self._load_migration("009_add_gastos_table.py")
        captured: dict[str, list | tuple | None] = {
            "table": None,
            "indexes": [],
        }

        def _fake_create_table(table_name, *args, **kwargs):
            captured["table"] = (table_name, args, kwargs)

        def _fake_create_index(index_name, table_name, columns, unique=False, **kwargs):
            captured["indexes"].append((index_name, table_name, columns, unique, kwargs))

        monkeypatch.setattr(mod.op, "create_table", _fake_create_table)
        monkeypatch.setattr(mod.op, "create_index", _fake_create_index)

        mod.upgrade()

        table_name, args, _kwargs = captured["table"]
        assert table_name == "gastos"

        columns = [arg for arg in args if isinstance(arg, sa.Column)]
        col_by_name = {col.name: col for col in columns}
        expected_columns = {
            "id",
            "deputado_id",
            "ano",
            "mes",
            "tipo_despesa",
            "tipo_documento",
            "data_documento",
            "numero_documento",
            "valor_documento",
            "valor_liquido",
            "valor_glosa",
            "nome_fornecedor",
            "cnpj_cpf_fornecedor",
            "url_documento",
            "cod_documento",
            "cod_lote",
            "parcela",
        }
        assert expected_columns.issubset(set(col_by_name))

        assert col_by_name["deputado_id"].nullable is True
        assert col_by_name["ano"].nullable is False
        assert col_by_name["mes"].nullable is False
        assert col_by_name["tipo_despesa"].nullable is False
        assert col_by_name["valor_documento"].nullable is False
        assert col_by_name["valor_liquido"].nullable is False
        assert col_by_name["valor_glosa"].nullable is False

        fk_constraints = [arg for arg in args if isinstance(arg, sa.ForeignKeyConstraint)]
        fk_deputado = next((fk for fk in fk_constraints if fk.column_keys == ["deputado_id"]), None)
        assert fk_deputado is not None
        assert fk_deputado.elements[0].target_fullname == "deputados.id"
        assert fk_deputado.ondelete == "SET NULL"

        unique_constraints = [arg for arg in args if isinstance(arg, sa.UniqueConstraint)]
        uq_gasto = next((uq for uq in unique_constraints if uq.name == "uq_gasto"), None)
        assert uq_gasto is not None
        uq_columns = list(uq_gasto.columns.keys()) or list(getattr(uq_gasto, "_pending_colargs", []))
        assert uq_columns == [
            "deputado_id",
            "ano",
            "mes",
            "tipo_despesa",
            "cnpj_cpf_fornecedor",
            "numero_documento",
        ]

        created_index_names = {index[0] for index in captured["indexes"]}
        expected_index_names = {
            "ux_gastos_dedup_normalized",
            "ix_gastos_deputado_id",
            "ix_gastos_ano_mes",
            "ix_gastos_tipo_despesa",
            "ix_gastos_fornecedor",
        }
        assert created_index_names == expected_index_names

        normalized_index = next(index for index in captured["indexes"] if index[0] == "ux_gastos_dedup_normalized")
        assert normalized_index[3] is True
        assert normalized_index[1] == "gastos"
        assert len(normalized_index[2]) == 6
        assert "coalesce(deputado_id, -1)" in str(normalized_index[2][0]).lower()
        assert "coalesce(cnpj_cpf_fornecedor, '')" in str(normalized_index[2][4]).lower()
        assert "coalesce(numero_documento, '')" in str(normalized_index[2][5]).lower()

    def test_migration_009_downgrade_removes_indexes_and_table(self, monkeypatch):
        """Test: Downgrade da migration 009 remove índices e tabela gastos."""
        mod = self._load_migration("009_add_gastos_table.py")
        dropped_indexes: list[tuple[str, str | None]] = []
        dropped_tables: list[str] = []

        def _fake_drop_index(index_name, table_name=None, **_kwargs):
            dropped_indexes.append((index_name, table_name))

        def _fake_drop_table(table_name):
            dropped_tables.append(table_name)

        monkeypatch.setattr(mod.op, "drop_index", _fake_drop_index)
        monkeypatch.setattr(mod.op, "drop_table", _fake_drop_table)

        mod.downgrade()

        assert dropped_tables == ["gastos"]
        assert dropped_indexes == [
            ("ix_gastos_fornecedor", "gastos"),
            ("ix_gastos_tipo_despesa", "gastos"),
            ("ix_gastos_ano_mes", "gastos"),
            ("ix_gastos_deputado_id", "gastos"),
            ("ux_gastos_dedup_normalized", "gastos"),
        ]
