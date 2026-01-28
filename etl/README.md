# ETL Memória Cívica

[![Tests](https://github.com/cezarzaleski/memoria-civica/actions/workflows/test.yml/badge.svg)](https://github.com/cezarzaleski/memoria-civica/actions/workflows/test.yml)

Pipeline ETL para coleta, validação e estruturação de dados da Câmara dos Deputados.

## Visão Geral

O ETL (Extract, Transform, Load) do Memória Cívica é responsável por:
- Extrair dados de votações, deputados e proposições da Câmara dos Deputados
- Validar e transformar os dados usando Pydantic schemas
- Carregar os dados estruturados no banco de dados SQLite

## Stack Tecnológico

- **Python 3.11+** - Linguagem principal
- **Poetry** - Gerenciador de dependências
- **SQLAlchemy** - ORM para acesso ao banco de dados
- **Alembic** - Gerenciamento de migrations
- **Pydantic** - Validação de dados
- **Pytest** - Framework de testes
- **Ruff** - Linting e formatação

## Estrutura do Projeto

```
etl/
├── src/               # Código fonte
│   ├── deputados/     # Domínio de Deputados
│   ├── proposicoes/   # Domínio de Proposições
│   ├── votacoes/      # Domínio de Votações
│   └── shared/        # Código compartilhado (config, database, utils)
├── scripts/           # Scripts de orquestração
│   ├── init_db.py     # Inicialização do banco de dados
│   └── run_etl.py     # Execução do pipeline ETL
├── tests/             # Testes
│   ├── test_deputados/
│   ├── test_proposicoes/
│   ├── test_votacoes/
│   └── test_shared/
└── pyproject.toml     # Configuração e dependências
```

## Configuração e Desenvolvimento

### Pré-requisitos

- Python 3.11+
- Poetry instalado (`pip install poetry`)
- SQLite 3.35+

### Instalação

Instale as dependências do projeto a partir da raiz:

```bash
# Da raiz do projeto
poetry install
```

### Ativar ambiente virtual

```bash
poetry shell
```

### Inicializar banco de dados

```bash
python etl/scripts/init_db.py
```

### Executar ETL

```bash
python etl/scripts/run_etl.py
```

## Testes

### Executar testes

```bash
# Da raiz do projeto
make test

# Ou diretamente com pytest
pytest etl/tests/
```

### Cobertura de testes

```bash
pytest etl/tests/ --cov=etl/src --cov-report=html
```

Target de cobertura: **≥80%**

## Linting e Formatação

### Executar linting

```bash
# Da raiz do projeto
make lint

# Ou diretamente com Ruff
ruff check etl/
```

### Formatar código

```bash
# Da raiz do projeto
make format

# Ou diretamente com Ruff
ruff format etl/
```

## Domínios

### Deputados

Gerencia informações dos 513 deputados federais:
- Nome completo e nome civil
- Partido e UF
- ID da API da Câmara

### Proposições

Gerencia projetos de lei, PECs e MPs:
- Número, ano e tipo
- Ementa e descrição
- Status de tramitação

### Votações

Gerencia registros de votações:
- Data e hora
- Resultado (aprovado/rejeitado)
- Votos individuais de cada deputado

## Padrões de Código

- **Type hints**: Obrigatório para todas as funções públicas
- **Docstrings**: Google style para funções e classes públicas
- **Line length**: 120 caracteres (configurado no Ruff)
- **Imports**: Organizados automaticamente pelo Ruff

## Troubleshooting

### Erro: "no such table"

Execute o script de inicialização do banco:
```bash
python etl/scripts/init_db.py
```

### Erro: "FOREIGN KEY constraint failed"

Certifique-se de executar o ETL na ordem correta:
1. Deputados
2. Proposições
3. Votações

O script `run_etl.py` já faz isso automaticamente.

### Erro: "database is locked"

Use in-memory SQLite para testes (já configurado em conftest.py).

### Performance lenta

- Verifique índices em foreign keys
- Use `bulk_upsert()` em vez de inserts individuais
- Confira configuração `sqlite_synchronous`

## Referências

- [SQLAlchemy](https://docs.sqlalchemy.org/) - ORM utilizado
- [Alembic](https://alembic.sqlalchemy.org/) - Migrations
- [Pydantic](https://docs.pydantic.dev/) - Data validation
- [Pytest](https://docs.pytest.org/) - Testing framework
- [Ruff](https://docs.astral.sh/ruff/) - Linter e formatter

---

_Veja o [README principal](../README.md) para mais informações sobre o projeto._
