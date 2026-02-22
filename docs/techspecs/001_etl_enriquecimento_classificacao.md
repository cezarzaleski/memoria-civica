# Tech Spec 001 — ETL: Enriquecimento e Classificação Cívica de Votações

**Status:** Draft
**Autor:** Cezar Zaleski
**Data:** 2026-02-12
**Escopo:** Pipeline ETL — join de dados, ingestão de novas fontes, classificação por regras

> Esta tech spec cobre apenas a camada de dados (ETL + classificação por regex). A segunda tech spec (002) cobrirá o enriquecimento via LLM (explicações em linguagem simples, tags semânticas, "por que importa").

---

## 1. Contexto e Motivação

### 1.1 Estado Atual

O ETL atual ingere 4 entidades da API Dados Abertos da Câmara:

| Entidade | Tabela | Registros (2024) | CSV |
|----------|--------|-------------------|-----|
| Deputados | `deputados` | ~7.800 | `deputados.csv` |
| Proposições | `proposicoes` | ~61.500 | `proposicoes.csv` |
| Votações | `votacoes` | ~10.300 | `votacoes.csv` |
| Votos | `votos` | ~116.400 | `votos.csv` |

A relação `votacoes.proposicao_id` hoje é 1:1 (uma votação aponta para uma proposição), derivada do campo `ultimaApresentacaoProposicao_idProposicao` do CSV. Esse campo é preenchido em apenas ~40% dos casos.

### 1.2 Problema

1. **Dados desconectados**: O CSV `votacoes_proposicoes.csv` (7.430 registros) contém o mapeamento real entre votações e proposições, incluindo ementa e tipo. O ETL atual ignora esse arquivo.

2. **Sem filtragem de relevância**: Das 10.371 votações, apenas ~440 são nominais (com votos individuais registrados). As demais são procedurais/automáticas. O sistema não diferencia.

3. **Orientações de bancada ausentes**: O CSV `orientacoes.csv` (4.361 registros) com orientações dos líderes partidários não é ingerido.

4. **Sem classificação temática**: Não existe categorização das votações por impacto cívico (gastos públicos, tributação, direitos sociais, etc.).

### 1.3 Objetivo

Ao final desta spec, o pipeline será capaz de:

- Ingerir `votacoes_proposicoes.csv` e `orientacoes.csv`
- Enriquecer cada votação nominal com dados da(s) proposição(ões) vinculada(s)
- Classificar proposições em categorias de impacto cívico via regex
- Expor dados prontos para consumo pelo frontend/API (tech spec futura)

---

## 2. Decisões de Design

### 2.1 Relação Votação ↔ Proposição

**Decisão:** Manter a FK `votacoes.proposicao_id` existente (1:1) E criar tabela junction `votacoes_proposicoes` (N:N).

**Justificativa:** Uma votação pode estar associada a múltiplas proposições (ex: requerimento de urgência para um PL gera uma votação linkada tanto ao REQ quanto ao PL). O campo 1:1 existente serve como "proposição principal" (fallback), enquanto a junction table dá a visão completa.

### 2.2 Proposição Principal

**Decisão:** Para cada votação, eleger uma "proposição principal" usando ordem de prioridade de tipo:

```
PEC > PLP > PL > MPV > PDL > PFC > TVR > REQ > outros
```

**Justificativa:** Quando uma votação está linkada a um PL e ao REQ de urgência desse PL, o cidadão quer ver o PL, não o requerimento. A proposição principal é a que aparece no feed.

### 2.3 Classificação por Regras (não LLM)

**Decisão:** Classificação baseada em regex sobre `ementa` + `keywords` da proposição. Cada proposição pode receber múltiplas categorias.

**Justificativa:** Regex cobre ~30% das votações com boa precisão e zero custo. O LLM (tech spec 002) refinará os ~70% restantes. Regex serve como baseline determinística e verificável.

### 2.4 Armazenamento de Categorias

**Decisão:** Tabela separada `classificacoes_civicas` com relação N:N com proposições, em vez de coluna texto na tabela de proposições.

**Justificativa:** Permite queries eficientes ("todas as votações sobre tributação"), facilita adição de novas categorias, e distingue classificação por regra vs. por LLM (campo `origem`).

---

## 3. Modelo de Dados — Novas Tabelas

### 3.1 `votacoes_proposicoes` (junction table)

> **Nota sobre IDs:** O model atual `Votacao` usa `Integer` como PK, extraindo apenas a parte numérica antes do hífen do CSV (ex: `"2367548-7"` → `2367548`). As novas tabelas seguem essa convenção. O ID original completo (com hífen) é armazenado em `votacao_id_original` para rastreabilidade.

```sql
CREATE TABLE votacoes_proposicoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    votacao_id INTEGER NOT NULL,             -- ID numérico (parte antes do hífen)
    votacao_id_original VARCHAR(50),         -- ID completo da API (ex: "2367548-7")
    proposicao_id INTEGER NOT NULL,
    titulo VARCHAR(255),                     -- "PL 10106/2018"
    ementa TEXT,                             -- Ementa da proposição neste contexto
    sigla_tipo VARCHAR(20),                  -- PL, PLP, PEC, MPV, REQ...
    numero INTEGER,
    ano INTEGER,
    eh_principal BOOLEAN DEFAULT FALSE,      -- Proposição principal desta votação
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (votacao_id) REFERENCES votacoes(id) ON DELETE CASCADE,
    FOREIGN KEY (proposicao_id) REFERENCES proposicoes(id) ON DELETE CASCADE,
    UNIQUE(votacao_id, proposicao_id)
);

CREATE INDEX ix_vp_votacao_id ON votacoes_proposicoes(votacao_id);
CREATE INDEX ix_vp_proposicao_id ON votacoes_proposicoes(proposicao_id);
CREATE INDEX ix_vp_principal ON votacoes_proposicoes(eh_principal);
```

### 3.2 `orientacoes`

```sql
CREATE TABLE orientacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    votacao_id INTEGER NOT NULL,             -- ID numérico (parte antes do hífen)
    votacao_id_original VARCHAR(50),         -- ID completo da API
    sigla_bancada VARCHAR(100) NOT NULL,     -- "PT", "PL", "Governo", "Minoria"
    orientacao VARCHAR(20) NOT NULL,         -- "Sim", "Não", "Liberado", "Obstrução"
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (votacao_id) REFERENCES votacoes(id) ON DELETE CASCADE,
    UNIQUE(votacao_id, sigla_bancada)
);

CREATE INDEX ix_orientacoes_votacao_id ON orientacoes(votacao_id);
CREATE INDEX ix_orientacoes_bancada ON orientacoes(sigla_bancada);
```

### 3.3 `categorias_civicas` (lookup)

```sql
CREATE TABLE categorias_civicas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo VARCHAR(50) NOT NULL UNIQUE,       -- "GASTOS_PUBLICOS", "TRIBUTACAO_ISENCAO"
    nome VARCHAR(100) NOT NULL,               -- "Gastos Públicos"
    descricao TEXT,                            -- Explicação da categoria
    icone VARCHAR(10)                          -- Emoji: "💰", "📋", etc.
);
```

Seed data (9 categorias):

| codigo | nome | icone |
|--------|------|-------|
| GASTOS_PUBLICOS | Gastos Públicos | 💰 |
| TRIBUTACAO_AUMENTO | Aumento de Tributos | 📈 |
| TRIBUTACAO_ISENCAO | Isenção Tributária | 🏷️ |
| BENEFICIOS_CATEGORIAS | Benefícios para Categorias | 👔 |
| DIREITOS_SOCIAIS | Direitos Sociais | 🏥 |
| SEGURANCA_JUSTICA | Segurança e Justiça | ⚖️ |
| MEIO_AMBIENTE | Meio Ambiente | 🌿 |
| REGULACAO_ECONOMICA | Regulação Econômica | 🏭 |
| POLITICA_INSTITUCIONAL | Política Institucional | 🏛️ |

### 3.4 `proposicoes_categorias` (junction)

```sql
CREATE TABLE proposicoes_categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    proposicao_id INTEGER NOT NULL,
    categoria_id INTEGER NOT NULL,
    origem VARCHAR(20) NOT NULL DEFAULT 'regra',  -- "regra" ou "llm"
    confianca FLOAT DEFAULT 1.0,                   -- 1.0 para regra, 0.0-1.0 para LLM
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (proposicao_id) REFERENCES proposicoes(id) ON DELETE CASCADE,
    FOREIGN KEY (categoria_id) REFERENCES categorias_civicas(id) ON DELETE CASCADE,
    UNIQUE(proposicao_id, categoria_id, origem)
);

CREATE INDEX ix_pc_proposicao_id ON proposicoes_categorias(proposicao_id);
CREATE INDEX ix_pc_categoria_id ON proposicoes_categorias(categoria_id);
```

### 3.5 Alteração em `votacoes`

Adicionar colunas:

```sql
ALTER TABLE votacoes ADD COLUMN eh_nominal BOOLEAN DEFAULT FALSE;
ALTER TABLE votacoes ADD COLUMN votos_sim INTEGER DEFAULT 0;
ALTER TABLE votacoes ADD COLUMN votos_nao INTEGER DEFAULT 0;
ALTER TABLE votacoes ADD COLUMN votos_outros INTEGER DEFAULT 0;
ALTER TABLE votacoes ADD COLUMN descricao TEXT;
ALTER TABLE votacoes ADD COLUMN sigla_orgao VARCHAR(50);

CREATE INDEX ix_votacoes_nominal ON votacoes(eh_nominal);
```

---

## 4. Regras de Classificação

### 4.1 Engine

Classe `ClassificadorCivico` que recebe `ementa` + `keywords` e retorna lista de categorias.

```python
class ClassificadorCivico:
    def classificar(self, ementa: str, keywords: str = "") -> list[CategoriaMatch]:
        """Retorna categorias que deram match, com padrão que matchou."""
        ...
```

### 4.2 Padrões por Categoria

| Categoria | Padrões (regex, case-insensitive) |
|-----------|-----------------------------------|
| GASTOS_PUBLICOS | `crédito extraordinário`, `crédito suplementar`, `crédito especial`, `dotação orçamentária`, `abre crédito`, `\bLOA\b`, `\bLDO\b`, `\bPPA\b`, `orçament`, `despesa pública`, `gasto público` |
| TRIBUTACAO_AUMENTO | `aument.*tribut`, `major.*impost`, `alíquota.*maior`, `contribuição.*social`, `imposto.*renda`, `\bIBS\b`, `\bCBS\b`, `reforma tributária`, `tribut` |
| TRIBUTACAO_ISENCAO | `isenção`, `isent`, `incentivo fiscal`, `benefício fiscal`, `benefício tributário`, `redução.*alíquota`, `zona franca`, `regime especial`, `desoneração`, `simples nacional` |
| BENEFICIOS_CATEGORIAS | `remuneração.*magistrad`, `subsídio.*ministro`, `vencimentos.*servidor`, `reajuste.*salar`, `piso.*salarial`, `aposentadoria.*servidor`, `prerrogativa`, `foro privilegiado`, `cota parlamentar`, `verba.*gabinete`, `auxílio.*morad` |
| DIREITOS_SOCIAIS | `\bSUS\b`, `educação`, `saúde`, `moradia`, `direito.*trabalh`, `salário.?mínimo`, `\bBPC\b`, `\bLOAS\b`, `previdência social`, `aposentadoria` (exceto servidor), `bolsa.*famíl`, `assistência social` |
| SEGURANCA_JUSTICA | `código penal`, `segurança pública`, `armamento`, `porte.*arma`, `\bcrime\b`, `\bpena\b`, `prisão`, `improbidade`, `corrupção`, `lavagem.*dinheiro`, `tráfico`, `penal` |
| MEIO_AMBIENTE | `meio ambiente`, `ambiental`, `desmatamento`, `clima`, `emissão`, `carbono`, `licenciamento ambiental`, `código florestal`, `área.*proteção`, `reserva.*ambiental`, `sustentab`, `reciclagem` |
| REGULACAO_ECONOMICA | `privatização`, `concessão`, `regulação`, `mercado`, `concorrência`, `monopólio`, `agência reguladora`, `licitação`, `\bPPP\b`, `parceria público`, `marco regulatório`, `estatal` |
| POLITICA_INSTITUCIONAL | `eleitor`, `eleitoral`, `partido`, `campanha`, `reforma política`, `reforma administrativa`, `administração pública`, `fundo partidário`, `propaganda.*eleitoral` |

### 4.3 Desambiguação

Conflitos comuns e como resolver:

- **"aposentadoria"** → DIREITOS_SOCIAIS, exceto se acompanhado de "servidor", "magistrado", "militar" → BENEFICIOS_CATEGORIAS
- **"isenção" + "tributo"** → Conta para TRIBUTACAO_ISENCAO, não TRIBUTACAO_AUMENTO
- **Proposição sem ementa** → Sem classificação (categoria vazia)

---

## 5. Fluxo do Pipeline Atualizado

```
┌─────────────────────────────────────────────────────┐
│                    run_etl.py                        │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Fase 1: Ingestão base (existente)                  │
│  ├── ETL Deputados ✅                               │
│  ├── ETL Proposições ✅                             │
│  ├── ETL Votações ✅ (+ novos campos)               │
│  └── ETL Votos ✅                                   │
│                                                     │
│  Fase 2: Ingestão relacional (NOVO)                 │
│  ├── ETL Votações-Proposições 🆕                    │
│  │   ├── Ingestão do CSV                            │
│  │   └── Eleição da proposição principal            │
│  └── ETL Orientações 🆕                             │
│                                                     │
│  Fase 3: Enriquecimento (NOVO)                      │
│  ├── Marcar votações nominais 🆕                    │
│  │   └── eh_nominal = TRUE onde votosSim > 0        │
│  └── Classificação cívica por regras 🆕             │
│      ├── Iterar proposições com ementa              │
│      ├── Aplicar regex engine                       │
│      └── Inserir em proposicoes_categorias          │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 6. Breakdown de Tasks

### Task 1 — Migration: Novas tabelas e colunas

**O que fazer:**
- Criar migration Alembic `005_add_votacoes_proposicoes_table.py`
- Criar migration `006_add_orientacoes_table.py`
- Criar migration `007_add_categorias_civicas_tables.py` (categorias + junction + seed)
- Criar migration `008_add_votacoes_columns.py` (novos campos em votacoes)

**Critérios de aceite:**
- `alembic upgrade head` roda sem erros
- `alembic downgrade -1` (x4) reverte sem erros
- Tabelas e índices criados conforme spec seção 3

**Estimativa:** P (pequeno)

---

### Task 2 — Models + Schemas: Novas entidades

**O que fazer:**
- Criar `etl/src/votacoes/models.py` — adicionar models `VotacaoProposicao` e `Orientacao`
- Criar `etl/src/classificacao/models.py` — models `CategoriaCivica` e `ProposicaoCategoria`
- Criar schemas Pydantic correspondentes em `schemas.py` de cada módulo
- Atualizar model `Votacao` com novos campos (`eh_nominal`, `votos_sim`, `votos_nao`, `votos_outros`, `descricao`, `sigla_orgao`)

**Critérios de aceite:**
- Models refletem exatamente o schema SQL da seção 3
- Schemas validam dados de entrada/saída
- Relationships SQLAlchemy configurados (cascade, backref)
- Testes unitários para validação dos schemas

**Estimativa:** P

---

### Task 3 — Repository: Novos repositórios

**O que fazer:**
- `VotacaoProposicaoRepository` com métodos: `bulk_upsert`, `get_by_votacao`, `get_principal_by_votacao`, `get_by_proposicao`
- `OrientacaoRepository` com métodos: `bulk_upsert`, `get_by_votacao`, `get_by_bancada`
- `CategoriaCivicaRepository` com métodos: `get_all`, `get_by_codigo`, `seed` (popular tabela lookup)
- `ProposicaoCategoriaRepository` com métodos: `bulk_upsert`, `get_by_proposicao`, `get_by_categoria`, `delete_by_origem`

**Critérios de aceite:**
- Todos os métodos testados com SQLite in-memory
- `bulk_upsert` é idempotente
- `get_principal_by_votacao` retorna a proposição com maior prioridade de tipo

**Estimativa:** M (médio)

---

### Task 4 — ETL: Ingestão de `votacoes_proposicoes.csv`

**O que fazer:**

Extract:
```python
def extract_votacoes_proposicoes_csv(csv_path: Path) -> list[dict]:
    # Campos CSV: idVotacao, uriVotacao, data, descricao,
    #   proposicao_id, proposicao_uri, proposicao_titulo, proposicao_ementa,
    #   proposicao_codTipo, proposicao_siglaTipo, proposicao_numero, proposicao_ano
```

Transform:
```python
def transform_votacoes_proposicoes(raw_data: list[dict], db=None) -> list[VotacaoProposicaoCreate]:
    # - Parsear idVotacao: extrair parte numérica (split("-")[0]) para FK
    #   e armazenar string completa em votacao_id_original
    # - Validar FK: votacao_id existe em votacoes
    # - Validar FK: proposicao_id existe em proposicoes (se não, criar com dados do CSV)
    # - Eleger eh_principal por prioridade de tipo
```

Load:
```python
def load_votacoes_proposicoes(data: list[VotacaoProposicaoCreate], db=None) -> int:
    # bulk_upsert com constraint UNIQUE(votacao_id, proposicao_id)
```

**Critérios de aceite:**
- 7.430 registros processados do CSV
- FK violations logadas como warning, não erro fatal
- `eh_principal` corretamente calculado (PEC > PLP > PL > MPV > REQ > outros)
- Proposições não encontradas no banco são criadas a partir dos dados do CSV
- Testes com fixtures CSV

**Estimativa:** M

---

### Task 5 — ETL: Ingestão de `orientacoes.csv`

**O que fazer:**

Extract:
```python
def extract_orientacoes_csv(csv_path: Path) -> list[dict]:
    # Campos CSV: idVotacao, uriVotacao, siglaOrgao, descricao,
    #   siglaBancada, uriBancada, orientacao
```

Transform:
```python
def transform_orientacoes(raw_data: list[dict], db=None) -> list[OrientacaoCreate]:
    # - Parsear idVotacao: extrair parte numérica (split("-")[0]) para FK
    #   e armazenar string completa em votacao_id_original
    # - Validar FK: votacao_id existe em votacoes
    # - Normalizar orientacao: "Sim", "Não", "Liberado", "Obstrução"
    # - Filtrar registros sem orientacao (NaN)
```

Load:
```python
def load_orientacoes(data: list[OrientacaoCreate], db=None) -> int:
    # bulk_upsert com constraint UNIQUE(votacao_id, sigla_bancada)
```

**Critérios de aceite:**
- 4.361 registros processados
- Orientações nulas/vazias filtradas
- Testes com fixtures CSV

**Estimativa:** P

---

### Task 6 — ETL: Atualizar transform de Votações

**O que fazer:**
- Atualizar `transform_votacoes()` para extrair novos campos do CSV:
  - `votosSim` → `votos_sim`
  - `votosNao` → `votos_nao`
  - `votosOutros` → `votos_outros`
  - `descricao` → `descricao`
  - `siglaOrgao` → `sigla_orgao`
- Calcular `eh_nominal = votos_sim > 0`
- Atualizar schema `VotacaoCreate` com novos campos

**Critérios de aceite:**
- Votações carregadas com todos os novos campos
- `eh_nominal` corretamente setado para ~440 votações
- Campos existentes não quebram (retrocompatibilidade)
- Testes atualizados

**Estimativa:** P

---

### Task 7 — Classificação: Engine de regras

**O que fazer:**
- Criar módulo `etl/src/classificacao/`
  - `__init__.py`
  - `models.py` (já na Task 2)
  - `schemas.py` (já na Task 2)
  - `engine.py` — Classe `ClassificadorCivico`
  - `patterns.py` — Definição dos padrões regex por categoria
  - `repository.py` (já na Task 3)
- Implementar `ClassificadorCivico.classificar(ementa, keywords)`:
  - Normalizar texto (lowercase, remover acentos para matching)
  - Aplicar regex por categoria
  - Resolver desambiguações (seção 4.3)
  - Retornar lista de `CategoriaMatch(categoria_codigo, padrao_matchado, confianca=1.0)`

**Critérios de aceite:**
- Testes unitários com pelo menos 3 ementas por categoria (27+ testes)
- Testes de desambiguação ("aposentadoria" genérica vs. servidor)
- Classificação determinística (mesmo input → mesmo output)
- Cobertura: ≥90% do módulo

**Estimativa:** M

---

### Task 8 — ETL: Step de classificação no pipeline

**O que fazer:**
- Criar `etl/src/classificacao/etl.py`:
  ```python
  def run_classificacao_etl(db=None) -> int:
      # 1. Buscar proposições com ementa (via proposicoes + votacoes_proposicoes)
      # 2. Para cada proposição, aplicar ClassificadorCivico
      # 3. Salvar em proposicoes_categorias com origem='regra'
      # 4. Retornar contagem de classificações criadas
  ```
- Seed das categorias cívicas (tabela lookup) no início do step

**Critérios de aceite:**
- ~30% das proposições classificadas em ≥1 categoria
- Seed idempotente (re-executar não duplica categorias)
- Classificações existentes com `origem='regra'` são substituídas (não acumuladas)
- Classificações com `origem='llm'` são preservadas

**Estimativa:** P

---

### Task 9 — Orquestração: Atualizar `run_etl.py`

**O que fazer:**
- Adicionar Fase 2 (ingestão relacional) e Fase 3 (enriquecimento) ao pipeline
- Ordem de execução:
  1. Deputados
  2. Proposições
  3. Votações (com novos campos)
  4. Votos
  5. Votações-Proposições (inclui eleição de principal)
  6. Orientações
  7. Classificação cívica
- Atualizar logging e métricas de execução
- Atualizar `run_full_etl.py` (Docker) com novos CSVs no download

**Critérios de aceite:**
- Pipeline completo roda end-to-end sem erros
- Métricas logadas: registros processados/pulados por step
- Falha em step não-crítico (orientações, classificação) não bloqueia pipeline
- `run_full_etl.py` baixa os 2 novos CSVs

**Estimativa:** P

---

### Task 10 — Testes de integração end-to-end

**O que fazer:**
- Criar `etl/tests/test_integration/test_full_pipeline.py`
- Teste com fixtures que cobrem todo o fluxo:
  1. Ingestão de deputados, proposições, votações, votos
  2. Ingestão de votações-proposições e orientações
  3. Classificação cívica
  4. Verificar: votação nominal → proposição principal → categorias → orientações
- Teste de idempotência: rodar pipeline 2x, verificar que dados não duplicam
- Teste de integridade referencial: verificar que FKs estão consistentes

**Critérios de aceite:**
- Teste end-to-end passa com dados de fixture
- Idempotência verificada
- Coverage total do projeto ≥70%

**Estimativa:** M

---

## 7. Dados de Referência

### 7.1 Volumes esperados (legislatura 57, 2024)

| Entidade | Registros | Crescimento/mês |
|----------|-----------|-----------------|
| Votações nominais | ~440 | ~40 |
| Votações-proposições | ~7.430 | ~600 |
| Orientações | ~4.361 | ~400 |
| Classificações (regra) | ~1.500 | ~150 |

### 7.2 Performance esperada

Pipeline completo (todos os steps) deve rodar em < 2 minutos com SQLite local. Classificação por regex deve processar 5.000 proposições em < 5 segundos.

---

## 8. Fora de Escopo

Itens que ficam para a tech spec 002 (LLM):

- Explicação de ementas em linguagem simples
- Classificação semântica dos ~70% não classificados por regex
- Tag "por que importa" para cada votação
- Detecção de temas compostos (ex: "reforma tributária verde")
- Geração de headlines para o feed

Itens que ficam para tech specs futuras:

- API REST para servir dados classificados
- Frontend / feed de votações
- Compartilhamento social
- Notificações

---

## 9. Dependências e Riscos

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| CSV `votacoes_proposicoes` muda formato | Baixa | Médio | Validação no extract com fallback |
| Regex classifica incorretamente | Média | Baixo | Testes extensivos + LLM corrige na spec 002 |
| Proposições sem ementa (~60%) | Certa | Médio | Classificação depende de ementa; sem ementa = sem classificação. LLM pode classificar pela descrição da votação na spec 002 |
| Volume cresce com dados de 2025 | Certa | Baixo | Volumes são pequenos para SQLite |

---

## 10. Ordem de Execução Sugerida

```
Task 1 (Migrations) ─────────────────────────────┐
                                                  │
Task 2 (Models + Schemas) ───────────────────────┤
                                                  │ Paralelo
Task 7 (Engine classificação) ───────────────────┤
                                                  │
├─────────────────────────────────────────────────┘
│
├── Task 3 (Repository) ──────────┐
│                                 │
├── Task 6 (Transform votações) ──┤ Sequencial após 1+2
│                                 │
├── Task 4 (ETL votações-prop.) ──┤
│                                 │
├── Task 5 (ETL orientações) ─────┤
│                                 │
├── Task 8 (ETL classificação) ───┘
│
├── Task 9 (Orquestração) ─── Depende de 4, 5, 6, 8
│
└── Task 10 (Integração) ──── Depende de tudo
```

Tasks 1, 2 e 7 podem ser desenvolvidas em paralelo. Tasks 3-8 dependem de 1+2. Task 9 integra tudo. Task 10 valida.

---

## Apêndice A — Estrutura de Diretórios Final

```
etl/src/
├── shared/
│   ├── config.py
│   ├── database.py
│   ├── downloader.py
│   └── webhook.py
├── deputados/
│   ├── models.py
│   ├── schemas.py
│   ├── etl.py
│   └── repository.py
├── proposicoes/
│   ├── models.py
│   ├── schemas.py
│   ├── etl.py
│   └── repository.py
├── votacoes/
│   ├── models.py          ← atualizado (novos campos, VotacaoProposicao, Orientacao)
│   ├── schemas.py         ← atualizado
│   ├── etl.py             ← atualizado (novos extracts/transforms)
│   └── repository.py      ← atualizado (novos repositories)
└── classificacao/          ← NOVO módulo
    ├── __init__.py
    ├── models.py           (CategoriaCivica, ProposicaoCategoria)
    ├── schemas.py
    ├── engine.py           (ClassificadorCivico)
    ├── patterns.py         (definição dos regex por categoria)
    ├── etl.py              (run_classificacao_etl)
    └── repository.py       (CategoriaCivicaRepository, ProposicaoCategoriaRepository)
```

## Apêndice B — Exemplo de Dado Classificado

```json
{
  "votacao": {
    "id": "2420577-7",
    "data": "2024-03-12",
    "descricao": "Rejeitado o Recurso. Sim: 139; não: 290; total: 429.",
    "eh_nominal": true,
    "votos_sim": 139,
    "votos_nao": 290,
    "sigla_orgao": "PLEN"
  },
  "proposicao_principal": {
    "id": 81,
    "tipo": "PL",
    "numero": 81,
    "ano": 2024,
    "ementa": "Altera a Lei nº 11.482, de 31 de maio de 2007, a fim de assegurar a atualização automática da faixa de isenção do Imposto de Renda das pessoas físicas (IRPF) ao valor de 2 (dois) salários mínimos."
  },
  "categorias": [
    {"codigo": "TRIBUTACAO_AUMENTO", "nome": "Aumento de Tributos", "icone": "📈", "origem": "regra"},
    {"codigo": "TRIBUTACAO_ISENCAO", "nome": "Isenção Tributária", "icone": "🏷️", "origem": "regra"}
  ],
  "orientacoes": [
    {"bancada": "Governo", "orientacao": "Não"},
    {"bancada": "PT", "orientacao": "Não"},
    {"bancada": "PL", "orientacao": "Sim"}
  ],
  "polarizacao_pct": 67.6
}
```
