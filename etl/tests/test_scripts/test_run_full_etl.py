"""Testes unitários para o orquestrador completo `scripts/run_full_etl.py`."""

from __future__ import annotations

import logging
from pathlib import Path
from types import SimpleNamespace

import pytest

import scripts.run_full_etl as run_full_etl


def _touch(path: Path) -> None:
    path.write_text("coluna\nvalor\n", encoding="utf-8")


def _create_run_full_required_files(data_dir: Path, ano: int, include_orientacoes: bool = True) -> None:
    required = [
        "deputados.csv",
        f"proposicoes-{ano}.csv",
        f"votacoes-{ano}.csv",
        f"votacoesVotos-{ano}.csv",
        f"gastos-{ano}.csv",
        f"votacoesProposicoes-{ano}.csv",
    ]
    if include_orientacoes:
        required.append(f"votacoesOrientacoes-{ano}.csv")

    for name in required:
        _touch(data_dir / name)


class TestRetryWithBackoff:
    """Cobre o decorator de retry com backoff."""

    def test_retry_recupera_em_erro_transiente(self, monkeypatch):
        sleeps: list[int] = []
        monkeypatch.setattr(run_full_etl.time, "sleep", lambda seconds: sleeps.append(seconds))
        calls = {"count": 0}

        @run_full_etl.retry_with_backoff(max_retries=3, initial_wait=1)
        def _fn():
            calls["count"] += 1
            if calls["count"] == 1:
                raise ConnectionError("falha transitória")
            return 0

        assert _fn() == 0
        assert calls["count"] == 2
        assert sleeps == [1]

    def test_retry_nao_reexecuta_erro_nao_transiente(self):
        calls = {"count": 0}

        @run_full_etl.retry_with_backoff(max_retries=3, initial_wait=1)
        def _fn():
            calls["count"] += 1
            raise ValueError("erro de validação")

        with pytest.raises(ValueError):
            _fn()
        assert calls["count"] == 1

    def test_retry_exaure_tentativas_para_erro_transiente(self, monkeypatch):
        monkeypatch.setattr(run_full_etl.time, "sleep", lambda _seconds: None)

        @run_full_etl.retry_with_backoff(max_retries=3, initial_wait=1)
        def _fn():
            raise TimeoutError("sempre falha")

        with pytest.raises(TimeoutError):
            _fn()


class TestWrappers:
    """Valida wrappers decorados."""

    def test_run_deputados_wrapper_chama_funcao_base(self, monkeypatch):
        monkeypatch.setattr(run_full_etl, "run_deputados_etl", lambda _csv: 0)
        assert run_full_etl.run_deputados_etl_with_retry("deps.csv") == 0

    def test_run_proposicoes_wrapper_chama_funcao_base(self, monkeypatch):
        monkeypatch.setattr(run_full_etl, "run_proposicoes_etl", lambda _csv: 0)
        assert run_full_etl.run_proposicoes_etl_with_retry("props.csv") == 0

    def test_run_votacoes_wrapper_chama_funcao_base(self, monkeypatch):
        monkeypatch.setattr(run_full_etl, "run_votacoes_etl", lambda _vot, _votos: 0)
        assert run_full_etl.run_votacoes_etl_with_retry("vot.csv", "votos.csv") == 0

    def test_run_gastos_wrapper_chama_funcao_base(self, monkeypatch):
        monkeypatch.setattr(run_full_etl, "run_gastos_etl", lambda _csv: 0)
        assert run_full_etl.run_gastos_etl_with_retry("gastos.csv") == 0


class TestRunMigrations:
    """Cobertura para execução de migrations."""

    def test_run_migrations_sucesso(self, monkeypatch):
        monkeypatch.setattr(
            run_full_etl.subprocess,
            "run",
            lambda *_args, **_kwargs: SimpleNamespace(returncode=0, stdout="ok\nhead", stderr=""),
        )
        assert run_full_etl.run_migrations() == 0

    def test_run_migrations_retorna_erro_quando_subprocess_falha(self, monkeypatch):
        monkeypatch.setattr(
            run_full_etl.subprocess,
            "run",
            lambda *_args, **_kwargs: SimpleNamespace(returncode=1, stdout="", stderr="falha alembic"),
        )
        assert run_full_etl.run_migrations() == 1

    def test_run_migrations_trata_excecao(self, monkeypatch):
        def _raise(*_args, **_kwargs):
            raise RuntimeError("erro inesperado")

        monkeypatch.setattr(run_full_etl.subprocess, "run", _raise)
        assert run_full_etl.run_migrations() == 1


class TestRunDownload:
    """Cobertura para fase de download."""

    def test_run_download_sucesso(self, monkeypatch, tmp_path):
        stats = SimpleNamespace(failed=0)
        monkeypatch.setattr(run_full_etl.settings, "TEMP_DOWNLOAD_DIR", tmp_path)
        monkeypatch.setattr(run_full_etl, "download_all_files", lambda **_kwargs: stats)
        monkeypatch.setattr(run_full_etl, "print_summary", lambda _stats: None)
        assert run_full_etl.run_download() == 0

    def test_run_download_falha_quando_ha_arquivos_com_erro(self, monkeypatch, tmp_path):
        stats = SimpleNamespace(failed=2)
        monkeypatch.setattr(run_full_etl.settings, "TEMP_DOWNLOAD_DIR", tmp_path)
        monkeypatch.setattr(run_full_etl, "download_all_files", lambda **_kwargs: stats)
        monkeypatch.setattr(run_full_etl, "print_summary", lambda _stats: None)
        assert run_full_etl.run_download() == 1


class TestRunEtl:
    """Cobertura de fluxo da função `run_etl`."""

    def test_run_etl_fluxo_completo_sucesso(self, monkeypatch, tmp_path):
        ano = run_full_etl.settings.CAMARA_ANO
        _create_run_full_required_files(tmp_path, ano, include_orientacoes=True)

        monkeypatch.setattr(run_full_etl, "run_deputados_etl_with_retry", lambda _csv: 0)
        monkeypatch.setattr(run_full_etl, "run_proposicoes_etl_with_retry", lambda _csv: 0)
        monkeypatch.setattr(run_full_etl, "run_votacoes_etl_with_retry", lambda _v, _vv: 0)
        monkeypatch.setattr(run_full_etl, "run_gastos_etl_with_retry", lambda _csv: 0)
        monkeypatch.setattr(run_full_etl, "run_votacoes_proposicoes_etl", lambda _csv: None)
        monkeypatch.setattr(run_full_etl, "run_orientacoes_etl", lambda _csv: None)
        monkeypatch.setattr(run_full_etl, "run_classificacao_etl", lambda: None)

        assert run_full_etl.run_etl(tmp_path) == 0

    def test_run_etl_falha_quando_arquivo_deputados_ausente(self, tmp_path):
        assert run_full_etl.run_etl(tmp_path) == 1

    def test_run_etl_falha_quando_etl_deputados_retorna_erro(self, monkeypatch, tmp_path):
        ano = run_full_etl.settings.CAMARA_ANO
        _create_run_full_required_files(tmp_path, ano)
        monkeypatch.setattr(run_full_etl, "run_deputados_etl_with_retry", lambda _csv: 1)
        assert run_full_etl.run_etl(tmp_path) == 1

    def test_run_etl_falha_quando_arquivo_proposicoes_ausente(self, monkeypatch, tmp_path):
        _touch(tmp_path / "deputados.csv")
        monkeypatch.setattr(run_full_etl, "run_deputados_etl_with_retry", lambda _csv: 0)
        assert run_full_etl.run_etl(tmp_path) == 1

    def test_run_etl_falha_quando_etl_proposicoes_retorna_erro(self, monkeypatch, tmp_path):
        ano = run_full_etl.settings.CAMARA_ANO
        _touch(tmp_path / "deputados.csv")
        _touch(tmp_path / f"proposicoes-{ano}.csv")
        monkeypatch.setattr(run_full_etl, "run_deputados_etl_with_retry", lambda _csv: 0)
        monkeypatch.setattr(run_full_etl, "run_proposicoes_etl_with_retry", lambda _csv: 1)
        assert run_full_etl.run_etl(tmp_path) == 1

    def test_run_etl_falha_quando_arquivo_votacoes_ausente(self, monkeypatch, tmp_path):
        ano = run_full_etl.settings.CAMARA_ANO
        _touch(tmp_path / "deputados.csv")
        _touch(tmp_path / f"proposicoes-{ano}.csv")
        monkeypatch.setattr(run_full_etl, "run_deputados_etl_with_retry", lambda _csv: 0)
        monkeypatch.setattr(run_full_etl, "run_proposicoes_etl_with_retry", lambda _csv: 0)
        assert run_full_etl.run_etl(tmp_path) == 1

    def test_run_etl_falha_quando_arquivo_votos_ausente(self, monkeypatch, tmp_path):
        ano = run_full_etl.settings.CAMARA_ANO
        _touch(tmp_path / "deputados.csv")
        _touch(tmp_path / f"proposicoes-{ano}.csv")
        _touch(tmp_path / f"votacoes-{ano}.csv")
        monkeypatch.setattr(run_full_etl, "run_deputados_etl_with_retry", lambda _csv: 0)
        monkeypatch.setattr(run_full_etl, "run_proposicoes_etl_with_retry", lambda _csv: 0)
        assert run_full_etl.run_etl(tmp_path) == 1

    def test_run_etl_falha_quando_etl_votacoes_retorna_erro(self, monkeypatch, tmp_path):
        ano = run_full_etl.settings.CAMARA_ANO
        _touch(tmp_path / "deputados.csv")
        _touch(tmp_path / f"proposicoes-{ano}.csv")
        _touch(tmp_path / f"votacoes-{ano}.csv")
        _touch(tmp_path / f"votacoesVotos-{ano}.csv")
        monkeypatch.setattr(run_full_etl, "run_deputados_etl_with_retry", lambda _csv: 0)
        monkeypatch.setattr(run_full_etl, "run_proposicoes_etl_with_retry", lambda _csv: 0)
        monkeypatch.setattr(run_full_etl, "run_votacoes_etl_with_retry", lambda _v, _vv: 1)
        assert run_full_etl.run_etl(tmp_path) == 1

    def test_run_etl_falha_quando_arquivo_gastos_ausente(self, monkeypatch, tmp_path):
        ano = run_full_etl.settings.CAMARA_ANO
        _touch(tmp_path / "deputados.csv")
        _touch(tmp_path / f"proposicoes-{ano}.csv")
        _touch(tmp_path / f"votacoes-{ano}.csv")
        _touch(tmp_path / f"votacoesVotos-{ano}.csv")
        monkeypatch.setattr(run_full_etl, "run_deputados_etl_with_retry", lambda _csv: 0)
        monkeypatch.setattr(run_full_etl, "run_proposicoes_etl_with_retry", lambda _csv: 0)
        monkeypatch.setattr(run_full_etl, "run_votacoes_etl_with_retry", lambda _v, _vv: 0)
        assert run_full_etl.run_etl(tmp_path) == 1

    def test_run_etl_falha_quando_etl_gastos_retorna_erro(self, monkeypatch, tmp_path):
        ano = run_full_etl.settings.CAMARA_ANO
        _touch(tmp_path / "deputados.csv")
        _touch(tmp_path / f"proposicoes-{ano}.csv")
        _touch(tmp_path / f"votacoes-{ano}.csv")
        _touch(tmp_path / f"votacoesVotos-{ano}.csv")
        _touch(tmp_path / f"gastos-{ano}.csv")
        monkeypatch.setattr(run_full_etl, "run_deputados_etl_with_retry", lambda _csv: 0)
        monkeypatch.setattr(run_full_etl, "run_proposicoes_etl_with_retry", lambda _csv: 0)
        monkeypatch.setattr(run_full_etl, "run_votacoes_etl_with_retry", lambda _v, _vv: 0)
        monkeypatch.setattr(run_full_etl, "run_gastos_etl_with_retry", lambda _csv: 1)
        assert run_full_etl.run_etl(tmp_path) == 1

    def test_run_etl_falha_quando_arquivo_votacoes_proposicoes_ausente(self, monkeypatch, tmp_path):
        ano = run_full_etl.settings.CAMARA_ANO
        _touch(tmp_path / "deputados.csv")
        _touch(tmp_path / f"proposicoes-{ano}.csv")
        _touch(tmp_path / f"votacoes-{ano}.csv")
        _touch(tmp_path / f"votacoesVotos-{ano}.csv")
        _touch(tmp_path / f"gastos-{ano}.csv")
        monkeypatch.setattr(run_full_etl, "run_deputados_etl_with_retry", lambda _csv: 0)
        monkeypatch.setattr(run_full_etl, "run_proposicoes_etl_with_retry", lambda _csv: 0)
        monkeypatch.setattr(run_full_etl, "run_votacoes_etl_with_retry", lambda _v, _vv: 0)
        monkeypatch.setattr(run_full_etl, "run_gastos_etl_with_retry", lambda _csv: 0)
        assert run_full_etl.run_etl(tmp_path) == 1

    def test_run_etl_falha_quando_votacoes_proposicoes_lanca_excecao(self, monkeypatch, tmp_path):
        ano = run_full_etl.settings.CAMARA_ANO
        _create_run_full_required_files(tmp_path, ano)

        monkeypatch.setattr(run_full_etl, "run_deputados_etl_with_retry", lambda _csv: 0)
        monkeypatch.setattr(run_full_etl, "run_proposicoes_etl_with_retry", lambda _csv: 0)
        monkeypatch.setattr(run_full_etl, "run_votacoes_etl_with_retry", lambda _v, _vv: 0)
        monkeypatch.setattr(run_full_etl, "run_gastos_etl_with_retry", lambda _csv: 0)
        monkeypatch.setattr(
            run_full_etl,
            "run_votacoes_proposicoes_etl",
            lambda _csv: (_ for _ in ()).throw(RuntimeError("falha crítica")),
        )

        assert run_full_etl.run_etl(tmp_path) == 1

    def test_run_etl_continua_sem_orientacoes_quando_arquivo_ausente(self, monkeypatch, tmp_path):
        ano = run_full_etl.settings.CAMARA_ANO
        _create_run_full_required_files(tmp_path, ano, include_orientacoes=False)

        monkeypatch.setattr(run_full_etl, "run_deputados_etl_with_retry", lambda _csv: 0)
        monkeypatch.setattr(run_full_etl, "run_proposicoes_etl_with_retry", lambda _csv: 0)
        monkeypatch.setattr(run_full_etl, "run_votacoes_etl_with_retry", lambda _v, _vv: 0)
        monkeypatch.setattr(run_full_etl, "run_gastos_etl_with_retry", lambda _csv: 0)
        monkeypatch.setattr(run_full_etl, "run_votacoes_proposicoes_etl", lambda _csv: None)
        monkeypatch.setattr(run_full_etl, "run_classificacao_etl", lambda: None)

        assert run_full_etl.run_etl(tmp_path) == 0

    def test_run_etl_continua_quando_orientacoes_lanca_excecao(self, monkeypatch, tmp_path):
        ano = run_full_etl.settings.CAMARA_ANO
        _create_run_full_required_files(tmp_path, ano, include_orientacoes=True)

        monkeypatch.setattr(run_full_etl, "run_deputados_etl_with_retry", lambda _csv: 0)
        monkeypatch.setattr(run_full_etl, "run_proposicoes_etl_with_retry", lambda _csv: 0)
        monkeypatch.setattr(run_full_etl, "run_votacoes_etl_with_retry", lambda _v, _vv: 0)
        monkeypatch.setattr(run_full_etl, "run_gastos_etl_with_retry", lambda _csv: 0)
        monkeypatch.setattr(run_full_etl, "run_votacoes_proposicoes_etl", lambda _csv: None)
        monkeypatch.setattr(
            run_full_etl,
            "run_orientacoes_etl",
            lambda _csv: (_ for _ in ()).throw(RuntimeError("orientações indisponíveis")),
        )
        monkeypatch.setattr(run_full_etl, "run_classificacao_etl", lambda: None)

        assert run_full_etl.run_etl(tmp_path) == 0

    def test_run_etl_continua_quando_classificacao_lanca_excecao(self, monkeypatch, tmp_path):
        ano = run_full_etl.settings.CAMARA_ANO
        _create_run_full_required_files(tmp_path, ano, include_orientacoes=True)

        monkeypatch.setattr(run_full_etl, "run_deputados_etl_with_retry", lambda _csv: 0)
        monkeypatch.setattr(run_full_etl, "run_proposicoes_etl_with_retry", lambda _csv: 0)
        monkeypatch.setattr(run_full_etl, "run_votacoes_etl_with_retry", lambda _v, _vv: 0)
        monkeypatch.setattr(run_full_etl, "run_gastos_etl_with_retry", lambda _csv: 0)
        monkeypatch.setattr(run_full_etl, "run_votacoes_proposicoes_etl", lambda _csv: None)
        monkeypatch.setattr(run_full_etl, "run_orientacoes_etl", lambda _csv: None)
        monkeypatch.setattr(
            run_full_etl,
            "run_classificacao_etl",
            lambda: (_ for _ in ()).throw(RuntimeError("serviço indisponível")),
        )

        assert run_full_etl.run_etl(tmp_path) == 0


class TestMain:
    """Cobertura da função principal do pipeline completo."""

    def test_main_retorna_sucesso(self, monkeypatch, tmp_path):
        monkeypatch.setattr(run_full_etl.settings, "TEMP_DOWNLOAD_DIR", tmp_path)
        monkeypatch.setattr(run_full_etl, "run_migrations", lambda: 0)
        monkeypatch.setattr(run_full_etl, "run_download", lambda: 0)
        monkeypatch.setattr(run_full_etl, "run_etl", lambda _data_dir: 0)
        assert run_full_etl.main() == 0

    def test_main_falha_se_migrations_falhar(self, monkeypatch):
        monkeypatch.setattr(run_full_etl, "run_migrations", lambda: 1)
        assert run_full_etl.main() == 1

    def test_main_falha_se_download_falhar(self, monkeypatch):
        monkeypatch.setattr(run_full_etl, "run_migrations", lambda: 0)
        monkeypatch.setattr(run_full_etl, "run_download", lambda: 1)
        assert run_full_etl.main() == 1

    def test_main_falha_se_etl_falhar(self, monkeypatch, tmp_path):
        monkeypatch.setattr(run_full_etl.settings, "TEMP_DOWNLOAD_DIR", tmp_path)
        monkeypatch.setattr(run_full_etl, "run_migrations", lambda: 0)
        monkeypatch.setattr(run_full_etl, "run_download", lambda: 0)
        monkeypatch.setattr(run_full_etl, "run_etl", lambda _data_dir: 1)
        assert run_full_etl.main() == 1


class TestSetupLogging:
    """Cobertura de configuração de logging."""

    def test_setup_logging_configura_root_logger_info(self):
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        run_full_etl.setup_logging()

        assert root_logger.level == logging.INFO
        assert len(root_logger.handlers) >= 1
