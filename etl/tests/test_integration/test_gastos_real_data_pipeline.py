"""Validação E2E opcional do pipeline completo com dados reais da fonte cotas."""

from __future__ import annotations

import csv
import os
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

import scripts.run_full_etl as run_full_etl
import src.classificacao.models
import src.deputados.models
import src.gastos.models
import src.proposicoes.models
import src.votacoes.models  # noqa: F401
from src.classificacao.etl import run_classificacao_etl
from src.deputados.etl import run_deputados_etl
from src.deputados.models import Deputado
from src.gastos.etl import run_gastos_etl
from src.gastos.models import Gasto
from src.proposicoes.etl import run_proposicoes_etl
from src.shared.database import Base
from src.votacoes.etl import run_orientacoes_etl, run_votacoes_etl, run_votacoes_proposicoes_etl

pytestmark = [pytest.mark.integration, pytest.mark.slow]

RUN_REAL_DATA_ENV = "RUN_REAL_DATA_PIPELINE"


def _required_files(ano: int) -> tuple[str, ...]:
    return (
        "deputados.csv",
        f"proposicoes-{ano}.csv",
        f"votacoes-{ano}.csv",
        f"votacoesVotos-{ano}.csv",
        f"gastos-{ano}.csv",
        f"votacoesProposicoes-{ano}.csv",
        f"votacoesOrientacoes-{ano}.csv",
    )


def _resolve_real_data_dir(ano: int) -> Path:
    candidates = (
        Path("etl/data/dados_camara"),
        Path("data/dados_camara"),
    )

    required = _required_files(ano)
    for directory in candidates:
        if directory.exists() and all((directory / file_name).exists() for file_name in required):
            return directory

    missing_report: list[str] = []
    for directory in candidates:
        missing = [file_name for file_name in required if not (directory / file_name).exists()]
        missing_report.append(f"{directory}: faltando {', '.join(missing)}")

    raise FileNotFoundError(
        "Dados reais não encontrados para validação do pipeline. "
        + " | ".join(missing_report)
    )


def _subset_limit_for(file_name: str) -> int:
    if file_name == "deputados.csv":
        return 1000
    if file_name.startswith("gastos-"):
        return 200
    if file_name.startswith("votacoesVotos-"):
        return 5000
    return 1500


def _materialize_subset_csv(source: Path, destination: Path, max_rows: int) -> None:
    with source.open("r", encoding="utf-8-sig", newline="") as input_file:
        reader = csv.reader(input_file, delimiter=";")
        with destination.open("w", encoding="utf-8-sig", newline="") as output_file:
            writer = csv.writer(output_file, delimiter=";", lineterminator="\n")
            try:
                header = next(reader)
            except StopIteration as exc:
                raise ValueError(f"CSV vazio: {source}") from exc

            writer.writerow(header)

            for index, row in enumerate(reader, start=1):
                writer.writerow(row)
                if index >= max_rows:
                    break


@pytest.fixture(scope="module")
def real_data_subset_dir(tmp_path_factory) -> Path:
    if os.getenv(RUN_REAL_DATA_ENV) != "1":
        pytest.skip(
            "Validação com dados reais desabilitada. "
            f"Defina {RUN_REAL_DATA_ENV}=1 para executar."
        )

    ano = run_full_etl.settings.CAMARA_ANO
    source_dir = _resolve_real_data_dir(ano)
    subset_dir = tmp_path_factory.mktemp("real_data_subset")

    for file_name in _required_files(ano):
        source = source_dir / file_name
        destination = subset_dir / file_name
        _materialize_subset_csv(
            source=source,
            destination=destination,
            max_rows=_subset_limit_for(file_name),
        )

    return subset_dir


@pytest.fixture
def pipeline_db_session(tmp_path) -> Session:
    db_path = tmp_path / "real_data_pipeline.db"
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def _patch_run_full_with_real_etls(monkeypatch: pytest.MonkeyPatch, db: Session, call_order: list[str]) -> None:
    def _run_deputados(csv_path: str) -> int:
        call_order.append("deputados")
        return run_deputados_etl(csv_path, db)

    def _run_proposicoes(csv_path: str) -> int:
        call_order.append("proposicoes")
        return run_proposicoes_etl(csv_path, db)

    def _run_votacoes(votacoes_csv: str, votos_csv: str) -> int:
        call_order.append("votacoes")
        return run_votacoes_etl(votacoes_csv, votos_csv, db)

    def _run_gastos(csv_path: str) -> int:
        call_order.append("gastos")
        return run_gastos_etl(csv_path, db)

    def _run_votacoes_proposicoes(csv_path: str) -> int:
        call_order.append("votacoes_proposicoes")
        return run_votacoes_proposicoes_etl(csv_path, db)

    def _run_orientacoes(csv_path: str) -> int:
        call_order.append("orientacoes")
        return run_orientacoes_etl(csv_path, db)

    def _run_classificacao() -> int:
        call_order.append("classificacao")
        return run_classificacao_etl(db)

    monkeypatch.setattr(run_full_etl, "run_deputados_etl_with_retry", _run_deputados)
    monkeypatch.setattr(run_full_etl, "run_proposicoes_etl_with_retry", _run_proposicoes)
    monkeypatch.setattr(run_full_etl, "run_votacoes_etl_with_retry", _run_votacoes)
    monkeypatch.setattr(run_full_etl, "run_gastos_etl_with_retry", _run_gastos)
    monkeypatch.setattr(run_full_etl, "run_votacoes_proposicoes_etl", _run_votacoes_proposicoes)
    monkeypatch.setattr(run_full_etl, "run_orientacoes_etl", _run_orientacoes)
    monkeypatch.setattr(run_full_etl, "run_classificacao_etl", _run_classificacao)


def test_run_etl_real_data_happy_path_with_idempotencia_e_integridade(
    real_data_subset_dir: Path,
    pipeline_db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
):
    """Valida happy path com dados reais (subconjunto) e idempotência da carga de gastos."""
    call_order: list[str] = []
    _patch_run_full_with_real_etls(monkeypatch, pipeline_db_session, call_order)

    exit_code = run_full_etl.run_etl(real_data_subset_dir)

    assert exit_code == 0
    assert call_order == [
        "deputados",
        "proposicoes",
        "votacoes",
        "gastos",
        "votacoes_proposicoes",
        "orientacoes",
        "classificacao",
    ]

    deputados_count = pipeline_db_session.query(Deputado).count()
    gastos_count_before_rerun = pipeline_db_session.query(Gasto).count()

    assert deputados_count > 0
    assert gastos_count_before_rerun > 0

    invalid_fk_count = (
        pipeline_db_session.query(Gasto)
        .outerjoin(Deputado, Gasto.deputado_id == Deputado.id)
        .filter(
            Gasto.deputado_id.is_not(None),
            Deputado.id.is_(None),
        )
        .count()
    )
    assert invalid_fk_count == 0

    ano = run_full_etl.settings.CAMARA_ANO
    rerun_result = run_gastos_etl(str(real_data_subset_dir / f"gastos-{ano}.csv"), pipeline_db_session)
    gastos_count_after_rerun = pipeline_db_session.query(Gasto).count()

    assert rerun_result == 0
    assert gastos_count_after_rerun == gastos_count_before_rerun


def test_run_etl_real_data_aborta_em_falha_critica_do_step_gastos(
    real_data_subset_dir: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """Valida abortamento do pipeline quando o step crítico de gastos falha."""
    call_order: list[str] = []

    def _run_deputados(_csv_path: str) -> int:
        call_order.append("deputados")
        return 0

    def _run_proposicoes(_csv_path: str) -> int:
        call_order.append("proposicoes")
        return 0

    def _run_votacoes(_votacoes_csv: str, _votos_csv: str) -> int:
        call_order.append("votacoes")
        return 0

    def _run_gastos(_csv_path: str) -> int:
        call_order.append("gastos")
        return 1

    def _run_votacoes_proposicoes(_csv_path: str) -> int:
        call_order.append("votacoes_proposicoes")
        return 0

    def _run_orientacoes(_csv_path: str) -> int:
        call_order.append("orientacoes")
        return 0

    def _run_classificacao() -> int:
        call_order.append("classificacao")
        return 0

    monkeypatch.setattr(run_full_etl, "run_deputados_etl_with_retry", _run_deputados)
    monkeypatch.setattr(run_full_etl, "run_proposicoes_etl_with_retry", _run_proposicoes)
    monkeypatch.setattr(run_full_etl, "run_votacoes_etl_with_retry", _run_votacoes)
    monkeypatch.setattr(run_full_etl, "run_gastos_etl_with_retry", _run_gastos)
    monkeypatch.setattr(run_full_etl, "run_votacoes_proposicoes_etl", _run_votacoes_proposicoes)
    monkeypatch.setattr(run_full_etl, "run_orientacoes_etl", _run_orientacoes)
    monkeypatch.setattr(run_full_etl, "run_classificacao_etl", _run_classificacao)

    exit_code = run_full_etl.run_etl(real_data_subset_dir)

    assert exit_code == 1
    assert call_order == ["deputados", "proposicoes", "votacoes", "gastos"]
