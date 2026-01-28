"""Testes de smoke para validar a estrutura do projeto."""

import sys
from pathlib import Path


def test_python_version():
    """Verifica se a versão do Python é 3.11 ou superior."""
    assert sys.version_info >= (3, 11), f"Python 3.11+ é obrigatório, versão atual: {sys.version}"


def test_project_structure():
    """Verifica se todos os diretórios necessários existem."""
    etl_root = Path(__file__).parent.parent
    project_root = etl_root.parent

    # Diretórios em etl/
    required_dirs_etl = [
        "src",
        "src/deputados",
        "src/votacoes",
        "src/proposicoes",
        "src/shared",
        "scripts",
        "tests",
        "tests/fixtures",
        "tests/test_deputados",
        "tests/test_votacoes",
        "tests/test_proposicoes",
    ]

    for dir_path in required_dirs_etl:
        full_path = etl_root / dir_path
        assert full_path.exists(), f"Diretório obrigatório não encontrado: {dir_path}"
        assert full_path.is_dir(), f"Caminho existe mas não é um diretório: {dir_path}"

    # Diretórios na raiz do projeto
    required_dirs_root = [
        "data",
        "data/dados_camara",
        "alembic",
        "alembic/versions",
    ]

    for dir_path in required_dirs_root:
        full_path = project_root / dir_path
        assert full_path.exists(), f"Diretório obrigatório não encontrado: {dir_path}"
        assert full_path.is_dir(), f"Caminho existe mas não é um diretório: {dir_path}"


def test_config_files_exist():
    """Verifica se arquivos de configuração essenciais existem."""
    etl_root = Path(__file__).parent.parent
    project_root = etl_root.parent

    # Arquivos em etl/
    required_files_etl = [
        "pyproject.toml",
    ]

    for file_path in required_files_etl:
        full_path = etl_root / file_path
        assert full_path.exists(), f"Arquivo de configuração não encontrado: {file_path}"
        assert full_path.is_file(), f"Caminho existe mas não é um arquivo: {file_path}"

    # Arquivos na raiz do projeto
    required_files_root = [
        "pytest.ini",
        ".gitignore",
        "README.md",
    ]

    for file_path in required_files_root:
        full_path = project_root / file_path
        assert full_path.exists(), f"Arquivo de configuração não encontrado: {file_path}"
        assert full_path.is_file(), f"Caminho existe mas não é um arquivo: {file_path}"


def test_basic_imports():
    """Verifica se imports básicos funcionam."""
    try:
        import src
        import src.deputados
        import src.proposicoes
        import src.shared
        import src.votacoes  # noqa: F401
    except ImportError as e:
        raise AssertionError(f"Falha ao importar módulos básicos: {e}") from e


def test_dependencies_installed():
    """Verifica se dependências críticas estão instaladas."""
    dependencies = [
        "sqlalchemy",
        "alembic",
        "pydantic",
        "pydantic_settings",
        "pandas",
        "pytest",
    ]

    for dep in dependencies:
        try:
            __import__(dep)
        except ImportError as e:
            raise AssertionError(f"Dependência crítica não instalada: {dep}") from e


def test_data_directory_has_csv_files():
    """Verifica se o diretório de dados contém arquivos CSV."""
    etl_root = Path(__file__).parent.parent
    project_root = etl_root.parent
    data_dir = project_root / "data" / "dados_camara"

    csv_files = list(data_dir.glob("*.csv"))
    assert len(csv_files) > 0, "Nenhum arquivo CSV encontrado em data/dados_camara/"

    # Verifica arquivos CSV esperados
    expected_csvs = ["deputados.csv", "votacoes.csv", "proposicoes.csv", "votos.csv"]
    found_csvs = [f.name for f in csv_files]

    for expected in expected_csvs:
        assert expected in found_csvs, f"Arquivo CSV esperado não encontrado: {expected}"
