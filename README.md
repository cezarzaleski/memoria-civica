# Memória Cívica - Fundação de Dados

[![Tests](https://github.com/cezarzaleski/memoria-civica/actions/workflows/test.yml/badge.svg)](https://github.com/cezarzaleski/memoria-civica/actions/workflows/test.yml)

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
python etl/scripts/init_db.py  # Inicializar banco
python etl/scripts/run_etl.py  # Executar pipeline
```

**Testes:**
```bash
pytest etl/tests/
```

### **Arquivos de configuração raiz**

- `alembic/` e `alembic.ini`: Migrations de banco (mantidos na raiz para acesso fácil)
- `.python-version`: Especificação da versão do Python (monorepo-wide)
- `.env.example`: Template de variáveis de ambiente (monorepo-wide)

## Pré-requisitos

- Python 3.11+
- Poetry (gerenciador de dependências Python - instalado no diretório etl/)
- Node.js 20+ (para frontend)
- SQLite 3.35+

## Setup ETL

1. **Navegar para o diretório ETL:**
   ```bash
   cd etl
   ```

2. **Instalar dependências:**
   ```bash
   poetry install
   ```

3. **Ativar ambiente virtual:**
   ```bash
   poetry shell
   ```

4. **Inicializar banco de dados (da raiz do projeto):**
   ```bash
   cd ..
   python etl/scripts/init_db.py
   ```

## Execução ETL

- **ETL completo:**
  ```bash
  python etl/scripts/run_etl.py
  ```

- **Executar testes:**
  ```bash
  pytest etl/tests/
  ```

- **Coverage:**
  ```bash
  pytest etl/tests/ --cov=etl/src --cov-report=html
  ```

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
├── .python-version            # Versão Python (monorepo-wide)
├── .env.example               # Template de variáveis de ambiente
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
cd etl
poetry run ruff check src tests
```

### Formatar código

```bash
cd etl
poetry run ruff format src tests
```

### Estrutura de testes

```
etl/tests/
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
pytest etl/tests/

# Testes de um domínio
pytest etl/tests/test_deputados/

# Apenas testes de integração
pytest etl/tests/ -m integration

# Com coverage
pytest etl/tests/ --cov=etl/src --cov-report=html
```

## Continuous Integration (CI)

O projeto usa GitHub Actions para CI/CD com jobs separados para frontend e ETL. O pipeline detecta automaticamente mudanças e executa apenas os jobs relevantes.

### Workflow ETL

O job de testes do ETL no CI executa os seguintes steps:

1. **Setup**: Checkout, Python 3.11, Poetry instalação
2. **Cache**: Cache de dependências Poetry para performance
3. **Dependências**: `poetry install` em `etl/`
4. **Migrations**: `poetry -C etl run python etl/scripts/init_db.py` para criar banco e tabelas
5. **Linting**: `poetry run ruff check src tests` em `etl/`
6. **Testes**: `poetry run pytest tests/` em `etl/`

### Setup de banco de dados no CI

**IMPORTANTE**: O CI executa migrações Alembic automaticamente antes dos testes usando o script `etl/scripts/init_db.py`. Isso garante que:

- A tabela `alembic_version` existe e está atualizada
- Todas as tabelas do schema (deputados, proposicoes, votacoes, votos) são criadas
- O banco de dados SQLite está inicializado no caminho correto (`./memoria_civica.db`)

O comando usado no CI é:
```bash
poetry -C etl run python etl/scripts/init_db.py
```

Este comando:
- Usa o Poetry instalado em `etl/` (`-C etl`)
- Executa do diretório raiz do projeto (onde `alembic.ini` está localizado)
- Roda todas as migrações pendentes com `alembic upgrade head`

### Dados de teste no CI

O CI usa arquivos CSV mock mínimos em `data/dados_camara/` para testes de smoke que verificam a presença de dados:

- `deputados.csv`
- `proposicoes.csv`
- `votacoes.csv`
- `votos.csv`

Estes arquivos contêm apenas uma linha de dados cada (além do header) e são suficientes para validar que o diretório de dados está corretamente configurado. Os testes unitários usam fixtures mais completas em `etl/tests/fixtures/`.

### Troubleshooting CI

**Erro: `no such table: alembic_version`**
- Causa: Migrações não foram executadas antes dos testes
- Solução: Verificar que o step "Run Alembic migrations" está presente e sendo executado antes do step "Run tests"

**Erro: `Nenhum arquivo CSV encontrado`**
- Causa: Diretório `data/dados_camara/` está vazio
- Solução: Verificar que arquivos CSV mock existem no diretório (não apenas `.gitkeep`)

**Erro: `database is locked`**
- Causa: Testes unitários usando banco real em vez de in-memory SQLite
- Solução: Fixtures de teste devem usar `sqlite:///:memory:` para testes unitários

## Troubleshooting

### Erro: "no such table"

**Problema**: Ao rodar ETL, você vê erro "no such table: deputados"

**Solução**: Execute o script de inicialização do banco:
```bash
python etl/scripts/init_db.py
```

Este script cria todas as tabelas via Alembic migrations.

### Erro: "FOREIGN KEY constraint failed"

**Problema**: ETL falha com erro de constraint de chave estrangeira

**Possíveis causas**:
1. ETL foi executado fora de ordem (não seguiu: deputados → proposicoes → votacoes)
2. Dados referenciados não existem (ex: proposição referencia deputado que não existe)

**Solução**:
- Execute ETL na ordem correta: `python etl/scripts/run_etl.py` (já faz isso automaticamente)
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

# 2. Instalar dependências ETL
cd etl
poetry install
poetry shell
cd ..

# 3. Inicializar banco
python etl/scripts/init_db.py

# 4. Rodar ETL completo
python etl/scripts/run_etl.py

# 5. Verificar testes
pytest etl/tests/

# 6. Setup Frontend (opcional)
cd frontend
npm install
npm run dev
```

### Rodar apenas um domínio

```python
# Só ETL de deputados (nota: existem dependências entre domínios)
from pathlib import Path
from etl.src.deputados.etl import run_deputados_etl

exit_code = run_deputados_etl(Path("data/dados_camara/deputados.csv"))
```

### Acessar dados diretamente

```python
from etl.src.shared.database import SessionLocal, get_db
from etl.src.deputados.repository import DeputadoRepository

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

1. Criar diretório `etl/src/{novo_dominio}/`
2. Criar `models.py` com SQLAlchemy models
3. Criar `schemas.py` com Pydantic schemas
4. Criar `repository.py` com operações CRUD
5. Criar `etl.py` com pipeline (extract → transform → load)
6. Criar `etl/tests/test_{novo_dominio}/` com tests
7. Criar migration: `alembic revision -m "add_{novo_dominio}_table"`
8. Atualizar `etl/scripts/run_etl.py` para orquestrar o novo domínio

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
3. Certifique-se que testes passam: `pytest etl/tests/` (para ETL) ou `npm run test` (para frontend)
4. Certifique-se que linting passa: `cd etl && poetry run ruff check src tests` (para ETL) ou `npm run lint` (para frontend)
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
