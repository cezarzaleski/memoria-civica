"""Testes para o EnriquecimentoRepository.

Validam upsert idempotente, get_pendentes e get_by_proposicao
usando banco SQLite em memória via fixtures do conftest.
"""

import json

import pytest

from src.enriquecimento.models import EnriquecimentoLLM
from src.enriquecimento.repository import EnriquecimentoRepository
from src.proposicoes.models import Proposicao
from src.shared.llm_client import EnriquecimentoOutput


@pytest.fixture
def repository(db_session):
    """Retorna instância do EnriquecimentoRepository com sessão injetada."""
    return EnriquecimentoRepository(db_session)


@pytest.fixture
def sample_output():
    """Retorna um EnriquecimentoOutput de exemplo."""
    return EnriquecimentoOutput(
        headline="Projeto aumenta salário mínimo",
        resumo_simples="O projeto propõe aumentar o salário mínimo para R$ 2.000.",
        impacto_cidadao=["Aumento da renda para trabalhadores", "Impacto no custo de vida"],
        confianca=0.85,
    )


@pytest.fixture
def sample_proposicao(db_session):
    """Cria e retorna uma proposição de teste no banco."""
    proposicao = Proposicao(
        id=1,
        tipo="PL",
        numero=123,
        ano=2024,
        ementa="Altera a legislação do salário mínimo.",
    )
    db_session.add(proposicao)
    db_session.commit()
    return proposicao


@pytest.fixture
def multiple_proposicoes(db_session):
    """Cria múltiplas proposições de teste no banco."""
    proposicoes = [
        Proposicao(id=10, tipo="PL", numero=100, ano=2024, ementa="Ementa PL 100"),
        Proposicao(id=20, tipo="PEC", numero=200, ano=2024, ementa="Ementa PEC 200"),
        Proposicao(id=30, tipo="REQ", numero=300, ano=2024, ementa="Ementa REQ 300"),
    ]
    db_session.add_all(proposicoes)
    db_session.commit()
    return proposicoes


class TestUpsert:
    """Testes para o método upsert do EnriquecimentoRepository."""

    def test_upsert_inserts_new_record(self, db_session, repository, sample_output, sample_proposicao):
        """Test: upsert insere novo registro quando não existe."""
        result = repository.upsert(
            proposicao_id=sample_proposicao.id,
            resultado=sample_output,
            modelo="gpt-4o-mini",
            versao_prompt="v1.0",
            tokens_input=150,
            tokens_output=200,
        )

        assert result.proposicao_id == sample_proposicao.id
        assert result.modelo == "gpt-4o-mini"
        assert result.versao_prompt == "v1.0"
        assert result.headline == "Projeto aumenta salário mínimo"
        assert result.resumo_simples == "O projeto propõe aumentar o salário mínimo para R$ 2.000."
        assert json.loads(result.impacto_cidadao) == [
            "Aumento da renda para trabalhadores",
            "Impacto no custo de vida",
        ]
        assert result.confianca == 0.85
        assert result.necessita_revisao is False
        assert result.tokens_input == 150
        assert result.tokens_output == 200

    def test_upsert_updates_existing_record(self, db_session, repository, sample_output, sample_proposicao):
        """Test: upsert atualiza registro existente para mesma proposição e versão."""
        repository.upsert(
            proposicao_id=sample_proposicao.id,
            resultado=sample_output,
            modelo="gpt-4o-mini",
            versao_prompt="v1.0",
        )

        updated_output = EnriquecimentoOutput(
            headline="Headline atualizada",
            resumo_simples="Resumo atualizado",
            impacto_cidadao=["Novo impacto"],
            confianca=0.95,
        )

        result = repository.upsert(
            proposicao_id=sample_proposicao.id,
            resultado=updated_output,
            modelo="gpt-4o",
            versao_prompt="v1.0",
            tokens_input=300,
            tokens_output=400,
        )

        assert result.headline == "Headline atualizada"
        assert result.resumo_simples == "Resumo atualizado"
        assert result.modelo == "gpt-4o"
        assert result.confianca == 0.95
        assert result.tokens_input == 300
        assert result.tokens_output == 400

        count = db_session.query(EnriquecimentoLLM).filter_by(proposicao_id=sample_proposicao.id).count()
        assert count == 1

    def test_upsert_allows_different_versions(self, db_session, repository, sample_output, sample_proposicao):
        """Test: upsert permite múltiplas versões para a mesma proposição."""
        repository.upsert(
            proposicao_id=sample_proposicao.id,
            resultado=sample_output,
            modelo="gpt-4o-mini",
            versao_prompt="v1.0",
        )

        repository.upsert(
            proposicao_id=sample_proposicao.id,
            resultado=sample_output,
            modelo="gpt-4o-mini",
            versao_prompt="v2.0",
        )

        count = db_session.query(EnriquecimentoLLM).filter_by(proposicao_id=sample_proposicao.id).count()
        assert count == 2

    def test_upsert_sets_necessita_revisao_when_low_confidence(self, repository, sample_proposicao):
        """Test: upsert marca necessita_revisao=True quando confiança < threshold."""
        low_confidence_output = EnriquecimentoOutput(
            headline="Headline vaga",
            resumo_simples="Resumo incerto",
            impacto_cidadao=["Impacto não claro"],
            confianca=0.3,
        )

        result = repository.upsert(
            proposicao_id=sample_proposicao.id,
            resultado=low_confidence_output,
            modelo="gpt-4o-mini",
            versao_prompt="v1.0",
            confianca_threshold=0.5,
        )

        assert result.necessita_revisao is True

    def test_upsert_does_not_set_revisao_at_threshold(self, repository, sample_proposicao):
        """Test: upsert não marca necessita_revisao quando confiança == threshold."""
        threshold_output = EnriquecimentoOutput(
            headline="Headline",
            resumo_simples="Resumo",
            impacto_cidadao=["Impacto"],
            confianca=0.5,
        )

        result = repository.upsert(
            proposicao_id=sample_proposicao.id,
            resultado=threshold_output,
            modelo="gpt-4o-mini",
            versao_prompt="v1.0",
            confianca_threshold=0.5,
        )

        assert result.necessita_revisao is False

    def test_upsert_serializes_impacto_cidadao_as_json(self, repository, sample_output, sample_proposicao):
        """Test: upsert serializa impacto_cidadao como JSON string."""
        result = repository.upsert(
            proposicao_id=sample_proposicao.id,
            resultado=sample_output,
            modelo="gpt-4o-mini",
            versao_prompt="v1.0",
        )

        raw = result.impacto_cidadao
        assert isinstance(raw, str)
        parsed = json.loads(raw)
        assert isinstance(parsed, list)
        assert len(parsed) == 2

    def test_upsert_with_none_tokens(self, repository, sample_output, sample_proposicao):
        """Test: upsert aceita tokens_input e tokens_output como None."""
        result = repository.upsert(
            proposicao_id=sample_proposicao.id,
            resultado=sample_output,
            modelo="gpt-4o-mini",
            versao_prompt="v1.0",
        )

        assert result.tokens_input is None
        assert result.tokens_output is None


class TestGetPendentes:
    """Testes para o método get_pendentes do EnriquecimentoRepository."""

    def test_get_pendentes_returns_all_when_none_enriched(self, repository, multiple_proposicoes):
        """Test: get_pendentes retorna todas as proposições quando nenhuma foi enriquecida."""
        pendentes = repository.get_pendentes(versao_prompt="v1.0")

        assert len(pendentes) == 3
        ids = {p.id for p in pendentes}
        assert ids == {10, 20, 30}

    def test_get_pendentes_excludes_enriched(self, repository, multiple_proposicoes):
        """Test: get_pendentes exclui proposições já enriquecidas na versão."""
        output = EnriquecimentoOutput(
            headline="H",
            resumo_simples="R",
            impacto_cidadao=["I"],
            confianca=0.9,
        )
        repository.upsert(
            proposicao_id=10,
            resultado=output,
            modelo="gpt-4o-mini",
            versao_prompt="v1.0",
        )

        pendentes = repository.get_pendentes(versao_prompt="v1.0")

        assert len(pendentes) == 2
        ids = {p.id for p in pendentes}
        assert 10 not in ids
        assert ids == {20, 30}

    def test_get_pendentes_considers_version(self, repository, multiple_proposicoes):
        """Test: get_pendentes considera a versão do prompt corretamente."""
        output = EnriquecimentoOutput(
            headline="H",
            resumo_simples="R",
            impacto_cidadao=["I"],
            confianca=0.9,
        )
        repository.upsert(
            proposicao_id=10,
            resultado=output,
            modelo="gpt-4o-mini",
            versao_prompt="v1.0",
        )

        pendentes_v2 = repository.get_pendentes(versao_prompt="v2.0")
        assert len(pendentes_v2) == 3

    def test_get_pendentes_returns_empty_when_all_enriched(self, repository, multiple_proposicoes):
        """Test: get_pendentes retorna lista vazia quando todas foram enriquecidas."""
        output = EnriquecimentoOutput(
            headline="H",
            resumo_simples="R",
            impacto_cidadao=["I"],
            confianca=0.9,
        )
        for prop in multiple_proposicoes:
            repository.upsert(
                proposicao_id=prop.id,
                resultado=output,
                modelo="gpt-4o-mini",
                versao_prompt="v1.0",
            )

        pendentes = repository.get_pendentes(versao_prompt="v1.0")
        assert len(pendentes) == 0

    def test_get_pendentes_returns_empty_when_no_proposicoes(self, repository):
        """Test: get_pendentes retorna lista vazia quando não há proposições."""
        pendentes = repository.get_pendentes(versao_prompt="v1.0")
        assert len(pendentes) == 0


class TestGetByProposicao:
    """Testes para o método get_by_proposicao do EnriquecimentoRepository."""

    def test_get_by_proposicao_returns_none_when_not_found(self, repository):
        """Test: get_by_proposicao retorna None quando não existe enriquecimento."""
        result = repository.get_by_proposicao(proposicao_id=999)
        assert result is None

    def test_get_by_proposicao_returns_record(self, repository, sample_output, sample_proposicao):
        """Test: get_by_proposicao retorna o enriquecimento existente."""
        repository.upsert(
            proposicao_id=sample_proposicao.id,
            resultado=sample_output,
            modelo="gpt-4o-mini",
            versao_prompt="v1.0",
        )

        result = repository.get_by_proposicao(proposicao_id=sample_proposicao.id)

        assert result is not None
        assert result.proposicao_id == sample_proposicao.id
        assert result.headline == "Projeto aumenta salário mínimo"

    def test_get_by_proposicao_returns_most_recent(self, repository, sample_proposicao):
        """Test: get_by_proposicao retorna o enriquecimento mais recente."""
        output_v1 = EnriquecimentoOutput(
            headline="Headline v1",
            resumo_simples="Resumo v1",
            impacto_cidadao=["Impacto v1"],
            confianca=0.7,
        )
        repository.upsert(
            proposicao_id=sample_proposicao.id,
            resultado=output_v1,
            modelo="gpt-4o-mini",
            versao_prompt="v1.0",
        )

        output_v2 = EnriquecimentoOutput(
            headline="Headline v2",
            resumo_simples="Resumo v2",
            impacto_cidadao=["Impacto v2"],
            confianca=0.9,
        )
        repository.upsert(
            proposicao_id=sample_proposicao.id,
            resultado=output_v2,
            modelo="gpt-4o-mini",
            versao_prompt="v2.0",
        )

        result = repository.get_by_proposicao(proposicao_id=sample_proposicao.id)

        assert result is not None
        assert result.versao_prompt == "v2.0"
        assert result.headline == "Headline v2"
