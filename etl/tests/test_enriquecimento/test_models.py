"""Testes para models SQLAlchemy do domínio de Enriquecimento LLM.

Validam a instanciação do model EnriquecimentoLLM, __repr__,
__tablename__ e table_args (constraints e indexes).
"""

from src.enriquecimento.models import EnriquecimentoLLM


class TestEnriquecimentoLLM:
    """Testes para o model EnriquecimentoLLM."""

    def test_model_instantiation_with_required_fields(self):
        """Test: EnriquecimentoLLM pode ser instanciado com campos obrigatórios."""
        enriquecimento = EnriquecimentoLLM(
            proposicao_id=123,
            modelo="gpt-4o-mini",
            versao_prompt="v1.0",
            confianca=0.85,
        )
        assert enriquecimento.proposicao_id == 123
        assert enriquecimento.modelo == "gpt-4o-mini"
        assert enriquecimento.versao_prompt == "v1.0"
        assert enriquecimento.confianca == 0.85

    def test_model_repr(self):
        """Test: __repr__ retorna formato esperado."""
        enriquecimento = EnriquecimentoLLM(
            id=1,
            proposicao_id=123,
            modelo="gpt-4o-mini",
            versao_prompt="v1.0",
            confianca=0.85,
        )
        repr_str = repr(enriquecimento)
        assert "EnriquecimentoLLM" in repr_str
        assert "proposicao_id=123" in repr_str
        assert "modelo='gpt-4o-mini'" in repr_str
        assert "versao_prompt='v1.0'" in repr_str
        assert "confianca=0.85" in repr_str

    def test_model_tablename(self):
        """Test: __tablename__ é 'enriquecimentos_llm'."""
        assert EnriquecimentoLLM.__tablename__ == "enriquecimentos_llm"

    def test_table_args_include_unique_constraint(self):
        """Test: table_args inclui unique constraint uq_enriquecimento."""
        table_args = EnriquecimentoLLM.__table_args__
        constraint_names = [arg.name for arg in table_args if hasattr(arg, "name")]
        assert "uq_enriquecimento" in constraint_names

    def test_table_args_include_indexes(self):
        """Test: table_args inclui os indexes esperados."""
        table_args = EnriquecimentoLLM.__table_args__
        index_names = [arg.name for arg in table_args if hasattr(arg, "name")]
        assert "ix_enriquecimentos_proposicao" in index_names
        assert "ix_enriquecimentos_confianca" in index_names
        assert "ix_enriquecimentos_revisao" in index_names

    def test_model_default_values(self):
        """Test: EnriquecimentoLLM usa defaults corretos para campos opcionais."""
        enriquecimento = EnriquecimentoLLM(
            proposicao_id=1,
            modelo="gpt-4o-mini",
            versao_prompt="v1.0",
        )
        assert enriquecimento.headline is None
        assert enriquecimento.resumo_simples is None
        assert enriquecimento.impacto_cidadao is None
        assert enriquecimento.tokens_input is None
        assert enriquecimento.tokens_output is None

    def test_model_with_all_fields(self):
        """Test: EnriquecimentoLLM aceita todos os campos."""
        enriquecimento = EnriquecimentoLLM(
            id=5,
            proposicao_id=42,
            modelo="gpt-4o-mini",
            versao_prompt="v1.0",
            headline="Headline teste",
            resumo_simples="Resumo teste",
            impacto_cidadao='["Impacto 1", "Impacto 2"]',
            confianca=0.95,
            necessita_revisao=False,
            tokens_input=100,
            tokens_output=200,
        )
        assert enriquecimento.id == 5
        assert enriquecimento.headline == "Headline teste"
        assert enriquecimento.tokens_input == 100
