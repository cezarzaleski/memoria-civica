FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema (para psycopg2)
RUN apt-get update && apt-get install -y \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Instalar Poetry
RUN pip install --no-cache-dir poetry

# Copiar arquivos de dependência
COPY pyproject.toml poetry.lock* ./

# Instalar dependências Python (sem dev dependencies, sem instalar o projeto)
RUN poetry config virtualenvs.create false && \
    poetry install --only main --no-interaction --no-ansi --no-root

# Copiar código fonte
COPY src/ ./src/
COPY scripts/ ./scripts/

# Variáveis de ambiente padrão
ENV PYTHONUNBUFFERED=1
ENV TEMP_DOWNLOAD_DIR=/tmp/camara_downloads

# Entrypoint: executa pipeline completo (download + ETL)
CMD ["python", "scripts/run_full_etl.py"]
