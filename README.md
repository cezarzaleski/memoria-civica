# Memória Cívica - Fundação de Dados

> "Democracia não é só votar. É lembrar, cobrar e participar."

## Visão Geral

Este projeto estabelece a **fundação de dados** do Memória Cívica, uma ferramenta que dá ao cidadão brasileiro o poder de lembrar o que seus deputados votaram, entender o significado de cada votação, e tomar decisões informadas nas eleições.

Esta fase inicial (Setup Inicial) valida a viabilidade de coletar e estruturar dados de votações da Câmara dos Deputados de 2025, estabelecendo a base para o MVP futuro.

## Estrutura do Projeto

O projeto está organizado em dois componentes principais:

### **frontend/** - PWA de Frontend (Next.js 15)

Interface mobile-first para visualizar votações e acompanhar deputados. Stack: React 19, Tailwind CSS, Shadcn/UI, MSW (mocks), next-pwa (PWA capabilities).

**Iniciar desenvolvimento:**
```bash
cd frontend
npm install
npm run dev  # http://localhost:3000
```

**Testes e qualidade:**
```bash
npm run test       # Vitest + React Testing Library
npm run lint       # ESLint
npm run format     # Prettier
```

Veja [frontend/README.md](frontend/README.md) para documentação completa.

### **etl/** - Pipeline ETL (Python)

Coleta, validação e estruturação de dados da Câmara dos Deputados. O código Python original foi reorganizado de `src/` para `etl/src/` para separar concerns entre frontend e backend.

**Estrutura ETL:**
```
etl/
├── src/               # Código Python (deputados, proposicoes, votacoes, shared)
├── scripts/           # Scripts de orquestração (init_db.py, run_etl.py)
├── tests/             # Testes (unitários, integração)
└── pyproject.toml     # Dependências Python
```

**Iniciar ETL:**
```bash
PYTHONPATH=. python etl/scripts/init_db.py  # Inicializar banco
PYTHONPATH=. python etl/scripts/run_etl.py  # Executar pipeline
```

**Testes:**
```bash
pytest etl/tests/  # Ou `make test` (roda de raiz)
```

### **Arquivo de configuração raiz**

- `pyproject.toml` (Python): Configuração de dependências e linting
- `Makefile`: Comandos convenientes (make test, make lint, etc)
- `pytest.ini`: Configuração de testes (aponta para etl/tests/)
- `alembic/`: Migrations de banco (mantém na raiz para acesso fácil)

## Pré-requisitos

- Python 3.11+
- Poetry (gerenciador de dependências)
- SQLite 3.35+

## Setup

1. **Instalar dependências:**
   ```bash
   poetry install
   ```

2. **Ativar ambiente virtual:**
   ```bash
   poetry shell
   ```

3. **Inicializar banco de dados:**
   ```bash
   PYTHONPATH=. python scripts/init_db.py
   ```

## Execução

- **ETL completo:**
  ```bash
  PYTHONPATH=. python scripts/run_etl.py
  ```

- **Executar testes:**
  ```bash
  pytest
  ```

- **Coverage:**
  ```bash
  pytest --cov=src --cov-report=html
  ```

## Download Automatizado de Dados

O projeto inclui um script para download automatizado de arquivos CSV da API Dados Abertos da Câmara dos Deputados. Este script pode ser executado manualmente ou agendado via cron para execução periódica.

### Uso do Script

O script `scripts/download_camara.py` baixa os seguintes arquivos:
- `deputados.csv`: Lista de todos os deputados federais
- `gastos-{ano}.csv`: Gastos parlamentares CEAP do ano (ex: gastos-2025.csv)
- `proposicoes-{ano}.csv`: Proposições do ano (ex: proposicoes-2025.csv)
- `votacoes-{legislatura}.csv`: Votações da legislatura
- `votacoesVotos-{legislatura}.csv`: Votos individuais

#### Argumentos CLI

```bash
PYTHONPATH=. python scripts/download_camara.py --help
```

| Argumento | Descrição | Padrão |
|-----------|-----------|--------|
| `--data-dir PATH` | Diretório de destino para os arquivos | `/tmp/camara_downloads` |
| `--file ARQUIVO` | Arquivo específico para baixar (pode ser repetido) | Todos |
| `--dry-run` | Simula downloads sem executar | Desabilitado |
| `-v, --verbose` | Habilita logging detalhado (DEBUG) | Desabilitado |

Arquivos válidos para `--file`: `deputados`, `gastos`, `proposicoes`, `votacoes`, `votos`, `votacoes_proposicoes`, `votacoes_orientacoes`

#### Exemplos de Uso

**Importante**: Execute os scripts a partir da raiz do projeto com `PYTHONPATH=.` para que os módulos sejam encontrados:

```bash
# Baixar todos os arquivos para diretório padrão
PYTHONPATH=. python scripts/download_camara.py

# Especificar diretório de destino
PYTHONPATH=. python scripts/download_camara.py --data-dir ./data/dados_camara

# Baixar apenas arquivo de deputados
PYTHONPATH=. python scripts/download_camara.py --file deputados

# Baixar múltiplos arquivos específicos
PYTHONPATH=. python scripts/download_camara.py --file votacoes --file votos

# Simular download (verifica URLs sem baixar)
PYTHONPATH=. python scripts/download_camara.py --dry-run

# Executar com logging detalhado
PYTHONPATH=. python scripts/download_camara.py --verbose
```

#### Códigos de Saída

| Código | Significado |
|--------|-------------|
| `0` | Sucesso - todos os downloads concluídos |
| `1` | Falha - pelo menos um download falhou |

### Variáveis de Ambiente

Configure as seguintes variáveis no arquivo `.env` ou no ambiente:

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `CAMARA_API_BASE_URL` | URL base da API Dados Abertos | `https://dadosabertos.camara.leg.br/arquivos` |
| `CAMARA_LEGISLATURA` | Número da legislatura (57 = 2023-2027) | `57` |
| `CAMARA_ANO` | Ano para download de proposições | `2025` |
| `TEMP_DOWNLOAD_DIR` | Diretório temporário para downloads | `/tmp/camara_downloads` |
| `WEBHOOK_URL` | URL do webhook para notificações de erro (opcional) | Vazio (desabilitado) |

#### Configuração do Webhook

Quando configurado, o script envia notificações HTTP POST para a URL especificada quando ocorrem erros. O payload JSON tem a seguinte estrutura:

```json
{
  "etapa": "download_deputados",
  "mensagem": "descrição do erro",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

Exemplos de URLs de webhook:
- Slack: `https://hooks.slack.com/services/T00000000/B00000000/XXXXXXX`
- Discord: `https://discord.com/api/webhooks/000000000000000000/XXXXXXX`
- Microsoft Teams: `https://outlook.office.com/webhook/...`
- Endpoint customizado: `https://api.example.com/webhooks/alerts`

### Agendamento via Cron

Para automatizar a coleta de dados, configure um job cron para executar o script periodicamente.

#### Configuração Básica

1. **Abra o crontab para edição:**
   ```bash
   crontab -e
   ```

2. **Adicione uma linha para agendar a execução:**
   ```bash
   # Download diário às 3h da manhã
   0 3 * * * cd /caminho/para/projeto && /caminho/para/venv/bin/python scripts/download_camara.py --data-dir ./data/dados_camara >> /var/log/camara_download.log 2>&1
   ```

#### Exemplos de Agendamento

```bash
# Diário às 3h da manhã
0 3 * * * cd /home/user/memoria_civica && poetry run python scripts/download_camara.py --data-dir ./data/dados_camara

# Semanal aos domingos às 2h
0 2 * * 0 cd /home/user/memoria_civica && poetry run python scripts/download_camara.py --data-dir ./data/dados_camara

# A cada 6 horas
0 */6 * * * cd /home/user/memoria_civica && poetry run python scripts/download_camara.py --data-dir ./data/dados_camara

# Dias úteis (segunda a sexta) às 4h
0 4 * * 1-5 cd /home/user/memoria_civica && poetry run python scripts/download_camara.py --data-dir ./data/dados_camara
```

#### Cron com Variáveis de Ambiente

Para incluir variáveis de ambiente customizadas:

```bash
# Opção 1: Definir variáveis inline
0 3 * * * WEBHOOK_URL="https://hooks.slack.com/..." cd /home/user/memoria_civica && poetry run python scripts/download_camara.py

# Opção 2: Carregar arquivo .env
0 3 * * * cd /home/user/memoria_civica && source .env && poetry run python scripts/download_camara.py

# Opção 3: Usar script wrapper
0 3 * * * /home/user/memoria_civica/scripts/run_download.sh
```

#### Script Wrapper (Recomendado)

Crie um script wrapper `scripts/run_download.sh` para facilitar o agendamento:

```bash
#!/bin/bash
# scripts/run_download.sh - Script wrapper para agendamento via cron

# Configurações
PROJECT_DIR="/home/user/memoria_civica"
LOG_DIR="/var/log/memoria_civica"
LOG_FILE="$LOG_DIR/download_$(date +%Y%m%d).log"

# Criar diretório de logs se não existir
mkdir -p "$LOG_DIR"

# Mudar para diretório do projeto
cd "$PROJECT_DIR" || exit 1

# Carregar variáveis de ambiente
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Executar download com logging
echo "=== Início: $(date) ===" >> "$LOG_FILE"
poetry run python scripts/download_camara.py --data-dir ./data/dados_camara >> "$LOG_FILE" 2>&1
EXIT_CODE=$?
echo "=== Fim: $(date) - Exit code: $EXIT_CODE ===" >> "$LOG_FILE"

exit $EXIT_CODE
```

Torne executável e agende:

```bash
chmod +x scripts/run_download.sh

# Adicionar ao crontab
0 3 * * * /home/user/memoria_civica/scripts/run_download.sh
```

### Integração com Pipeline ETL

O download de dados é a primeira etapa do pipeline completo. Após o download, execute o ETL para processar os dados:

```bash
# 1. Download dos CSVs
PYTHONPATH=. python scripts/download_camara.py --data-dir ./data/dados_camara

# 2. Inicializar banco (se necessário)
PYTHONPATH=. python scripts/init_db.py

# 3. Executar ETL
PYTHONPATH=. python scripts/run_etl.py
```

#### Pipeline Completo via Cron

```bash
# Execução completa diária às 3h
0 3 * * * cd /home/user/memoria_civica && poetry run python scripts/download_camara.py --data-dir ./data/dados_camara && poetry run python scripts/run_etl.py >> /var/log/memoria_civica_etl.log 2>&1
```

### Logs e Histórico de Execução

O script utiliza o módulo `logging` do Python com formato padronizado:

```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

#### Níveis de Log

| Nível | Uso |
|-------|-----|
| `INFO` | Operações normais, progresso de download |
| `WARNING` | Arquivos pulados (cache hit via ETag) |
| `ERROR` | Falhas de download, erros de rede |
| `DEBUG` | Detalhes técnicos (habilitar com `-v`) |

#### Saída de Exemplo

```
2024-01-15 03:00:01 - __main__ - INFO - ============================================================
2024-01-15 03:00:01 - __main__ - INFO - Iniciando download de 4 arquivo(s) da Câmara dos Deputados
2024-01-15 03:00:01 - __main__ - INFO - Legislatura: 57
2024-01-15 03:00:01 - __main__ - INFO - ============================================================
2024-01-15 03:00:01 - __main__ - INFO - [1/4] DEPUTADOS
2024-01-15 03:00:02 - __main__ - INFO -   Download concluído: deputados.csv (tamanho: 256.00 KB, tempo: 1.23s)
2024-01-15 03:00:02 - __main__ - INFO - [2/4] PROPOSICOES
2024-01-15 03:00:03 - __main__ - WARNING -   Arquivo não alterado, pulando: proposicoes-2025.csv (tempo: 0.45s)
...
2024-01-15 03:00:10 - __main__ - INFO - ============================================================
2024-01-15 03:00:10 - __main__ - INFO - SUMÁRIO DE DOWNLOADS
2024-01-15 03:00:10 - __main__ - INFO - ============================================================
2024-01-15 03:00:10 - __main__ - INFO - Estatísticas de arquivos:
2024-01-15 03:00:10 - __main__ - INFO -   Total processado: 4 arquivo(s)
2024-01-15 03:00:10 - __main__ - INFO -   Baixados: 2
2024-01-15 03:00:10 - __main__ - INFO -   Pulados (cache): 2
2024-01-15 03:00:10 - __main__ - INFO -   Falhas: 0
2024-01-15 03:00:10 - __main__ - INFO - ✓ Download concluído com sucesso!
```

#### Redirecionando Logs para Arquivo

```bash
# Redirecionar stdout e stderr para arquivo
PYTHONPATH=. python scripts/download_camara.py >> /var/log/camara_download.log 2>&1

# Logs rotativos por data
PYTHONPATH=. python scripts/download_camara.py >> /var/log/camara_download_$(date +%Y%m%d).log 2>&1
```

### Troubleshooting de Downloads

#### Erro: ModuleNotFoundError: No module named 'src'

**Problema**: Ao executar scripts, você vê erro "ModuleNotFoundError: No module named 'src'"

**Causa**: O Python não encontra o módulo `src` porque o diretório raiz do projeto não está no `PYTHONPATH`.

**Solução**: Execute os scripts com `PYTHONPATH=.` na frente:
```bash
PYTHONPATH=. python scripts/download_camara.py --help
```

Ou exporte a variável para a sessão toda:
```bash
export PYTHONPATH=/caminho/para/memoria_civica
python scripts/download_camara.py --help
```

#### Erro: Falha de conexão / Timeout

**Problema**: Download falha com erro de rede ou timeout.

**Causa**: Instabilidade de rede ou API temporariamente indisponível.

**Solução**:
1. O script já implementa retry automático com backoff exponencial (3 tentativas: 2s, 4s, 8s)
2. Verifique conectividade: `curl -I https://dadosabertos.camara.leg.br/arquivos/deputados/csv/deputados.csv`
3. Se persistir, aguarde e tente novamente mais tarde

#### Erro: HTTP 404 Not Found

**Problema**: Arquivo não encontrado na API.

**Causa**: Legislatura inválida ou arquivo temporariamente indisponível.

**Solução**:
1. Verifique `CAMARA_LEGISLATURA` no `.env` (atual: 57 para 2023-2027)
2. Consulte legislaturas válidas: 55 (2015-2019), 56 (2019-2023), 57 (2023-2027)

#### Erro: HTTP 429 Too Many Requests

**Problema**: Rate limit excedido na API.

**Causa**: Muitas requisições em curto período.

**Solução**:
1. Aguarde alguns minutos antes de tentar novamente
2. Se usando cron, evite agendar execuções frequentes (mínimo recomendado: 1x por dia)

#### Erro: Permission denied ao salvar arquivo

**Problema**: Sem permissão para escrever no diretório de destino.

**Solução**:
1. Verifique permissões: `ls -la /tmp/camara_downloads`
2. Crie diretório manualmente: `mkdir -p /tmp/camara_downloads && chmod 755 /tmp/camara_downloads`
3. Use diretório alternativo: `--data-dir ~/camara_data`

#### Erro: Webhook não envia notificações

**Problema**: Erros ocorrem mas webhooks não são recebidos.

**Solução**:
1. Verifique se `WEBHOOK_URL` está configurada corretamente
2. Teste o webhook manualmente:
   ```bash
   curl -X POST -H "Content-Type: application/json" \
     -d '{"etapa":"teste","mensagem":"teste","timestamp":"2024-01-15T10:00:00Z"}' \
     "$WEBHOOK_URL"
   ```
3. Webhooks são fire-and-forget: falhas de envio não interrompem o download

#### Cache (ETag) não funciona

**Problema**: Arquivos são sempre baixados novamente, mesmo sem alteração.

**Causa**: O servidor pode não suportar ETag ou arquivo foi modificado.

**Comportamento esperado**:
- Se o arquivo não mudou (mesmo ETag), o download é pulado
- Arquivos pulados aparecem como `WARNING` no log
- Isso é uma otimização, não um erro

## Arquitetura

Estrutura feature-based organizada por domínio, com separação clara entre frontend (Next.js) e backend (Python ETL):

```
memoria_civica/
├── frontend/                  # PWA com Next.js 15
│   ├── app/                   # Rotas e páginas (App Router)
│   ├── components/            # Componentes React (ui/ + features/)
│   ├── lib/                   # Hooks, types, utils
│   ├── mocks/                 # MSW (Mock Service Worker)
│   ├── __tests__/             # Testes frontend
│   ├── next.config.mjs        # Config Next.js + PWA
│   ├── package.json           # Dependências Node
│   └── README.md              # Docs frontend
│
├── etl/                       # Pipeline Python (reorganizado de src/)
│   ├── src/
│   │   ├── deputados/         # Domínio de Deputados
│   │   ├── proposicoes/       # Domínio de Proposições
│   │   ├── votacoes/          # Domínio de Votações
│   │   └── shared/            # Config, database, utils
│   ├── scripts/               # ETL orchestration (init_db.py, run_etl.py)
│   ├── tests/                 # Testes Python
│   └── pyproject.toml         # Dependências Python
│
├── alembic/                   # Database migrations (na raiz para fácil acesso)
├── data/                      # Dados CSV de entrada
├── pyproject.toml             # Config Python (pytest, ruff)
├── Makefile                   # Comandos convenientes
└── README.md                  # Esse arquivo
```

## Domínios

- **Deputados**: Informações dos 513 deputados federais (nome, partido, UF)
- **Proposições**: Projetos de lei, PECs, MPs que são votadas no Plenário
- **Votações**: Registros de votações e votos individuais de cada deputado

## Migrations

Migrations de banco de dados são gerenciadas via Alembic. Cada mudança de schema deve ter uma migration correspondente.

- **Criar migration:**
  ```bash
  alembic revision -m "descrição_da_mudança"
  ```

- **Aplicar migrations:**
  ```bash
  alembic upgrade head
  ```

- **Reverter migration:**
  ```bash
  alembic downgrade -1
  ```

- **Verificar status:**
  ```bash
  alembic current
  ```

### Quando criar uma migration

Crie uma migration sempre que:
- Adicionar uma nova tabela
- Adicionar ou remover colunas
- Modificar tipos de coluna
- Adicionar índices ou constraints
- Alterar foreign keys

**Nunca modifique migrations já aplicadas.** Crie uma nova migration para corrigir erros.

### Testing migrations

Para garantir que migrations funcionam corretamente:

```bash
# Testar upgrade
alembic upgrade head

# Testar downgrade (rollback)
alembic downgrade -1

# Testar upgrade novamente
alembic upgrade head
```

### Convenção de naming

Use o padrão: `NNN_verb_subject.py`

Exemplos:
- `001_add_deputados_table.py`
- `002_add_proposicoes_table.py`
- `003_add_votacoes_table.py`
- `004_add_votos_table.py`

## Desenvolvimento

### Padrões de código

Este projeto segue padrões rigorosos de qualidade:

- **Type hints**: Todas as funções públicas devem ter type hints
- **Docstrings**: Google style docstrings para funções e classes públicas
- **Linting**: Ruff com line length 120
- **Testes**: Mínimo 70% coverage para repositories e ETL

### Executar linting

```bash
make lint
```

Ou diretamente com Ruff:

```bash
ruff check src tests
```

### Formatar código

```bash
make format
```

### Estrutura de testes

```
tests/
├── test_smoke.py                # Testes de smoke (verificação básica)
├── test_deputados/
│   ├── conftest.py             # Fixtures específicas do domínio
│   ├── test_repository.py       # Testes do repositório
│   ├── test_etl.py             # Testes do pipeline ETL
│   └── test_schemas.py         # Testes de validação
├── test_proposicoes/
│   └── [similar structure]
├── test_votacoes/
│   └── [similar structure]
├── test_shared/
│   ├── test_config.py          # Testes de configuração
│   ├── test_database.py        # Testes de banco de dados
│   └── test_integration.py     # Testes de integração
└── test_integration/
    └── test_orchestration.py   # Testes end-to-end
```

### Rodar testes específicos

```bash
# Todos os testes
pytest

# Testes de um domínio
pytest tests/test_deputados/

# Apenas testes de integração
pytest -m integration

# Com coverage
pytest --cov=src --cov-report=html
```

## Troubleshooting

### Erro: "no such table"

**Problema**: Ao rodar ETL, você vê erro "no such table: deputados"

**Solução**: Execute o script de inicialização do banco:
```bash
PYTHONPATH=. python scripts/init_db.py
```

Este script cria todas as tabelas via Alembic migrations.

### Erro: "FOREIGN KEY constraint failed"

**Problema**: ETL falha com erro de constraint de chave estrangeira

**Possíveis causas**:
1. ETL foi executado fora de ordem (não seguiu: deputados → proposicoes → votacoes)
2. Dados referenciados não existem (ex: proposição referencia deputado que não existe)

**Solução**:
- Execute ETL na ordem correta: `PYTHONPATH=. python scripts/run_etl.py` (já faz isso automaticamente)
- Verifique que os CSVs de entrada têm dados válidos (sem referências quebradas)

### Erro: "database is locked"

**Problema**: Ao rodar testes em paralelo, database is locked

**Solução**: Use in-memory SQLite para testes (já configurado em conftest.py)

### Performance lenta

**Problema**: ETL é muito lento

**Possíveis causas**:
1. Falta de índices em colunas frequentemente consultadas
2. Bulk operations ineficientes

**Solução**:
- Adicione índices nas colunas de foreign key
- Use `bulk_upsert()` em vez de loops com inserts individuais
- Verifique que `sqlite_synchronous` está configurado

### Erro: "ValidationError" durante ETL

**Problema**: Registros no CSV são rejeitados na validação Pydantic

**Comportamento esperado**: Validação é não-fatal. Registros inválidos são pulados e logados como warnings.

**Para investigar**:
1. Procure por "Validation error" nos logs
2. Verifique o CSV de entrada tem dados válidos (encoding UTF-8, separador ";", datas em ISO 8601)

**Solução**: Corrija os dados no CSV e reexecute.

### Erro: "IntegrityError" com duplicates

**Problema**: Ao rodar ETL duas vezes, falha com erro de duplicate

**Solução**: Use `bulk_upsert()` que já trata upserts corretamente (UPDATE se existe, INSERT se novo)

## Exemplos de uso

### Setup completo do zero

```bash
# 1. Clonar e entrar no diretório
git clone <repo>
cd memoria_civica

# 2. Instalar dependências
poetry install

# 3. Ativar ambiente
poetry shell

# 4. Inicializar banco
PYTHONPATH=. python scripts/init_db.py

# 5. Rodar ETL completo
PYTHONPATH=. python scripts/run_etl.py

# 6. Verificar testes
pytest
```

### Rodar apenas um domínio

```bash
# Só ETL de deputados (nota: existem dependências entre domínios)
from src.deputados.etl import run_deputados_etl
exit_code = run_deputados_etl(Path("data/dados_camara/deputados.csv"))
```

### Acessar dados diretamente

```python
from src.shared.database import SessionLocal, get_db
from src.deputados.repository import DeputadoRepository

# Criar session
session = SessionLocal()
repo = DeputadoRepository(session)

# Buscar deputados
deputados = repo.get_all()

# Filtrar por UF
deputados_sp = repo.get_by_uf("SP")

# Buscar específico
deputado = repo.get_by_id(1)

session.close()
```

### Adicionar domínio novo

1. Criar diretório `src/{novo_dominio}/`
2. Criar `models.py` com SQLAlchemy models
3. Criar `schemas.py` com Pydantic schemas
4. Criar `repository.py` com operações CRUD
5. Criar `etl.py` com pipeline (extract → transform → load)
6. Criar `tests/test_{novo_dominio}/` com tests
7. Criar migration: `alembic revision -m "add_{novo_dominio}_table"`
8. Atualizar `scripts/run_etl.py` para orquestrar o novo domínio

## Status

🚧 **Em desenvolvimento** - Setup inicial em andamento

Fases completadas:
- ✅ Estrutura do projeto e dependências
- ✅ Módulo shared (database, config)
- ✅ Domínio de Deputados (models, schemas, repository, ETL)
- ✅ Domínio de Proposições (models, schemas, repository, ETL)
- ✅ Domínio de Votações (models, schemas, repository, ETL)
- ✅ Scripts de orquestração ETL
- 🚧 Documentação e validação end-to-end

## Contribuição

### Como contribuir

1. Crie uma branch para sua feature: `git checkout -b feature/minha-feature`
2. Faça commits descritivos: `git commit -m "feat: descrição clara da mudança"`
3. Certifique-se que testes passam: `make test`
4. Certifique-se que linting passa: `make lint`
5. Envie pull request com descrição clara

### Convenções de commit

Use conventional commits:
- `feat:` para novas features
- `fix:` para bug fixes
- `docs:` para mudanças em documentação
- `test:` para testes
- `refactor:` para refactoring sem mudança de comportamento
- `perf:` para melhorias de performance

### Guidelines

- Mantenha type hints atualizado
- Escreva docstrings completos
- Mantenha coverage acima de 70%
- Teste sua mudança antes de enviar PR
- Respeite os padrões de código estabelecidos

## Recursos

- [Câmara API](https://www2.camara.leg.br/a-camara/conheca/historia/timeline) - Fonte dos dados
- [SQLAlchemy](https://docs.sqlalchemy.org/) - ORM utilizado
- [Alembic](https://alembic.sqlalchemy.org/) - Migrations
- [Pydantic](https://docs.pydantic.dev/) - Data validation
- [Pytest](https://docs.pytest.org/) - Testing framework

---

_Última atualização: Janeiro 2025_
