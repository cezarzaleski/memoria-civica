"""Testes para models SQLAlchemy do domínio de Votações.

Validam a criação de Votacao (com novos campos), VotacaoProposicao e Orientacao,
constraints de unicidade e relacionamentos.
"""

from datetime import datetime

import pytest
from sqlalchemy.exc import IntegrityError

from src.proposicoes.models import Proposicao
from src.votacoes.models import Orientacao, Votacao, VotacaoProposicao


class TestVotacaoModel:
    """Testes para o model Votacao atualizado."""

    def _create_proposicao(self, db_session, prop_id=1):
        """Helper para criar uma proposição de teste."""
        prop = Proposicao(id=prop_id, tipo="PL", numero=100, ano=2024, ementa="Ementa teste")
        db_session.add(prop)
        db_session.commit()
        return prop

    def test_create_votacao_without_proposicao_id(self, db_session):
        """Test: Votacao pode ser criada sem proposicao_id (nullable)."""
        votacao = Votacao(
            id=1,
            proposicao_id=None,
            data_hora=datetime(2024, 1, 15, 14, 30, 0),
            resultado="APROVADO",
        )
        db_session.add(votacao)
        db_session.commit()

        assert votacao.id == 1
        assert votacao.proposicao_id is None

    def test_create_votacao_with_proposicao_id(self, db_session):
        """Test: Votacao pode ser criada com proposicao_id."""
        prop = self._create_proposicao(db_session)
        votacao = Votacao(
            id=1,
            proposicao_id=prop.id,
            data_hora=datetime(2024, 1, 15, 14, 30, 0),
            resultado="APROVADO",
        )
        db_session.add(votacao)
        db_session.commit()

        assert votacao.proposicao_id == prop.id

    def test_new_fields_accept_values(self, db_session):
        """Test: Votacao novos campos aceitam valores corretamente."""
        votacao = Votacao(
            id=1,
            data_hora=datetime(2024, 1, 15, 14, 30, 0),
            resultado="APROVADO",
            eh_nominal=True,
            votos_sim=250,
            votos_nao=150,
            votos_outros=10,
            descricao="Votação do PL 1234/2024",
            sigla_orgao="PLEN",
        )
        db_session.add(votacao)
        db_session.commit()

        assert votacao.eh_nominal is True
        assert votacao.votos_sim == 250
        assert votacao.votos_nao == 150
        assert votacao.votos_outros == 10
        assert votacao.descricao == "Votação do PL 1234/2024"
        assert votacao.sigla_orgao == "PLEN"

    def test_new_fields_defaults(self, db_session):
        """Test: Votacao novos campos têm defaults corretos."""
        votacao = Votacao(
            id=1,
            data_hora=datetime(2024, 1, 15, 14, 30, 0),
            resultado="APROVADO",
        )
        db_session.add(votacao)
        db_session.commit()

        db_session.refresh(votacao)
        assert votacao.eh_nominal is False
        assert votacao.votos_sim == 0
        assert votacao.votos_nao == 0
        assert votacao.votos_outros == 0
        assert votacao.descricao is None
        assert votacao.sigla_orgao is None


class TestVotacaoProposicaoModel:
    """Testes para o model VotacaoProposicao."""

    def _create_proposicao(self, db_session, prop_id=1):
        """Helper para criar uma proposição de teste."""
        prop = Proposicao(id=prop_id, tipo="PL", numero=100, ano=2024, ementa="Ementa teste")
        db_session.add(prop)
        db_session.commit()
        return prop

    def _create_votacao(self, db_session, votacao_id=1):
        """Helper para criar uma votação de teste."""
        votacao = Votacao(
            id=votacao_id,
            data_hora=datetime(2024, 1, 15, 14, 30, 0),
            resultado="APROVADO",
        )
        db_session.add(votacao)
        db_session.commit()
        return votacao

    def test_create_votacao_proposicao(self, db_session):
        """Test: VotacaoProposicao pode ser criada com todos os campos."""
        votacao = self._create_votacao(db_session)
        prop = self._create_proposicao(db_session)

        vp = VotacaoProposicao(
            votacao_id=votacao.id,
            votacao_id_original="2367548-7",
            proposicao_id=prop.id,
            titulo="PL 10106/2018",
            ementa="Ementa da proposição",
            sigla_tipo="PL",
            numero=10106,
            ano=2018,
            eh_principal=True,
        )
        db_session.add(vp)
        db_session.commit()

        assert vp.id is not None
        assert vp.votacao_id == votacao.id
        assert vp.votacao_id_original == "2367548-7"
        assert vp.proposicao_id == prop.id
        assert vp.titulo == "PL 10106/2018"
        assert vp.eh_principal is True

    def test_unique_constraint_votacao_proposicao(self, db_session):
        """Test: VotacaoProposicao rejeita duplicata em (votacao_id, proposicao_id)."""
        votacao = self._create_votacao(db_session)
        prop = self._create_proposicao(db_session)

        vp1 = VotacaoProposicao(votacao_id=votacao.id, proposicao_id=prop.id)
        db_session.add(vp1)
        db_session.commit()

        vp2 = VotacaoProposicao(votacao_id=votacao.id, proposicao_id=prop.id)
        db_session.add(vp2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_relationship_to_votacao(self, db_session):
        """Test: VotacaoProposicao tem relacionamento correto com Votacao."""
        votacao = self._create_votacao(db_session)
        prop = self._create_proposicao(db_session)

        vp = VotacaoProposicao(votacao_id=votacao.id, proposicao_id=prop.id)
        db_session.add(vp)
        db_session.commit()

        assert vp.votacao.id == votacao.id

    def test_relationship_to_proposicao(self, db_session):
        """Test: VotacaoProposicao tem relacionamento correto com Proposicao."""
        votacao = self._create_votacao(db_session)
        prop = self._create_proposicao(db_session)

        vp = VotacaoProposicao(votacao_id=votacao.id, proposicao_id=prop.id)
        db_session.add(vp)
        db_session.commit()

        assert vp.proposicao.id == prop.id

    def test_eh_principal_defaults_false(self, db_session):
        """Test: VotacaoProposicao.eh_principal default é False."""
        votacao = self._create_votacao(db_session)
        prop = self._create_proposicao(db_session)

        vp = VotacaoProposicao(votacao_id=votacao.id, proposicao_id=prop.id)
        db_session.add(vp)
        db_session.commit()

        db_session.refresh(vp)
        assert vp.eh_principal is False

    def test_fk_votacao_has_cascade_delete(self):
        """Test: VotacaoProposicao FK votacao_id tem ondelete CASCADE definido."""
        fk = next(fk for fk in VotacaoProposicao.__table__.c.votacao_id.foreign_keys)
        assert fk.ondelete == "CASCADE"

    def test_fk_proposicao_has_cascade_delete(self):
        """Test: VotacaoProposicao FK proposicao_id tem ondelete CASCADE definido."""
        fk = next(fk for fk in VotacaoProposicao.__table__.c.proposicao_id.foreign_keys)
        assert fk.ondelete == "CASCADE"


class TestOrientacaoModel:
    """Testes para o model Orientacao."""

    def _create_votacao(self, db_session, votacao_id=1):
        """Helper para criar uma votação de teste."""
        votacao = Votacao(
            id=votacao_id,
            data_hora=datetime(2024, 1, 15, 14, 30, 0),
            resultado="APROVADO",
        )
        db_session.add(votacao)
        db_session.commit()
        return votacao

    def test_create_orientacao(self, db_session):
        """Test: Orientacao pode ser criada com campos obrigatórios."""
        votacao = self._create_votacao(db_session)

        orientacao = Orientacao(
            votacao_id=votacao.id,
            votacao_id_original="2367548-7",
            sigla_bancada="PT",
            orientacao="Sim",
        )
        db_session.add(orientacao)
        db_session.commit()

        assert orientacao.id is not None
        assert orientacao.votacao_id == votacao.id
        assert orientacao.votacao_id_original == "2367548-7"
        assert orientacao.sigla_bancada == "PT"
        assert orientacao.orientacao == "Sim"

    def test_unique_constraint_votacao_bancada(self, db_session):
        """Test: Orientacao rejeita duplicata em (votacao_id, sigla_bancada)."""
        votacao = self._create_votacao(db_session)

        o1 = Orientacao(votacao_id=votacao.id, sigla_bancada="PT", orientacao="Sim")
        db_session.add(o1)
        db_session.commit()

        o2 = Orientacao(votacao_id=votacao.id, sigla_bancada="PT", orientacao="Não")
        db_session.add(o2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_different_bancada_allowed(self, db_session):
        """Test: Orientacao permite mesma votação com bancadas diferentes."""
        votacao = self._create_votacao(db_session)

        o1 = Orientacao(votacao_id=votacao.id, sigla_bancada="PT", orientacao="Sim")
        o2 = Orientacao(votacao_id=votacao.id, sigla_bancada="PL", orientacao="Não")
        db_session.add_all([o1, o2])
        db_session.commit()

        assert o1.id is not None
        assert o2.id is not None

    def test_relationship_to_votacao(self, db_session):
        """Test: Orientacao tem relacionamento correto com Votacao."""
        votacao = self._create_votacao(db_session)

        orientacao = Orientacao(
            votacao_id=votacao.id,
            sigla_bancada="PT",
            orientacao="Sim",
        )
        db_session.add(orientacao)
        db_session.commit()

        assert orientacao.votacao.id == votacao.id

    def test_fk_votacao_has_cascade_delete(self):
        """Test: Orientacao FK votacao_id tem ondelete CASCADE definido."""
        fk = next(fk for fk in Orientacao.__table__.c.votacao_id.foreign_keys)
        assert fk.ondelete == "CASCADE"
