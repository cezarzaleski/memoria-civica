"""Testes de contrato para integração de gastos no downloader e orquestrador ETL."""

from __future__ import annotations

from pathlib import Path

import scripts.download_camara as download_camara
import scripts.run_full_etl as run_full_etl


def _touch_csv(path: Path) -> None:
    """Cria arquivo CSV simples para simular presença de input."""
    path.write_text("coluna\nvalor\n", encoding="utf-8")


class TestDownloadGastosContract:
    """Valida contrato de gastos no script de download."""

    def test_file_configs_inclui_gastos_com_fonte_ceap(self):
        """`FILE_CONFIGS` deve expor `gastos` com URL CEAP anual."""
        assert "gastos" in download_camara.FILE_CONFIGS

        config = download_camara.FILE_CONFIGS["gastos"]
        assert config["base_url"] == "https://www.camara.leg.br"
        assert config["url_path"] == "cotas/Ano-{ano}.csv.zip"
        assert config["filename"] == "gastos-{ano}.csv"
        assert config["source_format"] == "zip"
        assert config["zip_inner_file"] == "Ano-{ano}.csv"
        assert config["requires_ano"] is True
        assert config["requires_legislatura"] is False

    def test_download_order_inclui_gastos_sem_quebrar_dependencias(self):
        """Ordem deve incluir gastos e preservar precedência de deputados."""
        order = download_camara.DOWNLOAD_ORDER

        assert "gastos" in order
        assert order.index("deputados") < order.index("gastos")
        assert order.index("proposicoes") < order.index("votacoes") < order.index("votos")

    def test_parse_args_aceita_file_gastos(self):
        """CLI deve aceitar seleção explícita de `--file gastos`."""
        parsed = download_camara.parse_args(["--file", "gastos"])
        assert parsed.files == ["gastos"]

    def test_download_all_files_reordena_selecao_com_gastos(self, monkeypatch, tmp_path):
        """Seleção múltipla deve respeitar `DOWNLOAD_ORDER` quando inclui gastos."""
        called_files: list[str] = []

        def _fake_download_single_file(file_key: str, *_args, **_kwargs) -> bool:
            called_files.append(file_key)
            return True

        monkeypatch.setattr(download_camara, "download_single_file", _fake_download_single_file)

        requested = ["votacoes", "gastos", "deputados"]
        download_camara.download_all_files(tmp_path, files=requested, dry_run=True)

        expected_order = [file_key for file_key in download_camara.DOWNLOAD_ORDER if file_key in requested]
        assert called_files == expected_order


class TestRunFullEtlComGastos:
    """Valida a etapa de gastos no orquestrador full ETL."""

    def test_run_etl_executa_gastos_no_fluxo_base(self, monkeypatch, tmp_path):
        """Pipeline deve executar gastos entre ingestão base e fase relacional."""
        ano = run_full_etl.settings.CAMARA_ANO
        required_files = [
            "deputados.csv",
            f"proposicoes-{ano}.csv",
            f"votacoes-{ano}.csv",
            f"votacoesVotos-{ano}.csv",
            f"gastos-{ano}.csv",
            f"votacoesProposicoes-{ano}.csv",
            f"votacoesOrientacoes-{ano}.csv",
        ]

        for file_name in required_files:
            _touch_csv(tmp_path / file_name)

        call_order: list[str] = []

        monkeypatch.setattr(
            run_full_etl,
            "run_deputados_etl_with_retry",
            lambda *_args, **_kwargs: call_order.append("deputados") or 0,
        )
        monkeypatch.setattr(
            run_full_etl,
            "run_proposicoes_etl_with_retry",
            lambda *_args, **_kwargs: call_order.append("proposicoes") or 0,
        )
        monkeypatch.setattr(
            run_full_etl,
            "run_votacoes_etl_with_retry",
            lambda *_args, **_kwargs: call_order.append("votacoes") or 0,
        )
        monkeypatch.setattr(
            run_full_etl,
            "run_gastos_etl_with_retry",
            lambda *_args, **_kwargs: call_order.append("gastos") or 0,
        )
        monkeypatch.setattr(
            run_full_etl,
            "run_votacoes_proposicoes_etl",
            lambda *_args, **_kwargs: call_order.append("votacoes_proposicoes") or None,
        )
        monkeypatch.setattr(
            run_full_etl,
            "run_orientacoes_etl",
            lambda *_args, **_kwargs: call_order.append("orientacoes") or None,
        )
        monkeypatch.setattr(
            run_full_etl,
            "run_classificacao_etl",
            lambda *_args, **_kwargs: call_order.append("classificacao") or None,
        )

        exit_code = run_full_etl.run_etl(tmp_path)

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

    def test_run_etl_falha_quando_step_gastos_retorna_erro(self, monkeypatch, tmp_path):
        """Falha na etapa de gastos deve abortar pipeline com exit code 1."""
        ano = run_full_etl.settings.CAMARA_ANO
        required_files = [
            "deputados.csv",
            f"proposicoes-{ano}.csv",
            f"votacoes-{ano}.csv",
            f"votacoesVotos-{ano}.csv",
            f"gastos-{ano}.csv",
        ]

        for file_name in required_files:
            _touch_csv(tmp_path / file_name)

        call_order: list[str] = []

        monkeypatch.setattr(
            run_full_etl,
            "run_deputados_etl_with_retry",
            lambda *_args, **_kwargs: call_order.append("deputados") or 0,
        )
        monkeypatch.setattr(
            run_full_etl,
            "run_proposicoes_etl_with_retry",
            lambda *_args, **_kwargs: call_order.append("proposicoes") or 0,
        )
        monkeypatch.setattr(
            run_full_etl,
            "run_votacoes_etl_with_retry",
            lambda *_args, **_kwargs: call_order.append("votacoes") or 0,
        )
        monkeypatch.setattr(
            run_full_etl,
            "run_gastos_etl_with_retry",
            lambda *_args, **_kwargs: call_order.append("gastos") or 1,
        )
        monkeypatch.setattr(
            run_full_etl,
            "run_votacoes_proposicoes_etl",
            lambda *_args, **_kwargs: call_order.append("votacoes_proposicoes") or None,
        )

        exit_code = run_full_etl.run_etl(tmp_path)

        assert exit_code == 1
        assert call_order == ["deputados", "proposicoes", "votacoes", "gastos"]
