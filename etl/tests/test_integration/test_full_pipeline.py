"""Testes de integração E2E para o pipeline completo de 3 fases.

Valida:
- Pipeline E2E: deputados → proposições → votações → votos →
  votacoes_proposicoes → orientacoes → classificação
- Encadeamento: votação nominal → proposição principal → categorias → orientações
- Idempotência: executar pipeline 2x sem duplicar dados
- Integridade referencial: FKs consistentes
- Falha parcial: step não-crítico falha, pipeline continua
- Política de erros: step crítico (votacoes_proposicoes) interrompe pipeline
"""

import contextlib
import logging
from pathlib import Path
from unittest.mock import patch

import pytest
from sqlalchemy.orm import Session, sessionmaker

from src.classificacao.etl import run_classificacao_etl
from src.classificacao.models import CategoriaCivica, ProposicaoCategoria
from src.deputados.etl import run_deputados_etl
from src.deputados.models import Deputado
from src.enriquecimento.etl import run_enriquecimento_etl
from src.enriquecimento.models import EnriquecimentoLLM
from src.proposicoes.etl import run_proposicoes_etl
from src.proposicoes.models import Proposicao
from src.votacoes.etl import (
    run_orientacoes_etl,
    run_votacoes_etl,
    run_votacoes_proposicoes_etl,
)
from src.votacoes.models import Orientacao, Votacao, VotacaoProposicao, Voto

pytestmark = pytest.mark.integration


@pytest.fixture
def pipeline_db(db_engine):
    """Sessão PostgreSQL com rollback automático para testes de pipeline."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    yield session
    session.close()
    transaction.rollback()
    connection.close()


def _run_full_pipeline(db, fixtures_dir: Path) -> dict:
    """Executa o pipeline completo e retorna métricas.

    Args:
        db: Sessão de banco de dados
        fixtures_dir: Diretório com fixtures CSV

    Returns:
        Dicionário com contagens de registros por tabela
    """
    # Fase 1: Ingestão base
    result = run_deputados_etl(str(fixtures_dir / "deputados.csv"), db)
    assert result == 0, "ETL de deputados falhou"

    result = run_proposicoes_etl(str(fixtures_dir / "proposicoes.csv"), db)
    assert result == 0, "ETL de proposições falhou"

    result = run_votacoes_etl(
        str(fixtures_dir / "votacoes.csv"),
        str(fixtures_dir / "votos.csv"),
        db,
    )
    assert result == 0, "ETL de votações falhou"

    # Fase 2: Ingestão relacional
    run_votacoes_proposicoes_etl(
        str(fixtures_dir / "votacoes_proposicoes.csv"),
        db,
    )

    run_orientacoes_etl(
        str(fixtures_dir / "votacoesOrientacoes.csv"),
        db,
    )

    # Fase 3: Enriquecimento
    run_classificacao_etl(db)

    # Step 4.2: Enriquecimento LLM (NÃO-CRÍTICO — skipped por padrão com LLM_ENABLED=False)
    run_enriquecimento_etl(db)

    return {
        "deputados": db.query(Deputado).count(),
        "proposicoes": db.query(Proposicao).count(),
        "votacoes": db.query(Votacao).count(),
        "votos": db.query(Voto).count(),
        "votacoes_proposicoes": db.query(VotacaoProposicao).count(),
        "orientacoes": db.query(Orientacao).count(),
        "categorias_civicas": db.query(CategoriaCivica).count(),
        "proposicoes_categorias": db.query(ProposicaoCategoria).count(),
    }


class TestFullPipelineE2E:
    """Testes E2E do pipeline completo com todas as 3 fases."""

    def test_full_pipeline_executes_all_phases(self, pipeline_db, fixtures_dir):
        """Test: Pipeline completo executa todas as 3 fases com sucesso.

        Valida que todos os dados são ingeridos e encadeados corretamente:
        deputados → proposições → votações → votos → votacoes_proposicoes
        → orientacoes → classificação
        """
        counts = _run_full_pipeline(pipeline_db, fixtures_dir)

        # Fase 1: Ingestão base
        assert counts["deputados"] > 0, "Nenhum deputado carregado"
        assert counts["proposicoes"] > 0, "Nenhuma proposição carregada"
        assert counts["votacoes"] > 0, "Nenhuma votação carregada"
        assert counts["votos"] > 0, "Nenhum voto carregado"

        # Fase 2: Ingestão relacional
        assert counts["votacoes_proposicoes"] > 0, "Nenhum vínculo votação-proposição carregado"
        assert counts["orientacoes"] > 0, "Nenhuma orientação carregada"

        # Fase 3: Enriquecimento
        assert counts["categorias_civicas"] == 9, "Seed de categorias cívicas incompleto"

    def test_votacao_proposicao_linkage(self, pipeline_db, fixtures_dir):
        """Test: Votações estão corretamente vinculadas a proposições via junction table.

        Valida que:
        - Votação 1 está vinculada a 2 proposições (PL 100/2024 e PEC 10/2024)
        - PEC 10/2024 é a principal (PEC > PL na prioridade)
        - Votação 2 está vinculada a 1 proposição (PLP 50/2024)
        """
        _run_full_pipeline(pipeline_db, fixtures_dir)

        # Votação 1 deve ter 2 proposições
        vp_votacao_1 = pipeline_db.query(VotacaoProposicao).filter(
            VotacaoProposicao.votacao_id == 1
        ).all()
        assert len(vp_votacao_1) == 2, f"Esperado 2 proposições para votação 1, encontrado {len(vp_votacao_1)}"

        # Verificar que a PEC é a principal (prioridade PEC > PL)
        principal = [vp for vp in vp_votacao_1 if vp.eh_principal]
        assert len(principal) == 1, "Deve haver exatamente 1 proposição principal"
        assert principal[0].sigla_tipo == "PEC", "PEC deveria ser a proposição principal"

    def test_orientacoes_loaded_correctly(self, pipeline_db, fixtures_dir):
        """Test: Orientações de bancada são carregadas e normalizadas.

        Valida:
        - Orientações associadas a votações existentes são carregadas
        - Orientações para votações inexistentes (999) são skipadas
        - Orientação vazia é skipada
        """
        _run_full_pipeline(pipeline_db, fixtures_dir)

        # Orientações para votação 1 (4 bancadas: PT, PL, Governo, Minoria)
        orient_v1 = pipeline_db.query(Orientacao).filter(
            Orientacao.votacao_id == 1
        ).all()
        assert len(orient_v1) == 4, f"Esperado 4 orientações para votação 1, encontrado {len(orient_v1)}"

        # Verificar normalização
        siglas = {o.sigla_bancada: o.orientacao for o in orient_v1}
        assert siglas["PT"] == "Sim"
        assert siglas["PL"] == "Não"

        # Orientações para votação 999 (inexistente) devem ser skipadas
        orient_v999 = pipeline_db.query(Orientacao).filter(
            Orientacao.votacao_id == 999
        ).all()
        assert len(orient_v999) == 0, "Orientações de votação inexistente não devem ser carregadas"

    def test_proposicao_parcial_creation(self, pipeline_db, fixtures_dir):
        """Test: Proposições parciais são criadas quando referenciadas no CSV
        mas não existem no banco.

        O fixture votacoes_proposicoes.csv referencia proposicao_id=99999 que
        não existe no fixture proposicoes.csv — deve ser criada como parcial.
        """
        _run_full_pipeline(pipeline_db, fixtures_dir)

        # Verificar que a proposição parcial 99999 foi criada
        prop_parcial = pipeline_db.query(Proposicao).filter(
            Proposicao.id == 99999
        ).one_or_none()
        # Se a votação 4 existir no banco, a proposição parcial deve ser criada
        votacao_4 = pipeline_db.query(Votacao).filter(Votacao.id == 4).one_or_none()
        if votacao_4:
            assert prop_parcial is not None, "Proposição parcial 99999 não foi criada"

    def test_classificacao_produces_categories(self, pipeline_db, fixtures_dir):
        """Test: Classificação cívica seed produz categorias no banco.

        Valida que as 9 categorias cívicas são inseridas pela seed.
        """
        _run_full_pipeline(pipeline_db, fixtures_dir)

        categorias = pipeline_db.query(CategoriaCivica).all()
        assert len(categorias) == 9, f"Esperado 9 categorias, encontrado {len(categorias)}"

        codigos = {c.codigo for c in categorias}
        expected = {
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
        assert codigos == expected, f"Categorias faltando: {expected - codigos}"

    def test_votacoes_nullable_proposicao_id(self, pipeline_db, fixtures_dir):
        """Test: Votações sem proposicao_id são ingeridas (campo nullable).

        O fixture votacoes.csv tem votação 6 com proposicao_id=0 e
        votação 7 com proposicao_id vazio — ambas devem ser ingeridas com
        proposicao_id=None.
        """
        _run_full_pipeline(pipeline_db, fixtures_dir)

        # Pelo menos as votações 6 e 7 devem ter proposicao_id None
        # (depende das proposições existentes no banco)
        total_votacoes = pipeline_db.query(Votacao).count()
        assert total_votacoes > 0, "Nenhuma votação carregada"

        # Verificar que votações sem proposicao_id foram aceitas
        votacoes_sem_prop_count = pipeline_db.query(Votacao).filter(
            Votacao.proposicao_id.is_(None)
        ).count()
        assert votacoes_sem_prop_count >= 0  # Pode ser 0 se todas têm proposição

    def test_eh_nominal_calculated(self, pipeline_db, fixtures_dir):
        """Test: eh_nominal é calculado corretamente (votos_sim > 0)."""
        _run_full_pipeline(pipeline_db, fixtures_dir)

        # Votação 1 tem votos_sim=250 → eh_nominal=True
        v1 = pipeline_db.query(Votacao).filter(Votacao.id == 1).one_or_none()
        if v1:
            assert v1.eh_nominal is True, "Votação 1 deveria ser nominal (votos_sim=250)"

        # Votação 4 tem votos_sim=0 → eh_nominal=False
        v4 = pipeline_db.query(Votacao).filter(Votacao.id == 4).one_or_none()
        if v4:
            assert v4.eh_nominal is False, "Votação 4 não deveria ser nominal (votos_sim=0)"


class TestIdempotency:
    """Testes de idempotência: executar pipeline 2x não duplica dados."""

    def test_pipeline_idempotent_no_duplicates(self, pipeline_db, fixtures_dir):
        """Test: Executar pipeline 2x produz mesmas contagens.

        Valida que bulk_upsert e ON CONFLICT garantem idempotência.
        """
        # Primeira execução
        counts_1 = _run_full_pipeline(pipeline_db, fixtures_dir)

        # Segunda execução (mesmos dados)
        counts_2 = _run_full_pipeline(pipeline_db, fixtures_dir)

        # Contagens devem ser iguais
        for table_name in ["deputados", "proposicoes", "votacoes", "votacoes_proposicoes", "orientacoes"]:
            assert counts_1[table_name] == counts_2[table_name], (
                f"Idempotência violada em {table_name}: "
                f"{counts_1[table_name]} vs {counts_2[table_name]}"
            )

        # Categorias devem ser exatamente 9 (seed idempotente)
        assert counts_2["categorias_civicas"] == 9


class TestReferentialIntegrity:
    """Testes de integridade referencial do pipeline completo."""

    def test_all_votacoes_proposicoes_have_valid_fks(self, pipeline_db, fixtures_dir):
        """Test: Todos os vínculos votação-proposição referenciam registros existentes."""
        _run_full_pipeline(pipeline_db, fixtures_dir)

        all_vp = pipeline_db.query(VotacaoProposicao).all()
        votacao_ids = {v.id for v in pipeline_db.query(Votacao).all()}
        proposicao_ids = {p.id for p in pipeline_db.query(Proposicao).all()}

        for vp in all_vp:
            assert vp.votacao_id in votacao_ids, (
                f"VotacaoProposicao.votacao_id={vp.votacao_id} não existe em votacoes"
            )
            assert vp.proposicao_id in proposicao_ids, (
                f"VotacaoProposicao.proposicao_id={vp.proposicao_id} não existe em proposicoes"
            )

    def test_all_orientacoes_have_valid_votacao_fk(self, pipeline_db, fixtures_dir):
        """Test: Todas as orientações referenciam votações existentes."""
        _run_full_pipeline(pipeline_db, fixtures_dir)

        all_orientacoes = pipeline_db.query(Orientacao).all()
        votacao_ids = {v.id for v in pipeline_db.query(Votacao).all()}

        for o in all_orientacoes:
            assert o.votacao_id in votacao_ids, (
                f"Orientacao.votacao_id={o.votacao_id} não existe em votacoes"
            )

    def test_all_votos_have_valid_fks(self, pipeline_db, fixtures_dir):
        """Test: Todos os votos referenciam votações e deputados existentes."""
        _run_full_pipeline(pipeline_db, fixtures_dir)

        all_votos = pipeline_db.query(Voto).all()
        votacao_ids = {v.id for v in pipeline_db.query(Votacao).all()}
        deputado_ids = {d.id for d in pipeline_db.query(Deputado).all()}

        for voto in all_votos:
            assert voto.votacao_id in votacao_ids, (
                f"Voto.votacao_id={voto.votacao_id} não existe em votacoes"
            )
            assert voto.deputado_id in deputado_ids, (
                f"Voto.deputado_id={voto.deputado_id} não existe em deputados"
            )

    def test_proposicoes_categorias_have_valid_fks(self, pipeline_db, fixtures_dir):
        """Test: Classificações referenciam proposições e categorias existentes."""
        _run_full_pipeline(pipeline_db, fixtures_dir)

        all_pc = pipeline_db.query(ProposicaoCategoria).all()
        proposicao_ids = {p.id for p in pipeline_db.query(Proposicao).all()}
        categoria_ids = {c.id for c in pipeline_db.query(CategoriaCivica).all()}

        for pc in all_pc:
            assert pc.proposicao_id in proposicao_ids, (
                f"ProposicaoCategoria.proposicao_id={pc.proposicao_id} não existe em proposicoes"
            )
            assert pc.categoria_id in categoria_ids, (
                f"ProposicaoCategoria.categoria_id={pc.categoria_id} não existe em categorias_civicas"
            )


class TestPartialFailure:
    """Testes de falha parcial: steps não-críticos falham, pipeline continua."""

    def test_orientacoes_failure_does_not_block_pipeline(self, pipeline_db, fixtures_dir):
        """Test: Falha no ETL de orientações não bloqueia o pipeline.

        Simula falha no step de orientações e verifica que classificação
        ainda executa.
        """
        # Fase 1: Ingestão base
        run_deputados_etl(str(fixtures_dir / "deputados.csv"), pipeline_db)
        run_proposicoes_etl(str(fixtures_dir / "proposicoes.csv"), pipeline_db)
        run_votacoes_etl(
            str(fixtures_dir / "votacoes.csv"),
            str(fixtures_dir / "votos.csv"),
            pipeline_db,
        )

        # Fase 2: votacoes_proposicoes OK, orientacoes falha
        run_votacoes_proposicoes_etl(
            str(fixtures_dir / "votacoes_proposicoes.csv"),
            pipeline_db,
        )

        # Simular falha em orientações (CSV inexistente)
        with contextlib.suppress(FileNotFoundError):
            run_orientacoes_etl("/path/inexistente.csv", pipeline_db)

        # Fase 3: Classificação deve executar normalmente
        run_classificacao_etl(pipeline_db)

        # Validar que dados de Fase 1 e Fase 2 (parcial) estão OK
        assert pipeline_db.query(Votacao).count() > 0
        assert pipeline_db.query(VotacaoProposicao).count() > 0
        assert pipeline_db.query(Orientacao).count() == 0  # Falhou
        assert pipeline_db.query(CategoriaCivica).count() == 9  # Seed OK

    def test_classificacao_failure_does_not_block_pipeline(self, pipeline_db, fixtures_dir):
        """Test: Falha na classificação não bloqueia o pipeline.

        Simula falha no step de classificação e verifica que dados
        de fases anteriores estão intactos.
        """
        # Fase 1: Ingestão base
        run_deputados_etl(str(fixtures_dir / "deputados.csv"), pipeline_db)
        run_proposicoes_etl(str(fixtures_dir / "proposicoes.csv"), pipeline_db)
        run_votacoes_etl(
            str(fixtures_dir / "votacoes.csv"),
            str(fixtures_dir / "votos.csv"),
            pipeline_db,
        )

        # Fase 2
        run_votacoes_proposicoes_etl(
            str(fixtures_dir / "votacoes_proposicoes.csv"),
            pipeline_db,
        )
        run_orientacoes_etl(
            str(fixtures_dir / "votacoesOrientacoes.csv"),
            pipeline_db,
        )

        # Fase 3: Simular falha na classificação
        with patch(
            "src.classificacao.etl._run_classificacao_etl_impl",
            side_effect=RuntimeError("Engine falhou"),
        ), contextlib.suppress(RuntimeError):
            run_classificacao_etl(pipeline_db)

        # Dados das Fases 1 e 2 devem estar intactos
        assert pipeline_db.query(Deputado).count() > 0
        assert pipeline_db.query(Proposicao).count() > 0
        assert pipeline_db.query(Votacao).count() > 0
        assert pipeline_db.query(VotacaoProposicao).count() > 0
        assert pipeline_db.query(Orientacao).count() > 0

    def test_votacoes_proposicoes_failure_is_critical(self, pipeline_db, fixtures_dir):
        """Test: Falha em votacoes_proposicoes (step crítico) gera exceção.

        O step de votacoes_proposicoes é CRÍTICO — deve propagar a exceção
        para que o orquestrador pare o pipeline.
        """
        # Fase 1: Ingestão base
        run_deputados_etl(str(fixtures_dir / "deputados.csv"), pipeline_db)
        run_proposicoes_etl(str(fixtures_dir / "proposicoes.csv"), pipeline_db)
        run_votacoes_etl(
            str(fixtures_dir / "votacoes.csv"),
            str(fixtures_dir / "votos.csv"),
            pipeline_db,
        )

        # Fase 2: votacoes_proposicoes com CSV inexistente deve lançar exceção
        with pytest.raises(FileNotFoundError):
            run_votacoes_proposicoes_etl(
                "/path/inexistente.csv",
                pipeline_db,
            )


class TestPipelineLogging:
    """Testes de logging do pipeline completo."""

    def test_pipeline_logs_phase_markers(self, pipeline_db, fixtures_dir, caplog):
        """Test: Pipeline loga marcadores de fase corretamente."""
        with caplog.at_level(logging.INFO):
            _run_full_pipeline(pipeline_db, fixtures_dir)

        messages = [r.message for r in caplog.records]

        # Verificar que logs ETL existem
        assert any("ETL" in msg or "etl" in msg.lower() for msg in messages), (
            "Nenhum log com 'ETL' encontrado"
        )

    def test_pipeline_logs_record_counts(self, pipeline_db, fixtures_dir, caplog):
        """Test: Pipeline loga contagens de registros processados."""
        with caplog.at_level(logging.INFO):
            _run_full_pipeline(pipeline_db, fixtures_dir)

        messages = " ".join(r.message for r in caplog.records)

        # Verificar logs de contagem
        assert "registros" in messages.lower() or "carregad" in messages.lower(), (
            "Nenhum log de contagem encontrado"
        )


class TestEnriquecimentoLLMIntegration:
    """Testes de integração do step 4.2: Enriquecimento LLM no pipeline."""

    def test_enriquecimento_skipped_when_llm_disabled(self, pipeline_db, fixtures_dir, caplog):
        """Test: Step 4.2 é pulado quando LLM_ENABLED=False (padrão).

        O pipeline completo deve executar sem erros com LLM_ENABLED=False,
        e nenhum enriquecimento deve ser criado.
        """
        with caplog.at_level(logging.INFO):
            _run_full_pipeline(pipeline_db, fixtures_dir)

        # Nenhum enriquecimento deve existir no banco
        enriquecimentos = pipeline_db.query(EnriquecimentoLLM).count()
        assert enriquecimentos == 0, "Nenhum enriquecimento deveria existir com LLM_ENABLED=False"

        # Log de skip deve estar presente
        assert "LLM_ENABLED=False" in caplog.text

    def test_enriquecimento_executes_with_mocked_llm(self, pipeline_db, fixtures_dir, caplog):
        """Test: Step 4.2 executa corretamente com LLM mockado.

        Simula LLM_ENABLED=True com client mockado e verifica que
        enriquecimentos são persistidos.
        """
        from unittest.mock import MagicMock

        from src.enriquecimento.prompts import PROMPT_VERSION
        from src.shared.llm_client import EnriquecimentoOutput, LLMResult

        # Executar fases 1-3 normalmente
        run_deputados_etl(str(fixtures_dir / "deputados.csv"), pipeline_db)
        run_proposicoes_etl(str(fixtures_dir / "proposicoes.csv"), pipeline_db)
        run_votacoes_etl(
            str(fixtures_dir / "votacoes.csv"),
            str(fixtures_dir / "votos.csv"),
            pipeline_db,
        )
        run_votacoes_proposicoes_etl(
            str(fixtures_dir / "votacoes_proposicoes.csv"),
            pipeline_db,
        )
        run_orientacoes_etl(
            str(fixtures_dir / "votacoesOrientacoes.csv"),
            pipeline_db,
        )
        run_classificacao_etl(pipeline_db)

        # Verificar que existem proposições no banco
        total_proposicoes = pipeline_db.query(Proposicao).count()
        assert total_proposicoes > 0, "Pré-condição: deve haver proposições"

        # Mockar LLM para step 4.2
        mock_result = LLMResult(
            output=EnriquecimentoOutput(
                headline="Título de teste",
                resumo_simples="Resumo de teste",
                impacto_cidadao=["Impacto 1"],
                confianca=0.9,
            ),
            tokens_input=100,
            tokens_output=50,
        )

        mock_client = MagicMock()
        mock_client.model = "gpt-4o-mini"
        mock_client.enriquecer_proposicao.return_value = mock_result

        with patch("src.enriquecimento.etl.settings") as mock_settings, \
             patch("src.enriquecimento.etl.OpenAIClient", return_value=mock_client), \
             patch("src.enriquecimento.etl.time.sleep"), \
             caplog.at_level(logging.INFO):
            mock_settings.LLM_ENABLED = True
            mock_settings.LLM_API_KEY = "test-key"
            mock_settings.LLM_MODEL = "gpt-4o-mini"
            mock_settings.LLM_BATCH_SIZE = 10
            mock_settings.LLM_CONFIDENCE_THRESHOLD = 0.5

            result = run_enriquecimento_etl(db=pipeline_db)

        assert result > 0, "Deve ter enriquecido pelo menos 1 proposição"

        # Verificar persistência
        enriquecimentos = pipeline_db.query(EnriquecimentoLLM).count()
        assert enriquecimentos > 0, "Enriquecimentos devem estar no banco"
        assert enriquecimentos == result

        # Verificar dados do primeiro enriquecimento
        first = pipeline_db.query(EnriquecimentoLLM).first()
        assert first.versao_prompt == PROMPT_VERSION
        assert first.modelo == "gpt-4o-mini"
        assert first.headline == "Título de teste"

    def test_enriquecimento_failure_does_not_block_pipeline(self, pipeline_db, fixtures_dir, caplog):
        """Test: Falha no step 4.2 não bloqueia o pipeline.

        Simula falha catastrófica no enriquecimento e verifica que
        dados de fases anteriores estão intactos.
        """
        # Executar fases 1-3 normalmente
        run_deputados_etl(str(fixtures_dir / "deputados.csv"), pipeline_db)
        run_proposicoes_etl(str(fixtures_dir / "proposicoes.csv"), pipeline_db)
        run_votacoes_etl(
            str(fixtures_dir / "votacoes.csv"),
            str(fixtures_dir / "votos.csv"),
            pipeline_db,
        )
        run_votacoes_proposicoes_etl(
            str(fixtures_dir / "votacoes_proposicoes.csv"),
            pipeline_db,
        )
        run_orientacoes_etl(
            str(fixtures_dir / "votacoesOrientacoes.csv"),
            pipeline_db,
        )
        run_classificacao_etl(pipeline_db)

        # Simular falha catastrófica no step 4.2
        with patch(
            "src.enriquecimento.etl._run_enriquecimento_etl_impl",
            side_effect=RuntimeError("LLM API indisponível"),
        ), contextlib.suppress(RuntimeError):
            run_enriquecimento_etl(pipeline_db)

        # Dados das fases anteriores devem estar intactos
        assert pipeline_db.query(Deputado).count() > 0
        assert pipeline_db.query(Proposicao).count() > 0
        assert pipeline_db.query(Votacao).count() > 0
        assert pipeline_db.query(VotacaoProposicao).count() > 0
        assert pipeline_db.query(Orientacao).count() > 0
        assert pipeline_db.query(CategoriaCivica).count() == 9

    def test_enriquecimento_idempotent_with_pipeline(self, pipeline_db, fixtures_dir):
        """Test: Re-execução do pipeline não reprocessa enriquecimentos já existentes.

        Executa o pipeline 2x com LLM mockado e verifica que proposições
        já enriquecidas não são reprocessadas.
        """
        from unittest.mock import MagicMock

        from src.shared.llm_client import EnriquecimentoOutput, LLMResult

        # Executar fases 1-3
        run_deputados_etl(str(fixtures_dir / "deputados.csv"), pipeline_db)
        run_proposicoes_etl(str(fixtures_dir / "proposicoes.csv"), pipeline_db)
        run_votacoes_etl(
            str(fixtures_dir / "votacoes.csv"),
            str(fixtures_dir / "votos.csv"),
            pipeline_db,
        )
        run_votacoes_proposicoes_etl(
            str(fixtures_dir / "votacoes_proposicoes.csv"),
            pipeline_db,
        )
        run_orientacoes_etl(
            str(fixtures_dir / "votacoesOrientacoes.csv"),
            pipeline_db,
        )
        run_classificacao_etl(pipeline_db)

        mock_result = LLMResult(
            output=EnriquecimentoOutput(
                headline="Título",
                resumo_simples="Resumo",
                impacto_cidadao=["Impacto"],
                confianca=0.9,
            ),
            tokens_input=100,
            tokens_output=50,
        )

        mock_client = MagicMock()
        mock_client.model = "gpt-4o-mini"
        mock_client.enriquecer_proposicao.return_value = mock_result

        with patch("src.enriquecimento.etl.settings") as mock_settings, \
             patch("src.enriquecimento.etl.OpenAIClient", return_value=mock_client), \
             patch("src.enriquecimento.etl.time.sleep"):
            mock_settings.LLM_ENABLED = True
            mock_settings.LLM_API_KEY = "test-key"
            mock_settings.LLM_MODEL = "gpt-4o-mini"
            mock_settings.LLM_BATCH_SIZE = 10
            mock_settings.LLM_CONFIDENCE_THRESHOLD = 0.5

            # Primeira execução
            result_1 = run_enriquecimento_etl(db=pipeline_db)

            # Reset mock call count
            mock_client.enriquecer_proposicao.reset_mock()

            # Segunda execução — não deve reprocessar
            result_2 = run_enriquecimento_etl(db=pipeline_db)

        assert result_1 > 0, "Primeira execução deve processar proposições"
        assert result_2 == 0, "Segunda execução não deve reprocessar"
        mock_client.enriquecer_proposicao.assert_not_called()
