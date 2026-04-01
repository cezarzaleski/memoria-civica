# Design: Coherence Incremental via Camara

Date: 2026-04-01

## Objetivo

Expandir o sinal de `coherence` para incumbentes federais usando blocos oficiais da Camara, sem introduzir score opaco nem dependencia de curadoria editorial.

## Escopo

- manter `coherence` restrito a `deputado_federal` com status `incumbent`
- coletar evidencia oficial adicional da Camara para o bloco `voting_summary`
- preservar `formal_activity_record` como bloco minimo existente
- ajustar o `signal-engine` para decidir por combinacao de blocos oficiais, nao por texto bruto
- adiar `propositions_summary` para um slice posterior, porque o `mcp-brasil` atual nao expoe vinculo confiavel por autor neste fluxo

## Abordagem

### Opcao recomendada

Usar regras estruturadas por cobertura de blocos oficiais:

- `0` blocos -> `insufficient`
- `1` bloco -> `mixed`
- `2+` blocos distintos -> `positive`

Essa abordagem e auditavel, testavel e conservadora.

### Opcao descartada

Criar score ponderado por texto ou por pesos politicos nesta fase. Isso amplia demais a inferencia metodologica antes da base operacional estar estavel.

## Mudancas previstas

### Coleta

- expandir o conector da Camara para buscar:
  - resumo de votacoes nominais recentes do deputado, quando disponivel via `mcp-brasil`

### Planejamento

- pedir esses blocos apenas para incumbentes federais quando `coherence` for solicitado

### Sinal

- classificar `coherence` pela presenca de blocos `strong_official` da Camara
- manter mensagem explicita quando houver cobertura parcial

## Regras de resposta

- nao inferir alinhamento tematico
- nao transformar quantidade em qualidade politica
- nao remover o alerta atual de limitacao sem evidencia nominal suficiente
- nao simular vinculo de proposicoes por deputado sem suporte estrutural da ferramenta

## Testes

- unitarios do `signal-engine` para `1` e `2+` blocos
- unitarios do `collection-planner` para confirmar novas tarefas
- testes do conector para mapear evidencia `voting_summary`
- smoke test do CLI com caso real de incumbente
