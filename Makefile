.PHONY: test lint format check clean install

# Instalar dependências
install:
	@echo "Instalando dependências..."
	poetry install

# Executar testes com cobertura (excluindo testes de integração)
test:
	@echo "Executando testes..."
	poetry run pytest -v --cov=src --cov-report=term-missing --cov-report=html -m "not integration"

# Executar linting
lint:
	@echo "Executando linting com Ruff..."
	poetry run ruff check .

# Executar formatação de código
format:
	@echo "Formatando código com Ruff..."
	poetry run ruff format .

# Executar linting e formatação
check: lint
	@echo "Verificação de código completa."

# Limpar arquivos temporários
clean:
	@echo "Limpando arquivos temporários..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name ".coverage" -delete 2>/dev/null || true
	@echo "Limpeza concluída."

# Help
help:
	@echo "Comandos disponíveis:"
	@echo "  make install  - Instalar dependências com Poetry"
	@echo "  make test     - Executar testes com cobertura"
	@echo "  make lint     - Executar linting com Ruff"
	@echo "  make format   - Formatar código com Ruff"
	@echo "  make check    - Executar linting e formatação"
	@echo "  make clean    - Limpar arquivos temporários"
