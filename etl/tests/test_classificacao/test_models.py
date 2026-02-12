"""Testes para models SQLAlchemy do domínio de Classificação Cívica.

Validam a criação de CategoriaCivica e ProposicaoCategoria,
constraints de unicidade e relacionamentos.
"""

import pytest
from sqlalchemy.exc import IntegrityError

from src.classificacao.models import CategoriaCivica, ProposicaoCategoria
from src.proposicoes.models import Proposicao


class TestCategoriaCivica:
    """Testes para o model CategoriaCivica."""

    def test_create_categoria_civica(self, db_session):
        """Test: CategoriaCivica pode ser criada com campos obrigatórios."""
        categoria = CategoriaCivica(
            codigo="GASTOS_PUBLICOS",
            nome="Gastos Públicos",
            descricao="Proposições sobre gastos públicos",
            icone="💰",
        )
        db_session.add(categoria)
        db_session.commit()

        assert categoria.id is not None
        assert categoria.codigo == "GASTOS_PUBLICOS"
        assert categoria.nome == "Gastos Públicos"
        assert categoria.descricao == "Proposições sobre gastos públicos"
        assert categoria.icone == "💰"

    def test_create_categoria_without_optional_fields(self, db_session):
        """Test: CategoriaCivica pode ser criada sem campos opcionais."""
        categoria = CategoriaCivica(
            codigo="TEST_CODE",
            nome="Test Name",
        )
        db_session.add(categoria)
        db_session.commit()

        assert categoria.id is not None
        assert categoria.descricao is None
        assert categoria.icone is None

    def test_unique_constraint_on_codigo(self, db_session):
        """Test: CategoriaCivica rejeita duplicata no campo codigo."""
        cat1 = CategoriaCivica(codigo="GASTOS_PUBLICOS", nome="Gastos Públicos")
        db_session.add(cat1)
        db_session.commit()

        cat2 = CategoriaCivica(codigo="GASTOS_PUBLICOS", nome="Outro Nome")
        db_session.add(cat2)
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestProposicaoCategoria:
    """Testes para o model ProposicaoCategoria."""

    def _create_proposicao(self, db_session, prop_id=1):
        """Helper para criar uma proposição de teste."""
        prop = Proposicao(id=prop_id, tipo="PL", numero=100, ano=2024, ementa="Ementa teste")
        db_session.add(prop)
        db_session.commit()
        return prop

    def _create_categoria(self, db_session, codigo="GASTOS_PUBLICOS"):
        """Helper para criar uma categoria de teste."""
        cat = CategoriaCivica(codigo=codigo, nome="Gastos Públicos")
        db_session.add(cat)
        db_session.commit()
        return cat

    def test_create_proposicao_categoria(self, db_session):
        """Test: ProposicaoCategoria pode ser criada com campos obrigatórios."""
        prop = self._create_proposicao(db_session)
        cat = self._create_categoria(db_session)

        pc = ProposicaoCategoria(
            proposicao_id=prop.id,
            categoria_id=cat.id,
            origem="regra",
            confianca=1.0,
        )
        db_session.add(pc)
        db_session.commit()

        assert pc.id is not None
        assert pc.proposicao_id == prop.id
        assert pc.categoria_id == cat.id
        assert pc.origem == "regra"
        assert pc.confianca == 1.0

    def test_unique_constraint_proposicao_categoria_origem(self, db_session):
        """Test: ProposicaoCategoria rejeita duplicata em (proposicao_id, categoria_id, origem)."""
        prop = self._create_proposicao(db_session)
        cat = self._create_categoria(db_session)

        pc1 = ProposicaoCategoria(
            proposicao_id=prop.id,
            categoria_id=cat.id,
            origem="regra",
            confianca=1.0,
        )
        db_session.add(pc1)
        db_session.commit()

        pc2 = ProposicaoCategoria(
            proposicao_id=prop.id,
            categoria_id=cat.id,
            origem="regra",
            confianca=0.8,
        )
        db_session.add(pc2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_different_origem_allowed(self, db_session):
        """Test: ProposicaoCategoria permite mesma proposicao+categoria com origens diferentes."""
        prop = self._create_proposicao(db_session)
        cat = self._create_categoria(db_session)

        pc1 = ProposicaoCategoria(
            proposicao_id=prop.id,
            categoria_id=cat.id,
            origem="regra",
            confianca=1.0,
        )
        pc2 = ProposicaoCategoria(
            proposicao_id=prop.id,
            categoria_id=cat.id,
            origem="llm",
            confianca=0.8,
        )
        db_session.add_all([pc1, pc2])
        db_session.commit()

        assert pc1.id is not None
        assert pc2.id is not None
        assert pc1.id != pc2.id

    def test_relationship_to_proposicao(self, db_session):
        """Test: ProposicaoCategoria tem relacionamento correto com Proposicao."""
        prop = self._create_proposicao(db_session)
        cat = self._create_categoria(db_session)

        pc = ProposicaoCategoria(
            proposicao_id=prop.id,
            categoria_id=cat.id,
            origem="regra",
        )
        db_session.add(pc)
        db_session.commit()

        assert pc.proposicao.id == prop.id

    def test_relationship_to_categoria(self, db_session):
        """Test: ProposicaoCategoria tem relacionamento correto com CategoriaCivica."""
        prop = self._create_proposicao(db_session)
        cat = self._create_categoria(db_session)

        pc = ProposicaoCategoria(
            proposicao_id=prop.id,
            categoria_id=cat.id,
            origem="regra",
        )
        db_session.add(pc)
        db_session.commit()

        assert pc.categoria.codigo == "GASTOS_PUBLICOS"

    def test_fk_proposicao_has_cascade_delete(self):
        """Test: ProposicaoCategoria FK proposicao_id tem ondelete CASCADE definido."""
        fk = next(fk for fk in ProposicaoCategoria.__table__.c.proposicao_id.foreign_keys)
        assert fk.ondelete == "CASCADE"

    def test_fk_categoria_has_cascade_delete(self):
        """Test: ProposicaoCategoria FK categoria_id tem ondelete CASCADE definido."""
        fk = next(fk for fk in ProposicaoCategoria.__table__.c.categoria_id.foreign_keys)
        assert fk.ondelete == "CASCADE"
