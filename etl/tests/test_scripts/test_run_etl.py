"""Testes unitários para `scripts/run_etl.py`."""

from __future__ import annotations

import logging

import pytest

import scripts.run_etl as run_etl


class TestRetryWithBackoff:
    """Cobre o decorator de retry."""

    def test_retry_recupera_erro_transiente(self, monkeypatch):
        sleeps: list[int] = []
        monkeypatch.setattr(run_etl.time, "sleep", lambda seconds: sleeps.append(seconds))
        calls = {"count": 0}

        @run_etl.retry_with_backoff(max_retries=3, initial_wait=1)
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

        @run_etl.retry_with_backoff(max_retries=3, initial_wait=1)
        def _fn():
            calls["count"] += 1
            raise ValueError("erro de validação")

        with pytest.raises(ValueError):
            _fn()
        assert calls["count"] == 1

    def test_retry_exaure_todas_as_tentativas(self, monkeypatch):
        monkeypatch.setattr(run_etl.time, "sleep", lambda _seconds: None)

        @run_etl.retry_with_backoff(max_retries=3, initial_wait=1)
        def _fn():
            raise OSError("erro transiente recorrente")

        with pytest.raises(OSError):
            _fn()


class TestWrappers:
    """Valida wrappers do script."""

    def test_run_deputados_wrapper(self, monkeypatch):
        monkeypatch.setattr(run_etl, "run_deputados_etl", lambda _csv: 0)
        assert run_etl.run_deputados_etl_with_retry("deputados.csv") == 0

    def test_run_proposicoes_wrapper(self, monkeypatch):
        monkeypatch.setattr(run_etl, "run_proposicoes_etl", lambda _csv: 0)
        assert run_etl.run_proposicoes_etl_with_retry("proposicoes.csv") == 0

    def test_run_votacoes_wrapper(self, monkeypatch):
        monkeypatch.setattr(run_etl, "run_votacoes_etl", lambda _v, _vv: 0)
        assert run_etl.run_votacoes_etl_with_retry("votacoes.csv", "votos.csv") == 0

    def test_run_gastos_wrapper(self, monkeypatch):
        monkeypatch.setattr(run_etl, "run_gastos_etl", lambda _csv: 0)
        assert run_etl.run_gastos_etl_with_retry("gastos.csv") == 0


class TestMain:
    """Cobertura do fluxo principal do orquestrador ETL."""

    def test_main_falha_quando_data_dir_nao_existe(self, monkeypatch):
        monkeypatch.setattr(run_etl.Path, "exists", lambda _self: False, raising=False)
        assert run_etl.main() == 1

    def test_main_fluxo_completo_sucesso(self, monkeypatch):
        monkeypatch.setattr(run_etl.Path, "exists", lambda _self: True, raising=False)
        monkeypatch.setattr(run_etl, "run_deputados_etl_with_retry", lambda _csv: 0)
        monkeypatch.setattr(run_etl, "run_proposicoes_etl_with_retry", lambda _csv: 0)
        monkeypatch.setattr(run_etl, "run_votacoes_etl_with_retry", lambda _v, _vv: 0)
        monkeypatch.setattr(run_etl, "run_gastos_etl_with_retry", lambda _csv: 0)
        monkeypatch.setattr(run_etl, "run_votacoes_proposicoes_etl", lambda _csv: None)
        monkeypatch.setattr(run_etl, "run_orientacoes_etl", lambda _csv: None)
        monkeypatch.setattr(run_etl, "run_classificacao_etl", lambda: None)
        assert run_etl.main() == 0

    def test_main_falha_se_deputados_falhar(self, monkeypatch):
        monkeypatch.setattr(run_etl.Path, "exists", lambda _self: True, raising=False)
        monkeypatch.setattr(run_etl, "run_deputados_etl_with_retry", lambda _csv: 1)
        assert run_etl.main() == 1

    def test_main_falha_se_proposicoes_falhar(self, monkeypatch):
        monkeypatch.setattr(run_etl.Path, "exists", lambda _self: True, raising=False)
        monkeypatch.setattr(run_etl, "run_deputados_etl_with_retry", lambda _csv: 0)
        monkeypatch.setattr(run_etl, "run_proposicoes_etl_with_retry", lambda _csv: 1)
        assert run_etl.main() == 1

    def test_main_falha_se_votacoes_falhar(self, monkeypatch):
        monkeypatch.setattr(run_etl.Path, "exists", lambda _self: True, raising=False)
        monkeypatch.setattr(run_etl, "run_deputados_etl_with_retry", lambda _csv: 0)
        monkeypatch.setattr(run_etl, "run_proposicoes_etl_with_retry", lambda _csv: 0)
        monkeypatch.setattr(run_etl, "run_votacoes_etl_with_retry", lambda _v, _vv: 1)
        assert run_etl.main() == 1

    def test_main_falha_se_gastos_falhar(self, monkeypatch):
        monkeypatch.setattr(run_etl.Path, "exists", lambda _self: True, raising=False)
        monkeypatch.setattr(run_etl, "run_deputados_etl_with_retry", lambda _csv: 0)
        monkeypatch.setattr(run_etl, "run_proposicoes_etl_with_retry", lambda _csv: 0)
        monkeypatch.setattr(run_etl, "run_votacoes_etl_with_retry", lambda _v, _vv: 0)
        monkeypatch.setattr(run_etl, "run_gastos_etl_with_retry", lambda _csv: 1)
        assert run_etl.main() == 1

    def test_main_falha_se_votacoes_proposicoes_lancar_excecao(self, monkeypatch):
        monkeypatch.setattr(run_etl.Path, "exists", lambda _self: True, raising=False)
        monkeypatch.setattr(run_etl, "run_deputados_etl_with_retry", lambda _csv: 0)
        monkeypatch.setattr(run_etl, "run_proposicoes_etl_with_retry", lambda _csv: 0)
        monkeypatch.setattr(run_etl, "run_votacoes_etl_with_retry", lambda _v, _vv: 0)
        monkeypatch.setattr(run_etl, "run_gastos_etl_with_retry", lambda _csv: 0)
        monkeypatch.setattr(
            run_etl,
            "run_votacoes_proposicoes_etl",
            lambda _csv: (_ for _ in ()).throw(RuntimeError("falha crítica")),
        )
        assert run_etl.main() == 1

    def test_main_continua_com_orientacoes_nao_critico(self, monkeypatch):
        monkeypatch.setattr(run_etl.Path, "exists", lambda _self: True, raising=False)
        monkeypatch.setattr(run_etl, "run_deputados_etl_with_retry", lambda _csv: 0)
        monkeypatch.setattr(run_etl, "run_proposicoes_etl_with_retry", lambda _csv: 0)
        monkeypatch.setattr(run_etl, "run_votacoes_etl_with_retry", lambda _v, _vv: 0)
        monkeypatch.setattr(run_etl, "run_gastos_etl_with_retry", lambda _csv: 0)
        monkeypatch.setattr(run_etl, "run_votacoes_proposicoes_etl", lambda _csv: None)
        monkeypatch.setattr(
            run_etl,
            "run_orientacoes_etl",
            lambda _csv: (_ for _ in ()).throw(RuntimeError("orientações indisponíveis")),
        )
        monkeypatch.setattr(run_etl, "run_classificacao_etl", lambda: None)
        assert run_etl.main() == 0

    def test_main_continua_com_classificacao_nao_critico(self, monkeypatch):
        monkeypatch.setattr(run_etl.Path, "exists", lambda _self: True, raising=False)
        monkeypatch.setattr(run_etl, "run_deputados_etl_with_retry", lambda _csv: 0)
        monkeypatch.setattr(run_etl, "run_proposicoes_etl_with_retry", lambda _csv: 0)
        monkeypatch.setattr(run_etl, "run_votacoes_etl_with_retry", lambda _v, _vv: 0)
        monkeypatch.setattr(run_etl, "run_gastos_etl_with_retry", lambda _csv: 0)
        monkeypatch.setattr(run_etl, "run_votacoes_proposicoes_etl", lambda _csv: None)
        monkeypatch.setattr(run_etl, "run_orientacoes_etl", lambda _csv: None)
        monkeypatch.setattr(
            run_etl,
            "run_classificacao_etl",
            lambda: (_ for _ in ()).throw(RuntimeError("classificação indisponível")),
        )
        assert run_etl.main() == 0


class TestSetupLogging:
    """Cobertura para setup de logging."""

    def test_setup_logging_adiciona_handlers(self, tmp_path):
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        run_etl.setup_logging(log_dir=tmp_path)

        assert root_logger.level == logging.INFO
        assert len(root_logger.handlers) >= 2
