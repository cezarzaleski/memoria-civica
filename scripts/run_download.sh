#!/bin/bash
# scripts/run_download.sh - Script wrapper para agendamento via cron
#
# Este script facilita o agendamento do download de dados da Camara
# dos Deputados via cron, gerenciando variaveis de ambiente e logs.
#
# Uso:
#   ./scripts/run_download.sh                    # Executa download padrao
#   ./scripts/run_download.sh --data-dir /path   # Passa argumentos ao script
#
# Agendamento cron:
#   0 3 * * * /caminho/projeto/scripts/run_download.sh
#
# Variaveis de ambiente (opcional):
#   MEMORIA_CIVICA_HOME  - Diretorio do projeto (padrao: diretorio do script)
#   MEMORIA_CIVICA_LOG   - Diretorio de logs (padrao: /var/log/memoria_civica)
#

set -e

# Determinar diretorio do projeto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="${MEMORIA_CIVICA_HOME:-$(dirname "$SCRIPT_DIR")}"

# Configurar diretorio de logs
LOG_DIR="${MEMORIA_CIVICA_LOG:-/var/log/memoria_civica}"
LOG_FILE="$LOG_DIR/download_$(date +%Y%m%d).log"

# Criar diretorio de logs se nao existir
if [ ! -d "$LOG_DIR" ]; then
    mkdir -p "$LOG_DIR" 2>/dev/null || {
        # Se nao conseguir criar em /var/log, usar diretorio local
        LOG_DIR="$PROJECT_DIR/logs"
        LOG_FILE="$LOG_DIR/download_$(date +%Y%m%d).log"
        mkdir -p "$LOG_DIR"
    }
fi

# Mudar para diretorio do projeto
cd "$PROJECT_DIR" || {
    echo "ERRO: Nao foi possivel acessar o diretorio do projeto: $PROJECT_DIR" >&2
    exit 1
}

# Carregar variaveis de ambiente do arquivo .env se existir
if [ -f .env ]; then
    # Exportar variaveis ignorando linhas de comentario
    set -a
    # shellcheck source=/dev/null
    source <(grep -v '^#' .env | grep -v '^$')
    set +a
fi

# Funcao para logging
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Registrar inicio
log_message "=== INICIO DO DOWNLOAD ==="
log_message "Diretorio do projeto: $PROJECT_DIR"
log_message "Arquivo de log: $LOG_FILE"
log_message "Argumentos: $*"

# Verificar se poetry esta disponivel
if command -v poetry &> /dev/null; then
    PYTHON_CMD="poetry run python"
elif [ -f "$PROJECT_DIR/.venv/bin/python" ]; then
    PYTHON_CMD="$PROJECT_DIR/.venv/bin/python"
elif [ -f "$PROJECT_DIR/venv/bin/python" ]; then
    PYTHON_CMD="$PROJECT_DIR/venv/bin/python"
else
    PYTHON_CMD="python3"
fi

log_message "Comando Python: $PYTHON_CMD"

# Argumentos padrao se nenhum for fornecido
if [ $# -eq 0 ]; then
    ARGS="--data-dir ./data/dados_camara"
else
    ARGS="$*"
fi

# Executar download
log_message "Executando: $PYTHON_CMD scripts/download_camara.py $ARGS"
$PYTHON_CMD scripts/download_camara.py $ARGS >> "$LOG_FILE" 2>&1
EXIT_CODE=$?

# Registrar resultado
if [ $EXIT_CODE -eq 0 ]; then
    log_message "=== DOWNLOAD CONCLUIDO COM SUCESSO (exit code: $EXIT_CODE) ==="
else
    log_message "=== DOWNLOAD FALHOU (exit code: $EXIT_CODE) ==="
fi

exit $EXIT_CODE
