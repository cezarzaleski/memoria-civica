---
title: Plano de Implementacao da V1
date: 2026-03-28
status: draft
---

# Plano de Implementacao da V1

Baseado em:

- [indice-mestre-v1.md](/Users/cezar.zaleski/workspace/pessoal/memoria_civica/docs/indice-mestre-v1.md)
- [arquitetura-tecnica-v1.md](/Users/cezar.zaleski/workspace/pessoal/memoria_civica/docs/arquitetura-tecnica-v1.md)
- [arquitetura-minima-sinais-v1.md](/Users/cezar.zaleski/workspace/pessoal/memoria_civica/docs/arquitetura-minima-sinais-v1.md)
- [arquitetura-coleta-sistemica-evidencias-v1.md](/Users/cezar.zaleski/workspace/pessoal/memoria_civica/docs/arquitetura-coleta-sistemica-evidencias-v1.md)
- [stack-dados-recomendado-v1.md](/Users/cezar.zaleski/workspace/pessoal/memoria_civica/docs/stack-dados-recomendado-v1.md)
- [fluxo-operacional-consulta-v1.md](/Users/cezar.zaleski/workspace/pessoal/memoria_civica/docs/fluxo-operacional-consulta-v1.md)
- [mapa-arquitetura-sistema-v1.md](/Users/cezar.zaleski/workspace/pessoal/memoria_civica/docs/mapa-arquitetura-sistema-v1.md)

A V1 deve nascer como sistema `query-first`, sob demanda, auditavel e frugal:

`consulta -> identidade -> evidencias oficiais -> sinais explicaveis -> semaforo com fontes`

## 1. Modulos do Sistema

- `consulta-entrypoint`
  - CLI primeiro, com API HTTP opcional expondo a mesma operacao `consultar-candidato`
- `query-orchestrator`
  - coordena fluxo ponta a ponta, classifica o tipo do candidato e define o plano de coleta
- `identity-resolver`
  - resolve nome canonico, aliases, partido, UF, status e IDs oficiais; bloqueia ambiguidade forte
- `collection-planner`
  - traduz `perfil do candidato + sinais necessarios` em chamadas minimas por fonte
- `source-connectors`
  - adaptadores para `mcp-brasil`, Camara, TSE e, em segunda camada, TCU e Portal da Transparencia
- `evidence-store`
  - persiste identidade resolvida, evidencias, metadados de coleta e cache seletivo
- `evidence-classifier`
  - classifica cada item como `strong_official`, `official_partial`, `complementary`, `weak` ou `insufficient`
- `signal-engine`
  - calcula `integrity`, `evidence_level`, `coherence` e `values_fit`, sempre com justificativa e limitacoes
- `editorial-config`
  - carrega watchlist e regras publicas ja definidas, sem reabrir curadoria nesta entrega
- `response-assembler`
  - monta payload final com semaforo, razoes, alertas, confianca e fontes
- `review-queue`
  - marca casos ambiguos ou sensiveis para revisao humana ou editorial fora do caminho automatico principal

## 2. Interfaces Entre Modulos

### 2.1 Entrada canonica

```json
{
  "candidate_name": "string",
  "uf": "string?",
  "party": "string?",
  "user_priorities": ["string"]
}
```

### 2.2 Fluxo de interfaces

- `consulta-entrypoint -> query-orchestrator`
  - `ConsultCandidateRequest`
- `query-orchestrator -> identity-resolver`
  - `IdentityQuery { name, uf?, party?, office: "deputado_federal" }`
- `identity-resolver -> query-orchestrator`
  - `ResolvedCandidate { canonical_name, aliases[], status, party?, uf?, official_ids, ambiguity_level }`
- `query-orchestrator -> collection-planner`
  - `CollectionPlanningInput { candidate, requested_signals, user_priorities? }`
- `collection-planner -> source-connectors`
  - lista ordenada de `CollectionTask { source, objective, params, priority }`
- `source-connectors -> evidence-store`
  - `RawEvidence`
- `evidence-store -> evidence-classifier`
  - `StoredEvidence[]`
- `evidence-classifier -> signal-engine`
  - `ClassifiedEvidence[]`
- `editorial-config -> signal-engine`
  - `WatchlistRules` apenas para `values_fit`
- `signal-engine -> response-assembler`
  - `SignalResults + confidence + gaps`

### 2.3 Saida canonica

```json
{
  "candidate": {},
  "traffic_light": "green|yellow|red|gray",
  "confidence": "high|medium|low",
  "summary": "string",
  "reasons": ["string"],
  "alerts": ["string"],
  "signals": {
    "integrity": {},
    "coherence": {},
    "evidence_level": {},
    "values_fit": {}
  },
  "sources": ["string"]
}
```

## 3. Sequencia de Entrega em Fases

### Fase 0: Fundacao Tecnica

- contratos de entrada e saida
- modelo relacional minimo para identidade, evidencias, classificacoes, execucoes e cache
- CLI funcional
- observabilidade basica por consulta

### Fase 1: Nucleo do MVP

- `identity-resolver`
- conectores `Camara` e `TSE`
- `evidence-store`
- `evidence-classifier`
- `signal-engine` com `evidence_level` e `integrity`
- resposta `gray`
- fluxo de desambiguacao

### Fase 2: Completude Operacional Minima

- classificacao de tipo de candidato
- `collection-planner` por perfil
- `coherence` para incumbentes com base em votos, proposicoes e atuacao formal
- cache seletivo por identidade, evidencia e sinal

### Fase 3: Expansao Controlada

- conectores `TCU` e `Portal da Transparencia`
- `review-queue` para casos sensiveis
- `values_fit` com regras editoriais ja congeladas

### Fase 4: Endurecimento

- testes de regressao por fonte
- politicas de TTL e invalidacao
- metricas de latencia, cobertura de fontes e taxa de resposta `gray`

## 4. MVP Tecnico Realista

Escopo minimo recomendavel:

- CLI de consulta nominal
- payload de resposta estavel
- resolucao de identidade robusta
- coleta sob demanda com `Camara + TSE`
- persistencia leve de evidencias e cache
- sinais `evidence_level` e `integrity` obrigatorios
- `coherence` apenas para incumbentes federais
- `values_fit` inicialmente simplificado ou marcado como `insufficient` quando faltar base editorial aplicavel

### Regra de corte se houver pressao de prazo

1. manter identidade
2. manter `evidence_level`
3. manter `integrity`
4. manter `coherence` so para incumbentes
5. simplificar `values_fit`

## 5. Riscos de Implementacao e Mitigacao

### 5.1 Ambiguidade de identidade

Risco:

- homonimos, nomes incompletos, mudanca de partido ou UF

Mitigacao:

- bloqueio explicito
- score de ambiguidade
- pedido de `UF` ou `partido`

### 5.2 Assimetria entre incumbentes e desafiantes

Risco:

- incumbentes tem mais evidencia que desafiantes

Mitigacao:

- regras distintas por perfil
- uso legitimo de `gray`

### 5.3 Instabilidade de fontes externas

Risco:

- APIs instaveis
- paginacao inconsistente
- mudancas de schema

Mitigacao:

- conectores isolados
- normalizacao interna
- retries curtos
- cache
- testes por schema

### 5.4 Taxonomia ruim de integridade

Risco:

- misturar condenacao, processo, investigacao, sancao e mencao contextual

Mitigacao:

- separar categorias
- jornalismo nunca decide sozinho

### 5.5 Arbitrariedade em `values_fit`

Risco:

- inferencia editorial instavel

Mitigacao:

- tratar a camada editorial como configuracao versionada e auditavel

### 5.6 Cache desatualizado

Risco:

- devolver leitura antiga em contexto eleitoral sensivel

Mitigacao:

- TTL por fonte
- invalidacao por nova coleta
- exposicao de `collected_at`

### 5.7 Crescimento indevido para pipeline massivo

Risco:

- reconstruir ETL pesado cedo demais

Mitigacao:

- preservar regra arquitetural central: consulta sob demanda primeiro

## 6. Decisao Final

A implementacao deve comecar por um nucleo pequeno e confiavel:

- `CLI ou API minima`
- `identidade`
- `Camara e TSE`
- `evidencia persistida`
- `sinais explicitos`
- `resposta auditavel`

Se isso estiver solido, a V1 ja existe tecnicamente.

Tudo alem disso e expansao, nao pre-condicao.
