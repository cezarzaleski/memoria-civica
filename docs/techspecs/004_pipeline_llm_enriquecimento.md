# Tech Spec 004 — Pipeline LLM: Enriquecimento de Proposições

**Status:** Draft
**Autor:** Cezar Zaleski
**Data:** 2026-02-22
**Escopo:** Pipeline batch no ETL para gerar conteúdo em linguagem acessível a partir de ementas legislativas usando LLM

> _Esta spec cobre o pipeline de geração e armazenamento. A exibição no frontend está fora de escopo. A spec complementa a Tech Spec 001 (classificação por regex), cobrindo os ~70% de proposições que regex não alcança._

---

## 1. Contexto e Motivação

### 1.1 Estado Atual

O Memória Cívica exibe ementas legislativas no formato original — linguagem jurídica incompreensível para a maioria da população. A Tech Spec 001 implementou classificação por regex em categorias cívicas, mas com cobertura limitada a padrões textuais explícitos.

A página de detalhe da votação já possui um slot para "Explicação Simplificada" (`llmExplanation` prop no `VotacaoDetalhes`), mas atualmente usa texto hardcoded para 5 votações mock.

### 1.2 Problema

- Ementas como "Dispõe sobre a alteração de dispositivos da Lei 11.482/2007" não comunicam nada a um cidadão comum
- O card do feed mostra ementa truncada em 80 chars — puro ruído
- Categorias cívicas cobrem apenas ~30% das proposições (regex)
- O slot de explicação simplificada existe mas não é alimentado por dados reais

### 1.3 Objetivo

Criar uma fase de enriquecimento LLM no pipeline ETL que gere, para cada proposição:

1. **Headline** — frase declarativa em linguagem ativa (para o card do feed)
2. **Resumo simples** — explicação sem juridiquês (para a página de detalhe)
3. **Impacto cidadão** — lista de mudanças concretas na vida das pessoas
4. **Classificação LLM** — categorias cívicas para proposições que o regex não cobriu

---

## 2. Decisões de Design

### 2.1 Processamento batch no ETL

**Decisão:** LLM executa como fase batch no pipeline ETL, armazenando resultados no banco. Não há chamada LLM em tempo de request.

**Justificativa:** Volume previsível (~100 proposições/mês), custo controlado, zero latência no frontend. A alternativa (on-demand) adicionaria 1-5s de latência, custos imprevisíveis e API keys no backend de serving.

### 2.2 Modelo: GPT-4o-mini como padrão

**Decisão:** Usar GPT-4o-mini como modelo primário. Configurável via variável de ambiente.

**Justificativa:** Melhor custo-benefício para português legislativo: $0.15/M input, $0.60/M output. Para 100 proposições/mês (~80k tokens), custo de ~R$ 0,15/mês. Qualidade comprovada para simplificação de texto em português. Gemini 2.0 Flash como alternativa futura.

### 2.3 Output em JSON estruturado

**Decisão:** Forçar output JSON via `response_format: {"type": "json_object"}`.

**Justificativa:** Elimina falhas de parsing. O prompt solicita campos específicos com tipos definidos, permitindo validação automática antes do armazenamento.

### 2.4 Versionamento de prompts

**Decisão:** Armazenar `versao_prompt` junto com cada enriquecimento.

**Justificativa:** Permite re-gerar seletivamente quando o prompt melhorar, sem reprocessar tudo. Também serve como auditoria de qualidade.

### 2.5 Threshold de confiança

**Decisão:** Campo `confianca` (0.0-1.0) reportado pelo próprio LLM. Proposições com `confianca < 0.5` recebem flag `necessita_revisao = TRUE` e não são exibidas no frontend.

**Justificativa:** Ementas ambíguas ou muito abstratas (especialmente MPs e REQs) geram resumos de baixa qualidade. O threshold previne desinformação.

### 2.6 Idempotência: skip se já enriquecido com versão atual

**Decisão:** O pipeline verifica se a proposição já tem enriquecimento com a `versao_prompt` corrente. Se sim, pula. Re-gera apenas se a versão do prompt mudou ou se `force_regenerate=True`.

**Justificativa:** Evita custos desnecessários e permite re-runs seguros do pipeline.

---

## 3. Modelo de Dados

### 3.1 Tabela `enriquecimentos_llm`

```sql
CREATE TABLE enriquecimentos_llm (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    proposicao_id    INTEGER NOT NULL,
    modelo           VARCHAR(50) NOT NULL,
    versao_prompt    VARCHAR(10) NOT NULL,
    headline         TEXT,
    resumo_simples   TEXT,
    impacto_cidadao  TEXT,               -- JSON array de strings
    confianca        FLOAT NOT NULL DEFAULT 1.0,
    necessita_revisao BOOLEAN NOT NULL DEFAULT FALSE,
    tokens_input     INTEGER,
    tokens_output    INTEGER,
    gerado_em        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_enriquecimento UNIQUE (proposicao_id, versao_prompt),
    FOREIGN KEY (proposicao_id) REFERENCES proposicoes(id) ON DELETE CASCADE
);

CREATE INDEX ix_enriquecimentos_proposicao ON enriquecimentos_llm(proposicao_id);
CREATE INDEX ix_enriquecimentos_confianca ON enriquecimentos_llm(confianca);
CREATE INDEX ix_enriquecimentos_revisao ON enriquecimentos_llm(necessita_revisao);
```

### 3.2 SQLAlchemy Model

```python
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime,
    ForeignKey, UniqueConstraint, Index
)
from datetime import datetime
from src.shared.database import Base

class EnriquecimentoLLM(Base):
    __tablename__ = "enriquecimentos_llm"

    id = Column(Integer, primary_key=True, autoincrement=True)
    proposicao_id = Column(Integer, ForeignKey("proposicoes.id", ondelete="CASCADE"), nullable=False)
    modelo = Column(String(50), nullable=False)
    versao_prompt = Column(String(10), nullable=False)
    headline = Column(Text, nullable=True)
    resumo_simples = Column(Text, nullable=True)
    impacto_cidadao = Column(Text, nullable=True)  # JSON array
    confianca = Column(Float, nullable=False, default=1.0)
    necessita_revisao = Column(Boolean, nullable=False, default=False)
    tokens_input = Column(Integer, nullable=True)
    tokens_output = Column(Integer, nullable=True)
    gerado_em = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("proposicao_id", "versao_prompt", name="uq_enriquecimento"),
        Index("ix_enriquecimentos_proposicao", "proposicao_id"),
        Index("ix_enriquecimentos_confianca", "confianca"),
        Index("ix_enriquecimentos_revisao", "necessita_revisao"),
    )
```

---

## 4. Prompt Design

### 4.1 System Prompt (v1.0)

```
Você é um especialista em traduzir linguagem jurídica e legislativa brasileira
para linguagem simples, acessível para cidadãos com ensino médio completo.

Suas respostas devem:
- Usar frases curtas (máximo 20 palavras por frase)
- Evitar jargão jurídico — use o glossário abaixo
- Usar voz ativa ("o governo vai cobrar" em vez de "será cobrado pelo governo")
- Mencionar impactos concretos em reais ou percentuais quando possível
- Nunca inventar informações que não estão no texto original
- Indicar incerteza com "provavelmente" ou "depende de regulamentação" quando o texto for ambíguo

GLOSSÁRIO:
- revoga/revogação → cancela/cancelamento
- vigência → quando começa a valer
- regulamentação posterior → regulamento que o governo ainda vai criar
- facultativo → opcional
- vedado → proibido
- alíquota → percentual de imposto
- dotação orçamentária → dinheiro reservado no orçamento
- crédito extraordinário → verba extra no orçamento
- contribuição → imposto/taxa (no contexto tributário)
- cessão onerosa → aluguel/venda
- PL → Projeto de Lei
- PEC → Proposta de Emenda à Constituição (muda a Constituição)
- MP → Medida Provisória (já vale, mas precisa ser aprovada)
- PLP → Projeto de Lei Complementar (exige mais votos para aprovar)
```

### 4.2 User Prompt Template (v1.0)

```
Analise esta proposição legislativa e gere as saídas solicitadas.

PROPOSIÇÃO:
Tipo: {tipo} {numero}/{ano}
Ementa: {ementa}
Ementa simplificada: {ementa_simplificada}  # se disponível
Categorias já identificadas: {categorias_regex}  # se houver

GERE EXATAMENTE ESTE JSON (sem texto fora do JSON):
{
  "headline": "<frase declarativa de até 120 caracteres, voz ativa, sem siglas>",
  "resumo_simples": "<2-3 parágrafos, máximo 200 palavras, nível ensino médio>",
  "impacto_cidadao": [
    "<impacto concreto 1 — quem é afetado e como>",
    "<impacto concreto 2>",
    "<impacto concreto 3 — somente se houver>"
  ],
  "confianca": <0.0 a 1.0 — quão clara é a ementa para gerar estas saídas>
}
```

### 4.3 Few-shot Examples (incluídos no system prompt)

**Exemplo 1 — Tributação (alta confiança):**

```json
// Input: PL 1234/2024 — "Altera a Lei 11.482/2007 para atualizar a faixa de isenção
//         do imposto sobre a renda das pessoas físicas ao valor de 2 salários mínimos."

{
  "headline": "Câmara vota isenção de imposto de renda para quem ganha até 2 salários mínimos",
  "resumo_simples": "Este projeto muda as regras do Imposto de Renda para pessoas físicas. Hoje, quem ganha até R$ 2.824 por mês não paga IR. Se aprovado, a faixa de isenção passa a acompanhar o salário mínimo automaticamente.\n\nIsso significa que cada vez que o salário mínimo aumentar, mais pessoas ficam isentas do imposto sem precisar de uma nova lei.",
  "impacto_cidadao": [
    "Trabalhadores com renda de até 2 salários mínimos deixam de pagar IR",
    "O valor exato muda todo ano junto com o salário mínimo — hoje seria R$ 2.824/mês"
  ],
  "confianca": 0.95
}
```

**Exemplo 2 — Ementa vaga (baixa confiança):**

```json
// Input: REQ 567/2025 — "Requer a realização de audiência pública para debater
//         assuntos relativos à implementação de políticas públicas."

{
  "headline": "Deputado pede audiência pública sobre políticas do governo",
  "resumo_simples": "Este requerimento pede que a Câmara realize uma audiência pública — uma reunião aberta onde especialistas e cidadãos podem opinar. O tema são políticas públicas do governo, mas o texto não especifica quais.\n\nAudiências públicas não mudam leis diretamente, mas influenciam o debate e as decisões dos deputados.",
  "impacto_cidadao": [
    "Nenhum impacto direto — é um pedido de debate, não uma mudança de lei"
  ],
  "confianca": 0.4
}
```

---

## 5. Fluxo do Pipeline

```
                     ┌──────────────────┐
                     │  proposicoes (DB) │
                     └────────┬─────────┘
                              │
                    ┌─────────▼──────────┐
                    │  Filtrar pendentes  │
                    │  (sem enriquecimento│
                    │   na versão atual)  │
                    └─────────┬──────────┘
                              │
                   ┌──────────▼───────────┐
                   │  Para cada proposição │
                   │  (batch de 10)        │
                   └──────────┬───────────┘
                              │
               ┌──────────────▼──────────────┐
               │  Montar prompt com ementa   │
               │  + categorias regex (se há) │
               └──────────────┬──────────────┘
                              │
                    ┌─────────▼──────────┐
                    │  Chamar LLM API    │
                    │  (GPT-4o-mini)     │
                    │  JSON mode         │
                    └─────────┬──────────┘
                              │
                   ┌──────────▼───────────┐
                   │  Validar JSON output │
                   │  - headline <= 120ch │
                   │  - confianca 0-1     │
                   │  - campos presentes  │
                   └──────────┬───────────┘
                              │
                    ┌─────────▼──────────┐
                    │  confianca < 0.5?  │
                    └──┬──────────────┬──┘
                   SIM │              │ NÃO
                       ▼              ▼
              necessita_revisao   salvar normal
              = TRUE
                       │              │
                       └──────┬───────┘
                              │
                   ┌──────────▼───────────┐
                   │  Upsert em           │
                   │  enriquecimentos_llm │
                   └──────────┬───────────┘
                              │
                   ┌──────────▼───────────┐
                   │  Classificar via LLM │
                   │  (proposicoes sem    │
                   │   categoria regex)   │
                   │  → proposicoes_      │
                   │    categorias         │
                   │    origem='llm'       │
                   └──────────────────────┘
```

---

## 6. Implementação do Client LLM

### 6.1 Configuração

```python
# src/shared/config.py — adicionar campos
class Settings(BaseSettings):
    # ... campos existentes ...

    # LLM
    LLM_PROVIDER: str = "openai"              # "openai" ou "google"
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_API_KEY: str = ""                     # OPENAI_API_KEY ou GOOGLE_API_KEY
    LLM_PROMPT_VERSION: str = "v1.0"
    LLM_CONFIDENCE_THRESHOLD: float = 0.5
    LLM_BATCH_SIZE: int = 10
    LLM_MAX_RETRIES: int = 3
    LLM_ENABLED: bool = True                  # Feature flag
```

### 6.2 Client abstrato

```python
# src/shared/llm_client.py

from abc import ABC, abstractmethod
from pydantic import BaseModel

class EnriquecimentoOutput(BaseModel):
    headline: str
    resumo_simples: str
    impacto_cidadao: list[str]
    confianca: float

class LLMClient(ABC):
    @abstractmethod
    def enriquecer_proposicao(
        self,
        tipo: str,
        numero: int,
        ano: int,
        ementa: str,
        categorias: list[str] | None = None,
    ) -> EnriquecimentoOutput:
        ...

class OpenAIClient(LLMClient):
    def __init__(self, api_key: str, model: str):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def enriquecer_proposicao(self, tipo, numero, ano, ementa, categorias=None):
        response = self.client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": format_user_prompt(
                    tipo, numero, ano, ementa, categorias
                )},
            ],
            temperature=0.3,
            max_tokens=800,
        )
        raw = json.loads(response.choices[0].message.content)
        return EnriquecimentoOutput(**raw)
```

### 6.3 Rate limiting e retry

```python
# Dentro do loop de processamento batch
import time

for batch in chunked(proposicoes_pendentes, settings.LLM_BATCH_SIZE):
    for proposicao in batch:
        for attempt in range(settings.LLM_MAX_RETRIES):
            try:
                resultado = client.enriquecer_proposicao(
                    tipo=proposicao.tipo,
                    numero=proposicao.numero,
                    ano=proposicao.ano,
                    ementa=proposicao.ementa,
                    categorias=categorias_map.get(proposicao.id),
                )
                salvar_enriquecimento(db, proposicao.id, resultado)
                break
            except (RateLimitError, APITimeoutError):
                wait = 2 ** attempt
                logger.warning(f"Retry {attempt+1} em {wait}s para proposição {proposicao.id}")
                time.sleep(wait)
            except Exception as e:
                logger.error(f"Erro ao enriquecer proposição {proposicao.id}: {e}")
                break

        time.sleep(0.5)  # Rate limit conservador entre requests
```

---

## 7. Integração no Pipeline

### 7.1 Posição no `run_full_etl.py`

```python
FASE 4: Enriquecimento
    4.1 classificacao civica (regex)     # já existe
    4.2 enriquecimento LLM              # NOVO — NÃO-CRÍTICO
```

O step 4.2 é **NÃO-CRÍTICO**: falhas incrementam `warnings_count` mas não abortam o pipeline. Isso porque:
- O frontend já funciona sem enriquecimentos
- Falhas de API LLM são transientes
- O próximo run do pipeline processa as proposições que falharam

### 7.2 Dependência do step de classificação

O enriquecimento LLM roda **após** a classificação regex porque:
- Usa as categorias regex como contexto no prompt (melhora a qualidade)
- Classifica via LLM apenas proposições que o regex não cobriu

---

## 8. Estimativa de Custos

### 8.1 Tokens por proposição

| Componente | Tokens estimados |
|-----------|-----------------|
| System prompt (fixo) | ~400 |
| User prompt (ementa + contexto) | ~150-300 |
| Output (headline + resumo + impacto) | ~300-500 |
| **Total por proposição** | **~800-1200** |

### 8.2 Custo mensal estimado

| Cenário | Proposições/mês | Tokens totais | Custo GPT-4o-mini | Custo Claude Haiku |
|---------|----------------|---------------|-------------------|-------------------|
| Normal | 100 | ~100k | R$ 0,15 | R$ 1,20 |
| Pico | 300 | ~300k | R$ 0,45 | R$ 3,60 |
| Re-geração completa | 1000 | ~1M | R$ 1,50 | R$ 12,00 |

---

## 9. Breakdown de Tasks

### Task 1 — Criar modelo e schema do enriquecimento

**O que fazer:**
- Criar `src/enriquecimento/__init__.py`
- Criar `src/enriquecimento/models.py` com `EnriquecimentoLLM`
- Criar `src/enriquecimento/schemas.py` com `EnriquecimentoCreate` e `EnriquecimentoRead`

**Critérios de aceite:**
- Model importável; schema valida JSON de impacto_cidadao como lista de strings

**Estimativa:** P

### Task 2 — Criar migration

**O que fazer:**
- Criar `alembic/versions/010_add_enriquecimentos_llm.py`
- Tabela, indexes, unique constraint

**Critérios de aceite:**
- Upgrade e downgrade executam sem erros

**Estimativa:** P

### Task 3 — Implementar LLM client

**O que fazer:**
- Criar `src/shared/llm_client.py` com interface abstrata + OpenAIClient
- Implementar montagem de prompts (system + user)
- Adicionar configuração em `src/shared/config.py`
- JSON parsing + validação com Pydantic

**Critérios de aceite:**
- Client retorna `EnriquecimentoOutput` válido
- Retry em caso de rate limit
- Configurável via env vars

**Estimativa:** M

### Task 4 — Criar repository

**O que fazer:**
- Criar `src/enriquecimento/repository.py`
- `upsert()` com ON CONFLICT em `(proposicao_id, versao_prompt)`
- `get_pendentes()` — proposições sem enriquecimento na versão atual
- `get_by_proposicao()` — enriquecimento mais recente

**Critérios de aceite:**
- Upsert idempotente
- `get_pendentes()` retorna apenas proposições não processadas na versão atual

**Estimativa:** M

### Task 5 — Criar ETL de enriquecimento

**O que fazer:**
- Criar `src/enriquecimento/etl.py` com `run_enriquecimento_etl()`
- Buscar proposições pendentes
- Processar em batches com rate limiting
- Aplicar threshold de confiança
- Classificar via LLM proposições sem categorias regex

**Critérios de aceite:**
- Pipeline idempotente (re-run não reprocessa)
- `confianca < 0.5` marca `necessita_revisao = TRUE`
- Logs de progresso e custo acumulado

**Estimativa:** G

### Task 6 — Integrar no pipeline e criar prompts

**O que fazer:**
- Adicionar step 4.2 em `run_full_etl.py` (NÃO-CRÍTICO)
- Criar arquivo de prompts versionados
- Adicionar `LLM_*` vars no `.env.example`

**Critérios de aceite:**
- Pipeline roda com LLM desabilitado (`LLM_ENABLED=False`) sem erros
- Pipeline roda com LLM habilitado e processa proposições

**Estimativa:** P

### Task 7 — Testes

**O que fazer:**
- Mock do LLM client para testes unitários
- Testar parsing de output JSON (válido, inválido, parcial)
- Testar threshold de confiança
- Testar idempotência
- Teste de integração com LLM real (marcado como `@pytest.mark.integration`)

**Critérios de aceite:**
- Testes unitários passam sem chamada real à API
- Teste de integração documentado para execução manual

**Estimativa:** M

---

## 10. Fora de Escopo

- Frontend: exibição de headline/resumo/impacto (será tratado separadamente)
- Interface de revisão manual para enriquecimentos com baixa confiança
- Fine-tuning de modelo LLM para domínio legislativo brasileiro
- Tradução para outros idiomas
- Enriquecimento de votações (apenas proposições nesta versão)
- Batch API assíncrona (volume atual não justifica; implementar quando > 1000 props/mês)

---

## 11. Dependências e Riscos

| Risco | Severidade | Mitigação |
|-------|-----------|-----------|
| API OpenAI indisponível | Média | Step NÃO-CRÍTICO; próximo run processa pendentes |
| LLM gera informação incorreta | Alta | `confianca` + threshold + `necessita_revisao`; link para ementa original sempre visível |
| Custo escala com volume inesperado | Baixa | `LLM_BATCH_SIZE` + `LLM_ENABLED` flag; monitorar `tokens_input/output` no DB |
| Prompt em português gera output em inglês | Baixa | System prompt explicita idioma; few-shot em português; validação pós-geração |
| Mudança de preços da API | Baixa | Client abstrato permite trocar modelo/provider sem mudar pipeline |

---

## 12. Ordem de Execução Sugerida

```
Task 1 (model/schema)
    └── Task 2 (migration)
        ├── Task 3 (LLM client)
        └── Task 4 (repository)
            └── Task 5 (ETL) ← depende de 3 e 4
                └── Task 6 (integração pipeline)
                    └── Task 7 (testes — pode iniciar em paralelo com Task 5)
```

---

## Apêndice A — Estrutura de Diretórios

```
etl/
├── src/
│   ├── enriquecimento/                     ← NOVO
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── etl.py
│   │   ├── repository.py
│   │   └── prompts.py                      ← templates versionados
│   ├── shared/
│   │   ├── llm_client.py                   ← NOVO
│   │   ├── config.py                       ← MODIFICADO (add LLM_* vars)
│   │   └── ...
│   └── ...
├── alembic/
│   └── versions/
│       └── 010_add_enriquecimentos_llm.py  ← NOVO
└── tests/
    └── test_enriquecimento/                ← NOVO
        ├── conftest.py
        ├── test_schemas.py
        ├── test_llm_client.py
        ├── test_etl.py
        └── test_repository.py
```

---

## Apêndice B — Exemplo de Output Armazenado

```json
{
  "id": 1,
  "proposicao_id": 42,
  "modelo": "gpt-4o-mini",
  "versao_prompt": "v1.0",
  "headline": "Câmara aprova projeto que simplifica abertura de pequenas empresas",
  "resumo_simples": "Este projeto de lei muda as regras para abrir uma pequena empresa no Brasil. Hoje, o processo exige vários documentos e pode levar semanas. Se aprovado, o registro será feito em um único lugar, com prazo máximo de 5 dias úteis.\n\nA mudança vale para microempresas e empresas de pequeno porte com faturamento de até R$ 4,8 milhões por ano.",
  "impacto_cidadao": [
    "Quem quer abrir uma empresa pequena vai gastar menos tempo e dinheiro com burocracia",
    "O prazo máximo para registro passa a ser 5 dias úteis",
    "Vale para empresas com faturamento de até R$ 4,8 milhões/ano"
  ],
  "confianca": 0.92,
  "necessita_revisao": false,
  "tokens_input": 450,
  "tokens_output": 380,
  "gerado_em": "2026-02-22T15:30:00"
}
```

---

_Última atualização: Fevereiro 2026_
