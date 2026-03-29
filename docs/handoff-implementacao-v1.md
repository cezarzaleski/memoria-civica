---
title: Handoff para Implementacao da V1
date: 2026-03-29
status: draft
---

# Handoff para Implementacao da V1

## Objetivo

Iniciar a implementacao da V1 do Memoria Civica sem reabrir discovery, tese de produto, watchlist editorial ou discussao regulatoria.

## Documento ancora

- [plano-implementacao-v1.md](/Users/cezar.zaleski/workspace/pessoal/memoria_civica/docs/plano-implementacao-v1.md)

## Leitura complementar minima

- [indice-mestre-v1.md](/Users/cezar.zaleski/workspace/pessoal/memoria_civica/docs/indice-mestre-v1.md)
- [arquitetura-tecnica-v1.md](/Users/cezar.zaleski/workspace/pessoal/memoria_civica/docs/arquitetura-tecnica-v1.md)
- [fluxo-operacional-consulta-v1.md](/Users/cezar.zaleski/workspace/pessoal/memoria_civica/docs/fluxo-operacional-consulta-v1.md)

## Escopo imediato

Implementar a `Fase 0` e, se houver margem, iniciar a `Fase 1` do plano de implementacao.

## O que fazer agora

1. definir a estrutura minima do projeto para a V1
2. criar contratos de entrada e saida da consulta
3. modelar identidade, evidencias, classificacoes e metadados de coleta
4. preparar `consulta-entrypoint`
5. preparar `query-orchestrator`
6. preparar esqueleto de `identity-resolver`

## O que nao fazer agora

- nao reabrir discovery
- nao reabrir watchlist editorial
- nao reinventar ETL massivo
- nao transformar a V1 em portal ou ranking eleitoral
- nao depender de UI antes da CLI ou API minima

## Regra tecnica central

A V1 deve nascer como:

- `query-first`
- `source-backed`
- `auditavel`
- `frugal`

Fluxo central:

`consulta -> identidade -> evidencias oficiais -> sinais explicaveis -> semaforo com fontes`

## Prompt curto sugerido para o proximo agente

Implemente a Fase 0 e, se sobrar espaco, comece a Fase 1 do [plano-implementacao-v1.md](/Users/cezar.zaleski/workspace/pessoal/memoria_civica/docs/plano-implementacao-v1.md). Nao reabra discovery, watchlist editorial nem tese de produto. Siga o plano tecnico ja definido.
