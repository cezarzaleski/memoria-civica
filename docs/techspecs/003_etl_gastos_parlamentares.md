# Tech Spec 003 — ETL: Gastos Parlamentares (CEAP)

**Status:** Draft
**Autor:** Cezar Zaleski
**Data:** 2026-02-22
**Escopo:** Novo domínio no pipeline ETL para ingestão de dados da Cota para Exercício da Atividade Parlamentar (CEAP)

> _Esta spec cobre exclusivamente o pipeline de dados (ETL). A exibição no frontend está fora de escopo e será tratada em implementação posterior conforme a PRD de Transparência de Gastos._

---

## 1. Contexto e Motivação

### 1.1 Estado Atual

O ETL do Memória Cívica possui 4 domínios: `deputados`, `proposicoes`, `votacoes` e `classificacao`. Todos seguem o padrão de 4 arquivos (`models.py`, `schemas.py`, `etl.py`, `repository.py`) e consomem CSVs bulk da API de Dados Abertos da Câmara.

### 1.2 Problema

Não existe nenhum dado sobre gastos parlamentares no sistema. A Cota Parlamentar (CEAP) é a principal fonte de dados sobre como deputados utilizam recursos públicos — informação essencial para accountability cívica.

### 1.3 Objetivo

Criar o domínio `src/gastos/` no ETL, ingerindo o CSV de despesas da Câmara a partir da origem anual compactada (`Ano-{ano}.csv.zip`) e produzindo `gastos-{ano}.csv` para consumo do ETL, seguindo os padrões estabelecidos, com upsert idempotente e integração no pipeline orquestrado.

---

## 2. Fonte de Dados

### 2.1 CSV Bulk (método primário)

| Atributo | Valor |
|----------|-------|
| **URL** | `https://www.camara.leg.br/cotas/Ano-{ano}.csv.zip` |
| **Formato** | ZIP contendo `Ano-{ano}.csv` (CSV, encoding UTF-8-sig, separador `;`) |
| **Atualização** | Diária |
| **Histórico** | 2008 até ano corrente |
| **Volume** | ~256.000 registros/ano (513 deputados x ~500 despesas) |

### 2.2 Campos do CSV

| Campo CSV | Tipo | Descrição |
|-----------|------|-----------|
| `idDeputado` | int | ID do deputado na Câmara |
| `nomeDeputado` | string | Nome parlamentar |
| `cpf` | string | CPF do deputado (mascarado) |
| `siglaPartido` | string | Partido |
| `siglaUF` | string | Unidade federativa |
| `idDocumento` | int | ID interno do documento |
| `tipoDespesa` | string | Categoria da despesa (22 tipos) |
| `tipoDocumento` | string | "Nota Fiscal", "Nota Fiscal Eletrônica", "Recibos/Outros" |
| `dataDocumento` | date | Data do documento fiscal |
| `numDocumento` | string | Número da nota/recibo |
| `valorDocumento` | decimal | Valor bruto (formato brasileiro: `1.234,56`) |
| `valorLiquido` | decimal | Valor líquido cobrado da cota |
| `valorGlosa` | decimal | Valor glosado/rejeitado |
| `nomeFornecedor` | string | Nome do fornecedor |
| `cnpjCpfFornecedor` | string | CNPJ ou CPF do fornecedor |
| `urlDocumento` | string | URL do PDF da nota fiscal |
| `numRessarcimento` | string | Referência de ressarcimento |
| `codLote` | int | Lote de processamento |
| `parcela` | int | Parcela (0 = pagamento único) |
| `ano` | int | Ano da despesa |
| `mes` | int | Mês da despesa |

### 2.3 Categorias de Despesa (22 tipos)

| Categoria |
|-----------|
| MANUTENÇÃO DE ESCRITÓRIO DE APOIO À ATIVIDADE PARLAMENTAR |
| LOCOMOÇÃO, ALIMENTAÇÃO E HOSPEDAGEM |
| COMBUSTÍVEIS E LUBRIFICANTES |
| CONSULTORIAS, PESQUISAS E TRABALHOS TÉCNICOS |
| DIVULGAÇÃO DA ATIVIDADE PARLAMENTAR |
| AQUISIÇÃO DE MATERIAL DE ESCRITÓRIO |
| AQUISIÇÃO OU LOCAÇÃO DE SOFTWARE; SERVIÇOS POSTAIS |
| SERVIÇO DE SEGURANÇA PRESTADO POR EMPRESA ESPECIALIZADA |
| PASSAGEM AÉREA - REEMBOLSO |
| TELEFONIA |
| SERVIÇOS POSTAIS |
| ASSINATURA DE PUBLICAÇÕES |
| FORNECIMENTO DE ALIMENTAÇÃO DO DEPUTADO |
| HOSPEDAGEM, EXCETO DO PARLAMENTAR NO DISTRITO FEDERAL |
| LOCAÇÃO OU FRETAMENTO DE AERONAVES |
| LOCAÇÃO OU FRETAMENTO DE VEÍCULOS AUTOMOTORES |
| LOCAÇÃO OU FRETAMENTO DE EMBARCAÇÕES |
| SERVIÇO DE TÁXI, PEDÁGIO E ESTACIONAMENTO |
| PASSAGENS TERRESTRES, MARÍTIMAS OU FLUVIAIS |
| PARTICIPAÇÃO EM CURSO, PALESTRA OU EVENTO SIMILAR |
| AQUISIÇÃO DE TOKENS E CERTIFICADOS DIGITAIS |
| PASSAGEM AÉREA - SIGEPA / RPA |

---

## 3. Decisões de Design

### 3.1 Chave primária auto-increment

**Decisão:** Usar `id INTEGER PRIMARY KEY AUTOINCREMENT` ao invés de PK natural.

**Justificativa:** O CSV de despesas não possui um campo de ID único. A combinação `(deputado_id, ano, mes, tipo_despesa, cnpj_cpf_fornecedor, numero_documento)` serve como constraint de unicidade para upsert, mas não é prática como PK.

### 3.2 Upsert via ON CONFLICT

**Decisão:** Usar `INSERT...ON CONFLICT DO UPDATE` (padrão PostgreSQL) ao invés de delete-then-reinsert.

**Justificativa:** Com ~256k registros/ano, o padrão delete-reinsert seria custoso e arriscaria cascades. O upsert via `ON CONFLICT` no unique constraint é idempotente e eficiente. Segue o mesmo padrão de `OrientacaoRepository` e `ProposicaoCategoriaRepository`.

### 3.3 FK para deputados nullable

**Decisão:** `deputado_id INTEGER REFERENCES deputados(id) ON DELETE SET NULL` — nullable.

**Justificativa:** O CSV de despesas pode conter registros de deputados que não estão na legislatura atual (suplentes, afastados). O mesmo padrão é usado em `proposicoes.autor_id`.

### 3.4 Valores monetários como Numeric

**Decisão:** Usar `Numeric(12, 2)` para campos de valor.

**Justificativa:** Evita erros de arredondamento de `Float` em valores financeiros. O CSV usa formato brasileiro (`1.234,56`) que deve ser normalizado no transform.

### 3.5 Mapeamento deputado_id via idDeputado do CSV

**Decisão:** Usar `idDeputado` do CSV diretamente como FK, pois corresponde ao `id` na tabela `deputados`.

**Justificativa:** O campo `idDeputado` no CSV de despesas é o mesmo ID usado no CSV de deputados e na API REST da Câmara. Não é necessário lookup adicional.

---

## 4. Modelo de Dados

### 4.1 Tabela `gastos`

```sql
CREATE TABLE gastos (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    deputado_id           INTEGER REFERENCES deputados(id) ON DELETE SET NULL,
    ano                   INTEGER NOT NULL,
    mes                   INTEGER NOT NULL,
    tipo_despesa          VARCHAR(255) NOT NULL,
    tipo_documento        VARCHAR(50),
    data_documento        DATE,
    numero_documento      VARCHAR(100),
    valor_documento       NUMERIC(12, 2) NOT NULL DEFAULT 0,
    valor_liquido         NUMERIC(12, 2) NOT NULL DEFAULT 0,
    valor_glosa           NUMERIC(12, 2) NOT NULL DEFAULT 0,
    nome_fornecedor       VARCHAR(255),
    cnpj_cpf_fornecedor   VARCHAR(20),
    url_documento         TEXT,
    cod_documento         INTEGER,
    cod_lote              INTEGER,
    parcela               INTEGER DEFAULT 0,

    CONSTRAINT uq_gasto UNIQUE (
        deputado_id, ano, mes, tipo_despesa,
        cnpj_cpf_fornecedor, numero_documento
    )
);

CREATE INDEX ix_gastos_deputado_id ON gastos(deputado_id);
CREATE INDEX ix_gastos_ano_mes ON gastos(ano, mes);
CREATE INDEX ix_gastos_tipo_despesa ON gastos(tipo_despesa);
CREATE INDEX ix_gastos_fornecedor ON gastos(cnpj_cpf_fornecedor);
```

### 4.2 SQLAlchemy Model

```python
from sqlalchemy import (
    Column, Integer, String, Numeric, Date, Text,
    ForeignKey, UniqueConstraint, Index
)
from src.shared.database import Base

class Gasto(Base):
    __tablename__ = "gastos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    deputado_id = Column(Integer, ForeignKey("deputados.id", ondelete="SET NULL"), nullable=True)
    ano = Column(Integer, nullable=False)
    mes = Column(Integer, nullable=False)
    tipo_despesa = Column(String(255), nullable=False)
    tipo_documento = Column(String(50), nullable=True)
    data_documento = Column(Date, nullable=True)
    numero_documento = Column(String(100), nullable=True)
    valor_documento = Column(Numeric(12, 2), nullable=False, default=0)
    valor_liquido = Column(Numeric(12, 2), nullable=False, default=0)
    valor_glosa = Column(Numeric(12, 2), nullable=False, default=0)
    nome_fornecedor = Column(String(255), nullable=True)
    cnpj_cpf_fornecedor = Column(String(20), nullable=True)
    url_documento = Column(Text, nullable=True)
    cod_documento = Column(Integer, nullable=True)
    cod_lote = Column(Integer, nullable=True)
    parcela = Column(Integer, default=0)

    __table_args__ = (
        UniqueConstraint(
            "deputado_id", "ano", "mes", "tipo_despesa",
            "cnpj_cpf_fornecedor", "numero_documento",
            name="uq_gasto"
        ),
        Index("ix_gastos_deputado_id", "deputado_id"),
        Index("ix_gastos_ano_mes", "ano", "mes"),
        Index("ix_gastos_tipo_despesa", "tipo_despesa"),
        Index("ix_gastos_fornecedor", "cnpj_cpf_fornecedor"),
    )
```

---

## 5. Fluxo do Pipeline Atualizado

```
FASE 0: Migrations (alembic upgrade head)
    └── 009_add_gastos_table

FASE 1: Download
    └── gastos-{ano}.csv (extraído de Ano-{ano}.csv.zip)  ← NOVO

FASE 2: ETL base
    2.1 deputados
    2.2 proposicoes
    2.3 votacoes + votos
    2.4 gastos                               ← NOVO (depende de deputados)

FASE 3: ETL relacional
    3.1 votacoes_proposicoes
    3.2 orientacoes

FASE 4: Enriquecimento
    4.1 classificacao civica
```

---

## 6. Transform: Tratamento de Dados

### 6.1 Normalização de valores monetários

O CSV usa formato brasileiro. O transform deve converter:

```python
def parse_valor_brasileiro(valor_str: str) -> Decimal:
    """Converte '1.234,56' para Decimal('1234.56')"""
    if not valor_str or valor_str.strip() == "":
        return Decimal("0")
    limpo = valor_str.strip().replace(".", "").replace(",", ".")
    return Decimal(limpo)
```

### 6.2 Validação de FK deputado_id

```python
def transform_gastos(raw_data: list[dict], db: Session) -> list[GastoCreate]:
    # Buscar IDs válidos de deputados
    deputados_validos = set(
        row[0] for row in db.query(Deputado.id).all()
    )

    gastos = []
    for row in raw_data:
        deputado_id = int(row["idDeputado"]) if row.get("idDeputado") else None
        if deputado_id and deputado_id not in deputados_validos:
            deputado_id = None  # SET NULL para deputados não encontrados

        gastos.append(GastoCreate(
            deputado_id=deputado_id,
            ano=int(row["ano"]),
            mes=int(row["mes"]),
            tipo_despesa=row["tipoDespesa"].strip(),
            tipo_documento=row.get("tipoDocumento", "").strip() or None,
            data_documento=parse_date(row.get("dataDocumento")),
            numero_documento=row.get("numDocumento", "").strip() or None,
            valor_documento=parse_valor_brasileiro(row.get("valorDocumento", "0")),
            valor_liquido=parse_valor_brasileiro(row.get("valorLiquido", "0")),
            valor_glosa=parse_valor_brasileiro(row.get("valorGlosa", "0")),
            nome_fornecedor=row.get("nomeFornecedor", "").strip() or None,
            cnpj_cpf_fornecedor=row.get("cnpjCpfFornecedor", "").strip() or None,
            url_documento=row.get("urlDocumento", "").strip() or None,
            cod_documento=safe_int(row.get("idDocumento")),
            cod_lote=safe_int(row.get("codLote")),
            parcela=safe_int(row.get("parcela")) or 0,
        ))
    return gastos
```

### 6.3 Mapeamento CSV → Model

| Campo CSV | Campo Model | Transformação |
|-----------|------------|---------------|
| `idDeputado` | `deputado_id` | Validar FK; NULL se não encontrado |
| `ano` | `ano` | `int()` |
| `mes` | `mes` | `int()` |
| `tipoDespesa` | `tipo_despesa` | `.strip()` |
| `tipoDocumento` | `tipo_documento` | `.strip()`, None se vazio |
| `dataDocumento` | `data_documento` | Parse `YYYY-MM-DD` ou `DD/MM/YYYY` |
| `numDocumento` | `numero_documento` | `.strip()`, None se vazio |
| `valorDocumento` | `valor_documento` | `parse_valor_brasileiro()` |
| `valorLiquido` | `valor_liquido` | `parse_valor_brasileiro()` |
| `valorGlosa` | `valor_glosa` | `parse_valor_brasileiro()` |
| `nomeFornecedor` | `nome_fornecedor` | `.strip()`, None se vazio |
| `cnpjCpfFornecedor` | `cnpj_cpf_fornecedor` | `.strip()`, manter sem formatação |
| `urlDocumento` | `url_documento` | `.strip()`, None se vazio |
| `idDocumento` | `cod_documento` | `safe_int()` |
| `codLote` | `cod_lote` | `safe_int()` |
| `parcela` | `parcela` | `safe_int()`, default 0 |

---

## 7. Breakdown de Tasks

### Task 1 — Criar modelo e schema

**O que fazer:**
- Criar `src/gastos/__init__.py`
- Criar `src/gastos/models.py` com classe `Gasto`
- Criar `src/gastos/schemas.py` com `GastoCreate` e `GastoRead`

**Critérios de aceite:**
- Model importável sem erros
- Schemas validam campos obrigatórios e tipos
- `GastoRead` possui `model_config = {"from_attributes": True}`

**Estimativa:** P

### Task 2 — Criar migration

**O que fazer:**
- Criar `alembic/versions/009_add_gastos_table.py`
- Incluir tabela, indexes e unique constraint
- Testar `upgrade` e `downgrade`

**Critérios de aceite:**
- `alembic upgrade head` executa sem erros
- `alembic downgrade -1` reverte corretamente

**Estimativa:** P

### Task 3 — Criar repository

**O que fazer:**
- Criar `src/gastos/repository.py` com `GastoRepository`
- Implementar `bulk_upsert()` usando `pg_insert...ON CONFLICT DO UPDATE`
- Implementar queries: `get_by_deputado()`, `get_by_ano_mes()`, `get_resumo_por_categoria()`

**Critérios de aceite:**
- Upsert idempotente: rodar 2x com mesmo CSV produz mesmo resultado
- Queries retornam dados corretos com fixtures de teste

**Estimativa:** M

### Task 4 — Criar ETL (extract, transform, load)

**O que fazer:**
- Criar `src/gastos/etl.py`
- Implementar `extract_gastos_csv()` com UTF-8-sig e separador `;`
- Implementar `transform_gastos()` com normalização de valores e validação de FK
- Implementar `load_gastos()` e `run_gastos_etl()`
- Adicionar `@retry_with_backoff(max_retries=3)`

**Critérios de aceite:**
- CSV de fixture processado corretamente
- Valores `1.234,56` convertidos para `Decimal('1234.56')`
- Deputados inexistentes resultam em `deputado_id = NULL`
- Pipeline idempotente

**Estimativa:** M

### Task 5 — Integrar no download e orquestrador

**O que fazer:**
- Adicionar `"gastos"` ao `FILE_CONFIGS` e `DOWNLOAD_ORDER` em `scripts/download_camara.py`
- Adicionar step 2.4 em `scripts/run_full_etl.py`
- Marcar como CRÍTICO (aborta pipeline em caso de falha)

**Critérios de aceite:**
- `download_all_files()` baixa o CSV de despesas
- `run_full_etl.py` executa gastos após deputados
- Falha no ETL de gastos aborta o pipeline

**Estimativa:** P

### Task 6 — Testes

**O que fazer:**
- Criar `tests/fixtures/gastos.csv` com 5-10 registros de amostra
- Criar `tests/test_gastos/conftest.py`, `test_schemas.py`, `test_etl.py`, `test_repository.py`
- Cobrir: parsing de valores, FK validation, idempotência do upsert

**Critérios de aceite:**
- Todos os testes passam
- Cobertura de parsing de formato brasileiro (`1.234,56`, vazio, negativo)
- Teste de idempotência (load 2x = mesmo count)

**Estimativa:** M

---

## 8. Fora de Escopo

- API REST para servir gastos ao frontend (será definida em spec separada)
- Agregações e rankings (serão implementados na camada de API/frontend)
- Dados de salários de assessores (indisponível via API programática)
- Remuneração do deputado (somente CSV/PDF no portal de transparência)
- Detecção de anomalias/fraude nos gastos (futuro, estilo Serenata de Amor)
- Ingestão multi-ano em uma única execução (1 ano por run, configurável via `CAMARA_ANO`)

---

## 9. Dependências e Riscos

| Risco | Severidade | Mitigação |
|-------|-----------|-----------|
| Formato do CSV muda sem aviso | Média | Validação de headers no `extract`; alerta via webhook se colunas esperadas faltam |
| Volume alto causa timeout no load | Baixa | Batch insert em chunks de 1000 registros |
| Formato decimal inconsistente entre anos | Média | `parse_valor_brasileiro()` trata ambos os formatos |
| Deputado no CSV não existe na tabela deputados | Baixa | FK nullable com SET NULL (decisão 3.3) |
| CSV indisponível temporariamente | Baixa | ETag cache + retry já implementados no downloader |

---

## 10. Ordem de Execução Sugerida

```
Task 1 (model/schema)
    └── Task 2 (migration)
        └── Task 3 (repository)
            └── Task 4 (ETL)
                └── Task 5 (integração)
                    └── Task 6 (testes — pode iniciar em paralelo com Task 4)
```

---

## Apêndice A — Estrutura de Diretórios

```
etl/
├── src/
│   ├── gastos/                         ← NOVO
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── etl.py
│   │   └── repository.py
│   ├── deputados/
│   ├── proposicoes/
│   ├── votacoes/
│   ├── classificacao/
│   └── shared/
├── alembic/
│   └── versions/
│       └── 009_add_gastos_table.py     ← NOVO
├── scripts/
│   ├── download_camara.py              ← MODIFICADO
│   ├── run_full_etl.py                 ← MODIFICADO
│   └── ...
└── tests/
    ├── fixtures/
    │   └── gastos.csv                  ← NOVO
    └── test_gastos/                    ← NOVO
        ├── conftest.py
        ├── test_schemas.py
        ├── test_etl.py
        └── test_repository.py
```

---

## Apêndice B — Exemplo de Registro CSV

```csv
ano;mes;idDeputado;idDocumento;tipoDespesa;tipoDocumento;dataDocumento;numDocumento;valorDocumento;valorLiquido;valorGlosa;nomeFornecedor;cnpjCpfFornecedor;urlDocumento;numRessarcimento;codLote;parcela
2025;1;220593;7587236;MANUTENÇÃO DE ESCRITÓRIO DE APOIO À ATIVIDADE PARLAMENTAR;Recibos/Outros;2025-01-05;11533012025001;43,20;43,20;0,00;AGUAS CUIABA S.A;14995581000153;https://www.camara.leg.br/cota-parlamentar/documentos/publ/3687/2025/7587236.pdf;;1957493;0
2025;1;220593;7601234;PASSAGEM AÉREA - SIGEPA;Nota Fiscal Eletrônica;2025-01-15;NFE-2025-001;1.850,00;1.850,00;0,00;GOL LINHAS AEREAS S.A;07966508000169;https://www.camara.leg.br/cota-parlamentar/documentos/publ/3687/2025/7601234.pdf;;1957500;0
```

---

_Última atualização: Fevereiro 2026_
