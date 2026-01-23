# Memória Cívica - Fundação de Dados

> "Democracia não é só votar. É lembrar, cobrar e participar."

## Visão Geral

Este projeto estabelece a **fundação de dados** do Memória Cívica, uma ferramenta que dá ao cidadão brasileiro o poder de lembrar o que seus deputados votaram, entender o significado de cada votação, e tomar decisões informadas nas eleições.

Esta fase inicial (Setup Inicial) valida a viabilidade de coletar e estruturar dados de votações da Câmara dos Deputados de 2025, estabelecendo a base para o MVP futuro.

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
   python scripts/init_db.py
   ```

## Execução

- **ETL completo:**
  ```bash
  python scripts/run_etl.py
  ```

- **Executar testes:**
  ```bash
  pytest
  ```

- **Coverage:**
  ```bash
  pytest --cov=src --cov-report=html
  ```

## Arquitetura

Estrutura feature-based organizada por domínio:

```
memoria_civica/
├── src/
│   ├── deputados/      # Domínio de Deputados
│   ├── proposicoes/    # Domínio de Proposições
│   ├── votacoes/       # Domínio de Votações
│   └── shared/         # Infraestrutura compartilhada (DB, config)
├── scripts/            # Scripts de orquestração
├── tests/              # Testes unitários e de integração
├── data/               # Dados CSV
└── alembic/            # Migrations de banco
```

## Domínios

- **Deputados**: Informações dos 513 deputados federais (nome, partido, UF)
- **Proposições**: Projetos de lei, PECs, MPs que são votadas no Plenário
- **Votações**: Registros de votações e votos individuais de cada deputado

## Migrations

- **Criar migration:**
  ```bash
  alembic revision -m "description"
  ```

- **Aplicar migrations:**
  ```bash
  alembic upgrade head
  ```

- **Reverter migration:**
  ```bash
  alembic downgrade -1
  ```

## Status

🚧 **Em desenvolvimento** - Setup inicial em andamento

---

_Última atualização: Janeiro 2025_
