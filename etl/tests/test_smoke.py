"""Testes de smoke para validar a estrutura do projeto."""

import sys
from pathlib import Path


def test_python_version():
    """Verifica se a versão do Python é 3.11 ou superior."""
    assert sys.version_info >= (3, 11), f"Python 3.11+ é obrigatório, versão atual: {sys.version}"


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
        import src.gastos
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
