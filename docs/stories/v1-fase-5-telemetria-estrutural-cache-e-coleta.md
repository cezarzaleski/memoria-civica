---
title: V1 Fase 5 - Telemetria estrutural de cache e coleta
status: Done
date: 2026-04-01
owner: dev
---

# Story

Expor telemetria operacional por escopo (`identity`, `evidence`, `signal`) no `QueryExecutionRecord`, tornando explicito quando cada etapa reutilizou cache ou executou coleta/calculo real sem alterar o payload funcional da consulta.

## Acceptance Criteria

- [x] a execucao registra `cache hit/miss` para `identity`, `evidence` e `signal`
- [x] a telemetria fica no registro operacional da consulta, sem contaminar o payload funcional
- [x] o backend de cache continua agnostico e observavel por wrapper
- [x] testes cobrem wrapper observado e a transicao `miss -> hit` em consultas repetidas
- [x] `npm run lint` passa
- [x] `npm run typecheck` passa
- [x] `npm test` passa

## Checklist

- [x] expandir o modelo de execucao com observabilidade de cache por escopo
- [x] introduzir wrapper observado para `CacheStore`
- [x] plugar a telemetria no `QueryOrchestrator` por consulta
- [x] cobrir `ObservedCacheStore` em testes
- [x] cobrir `QueryOrchestrator` com `miss -> hit` em consultas repetidas
- [x] validar quality gates

## File List

- [x] `packages/memoria-civica/src/domain/models.ts`
- [x] `packages/memoria-civica/src/observability/query-execution.ts`
- [x] `packages/memoria-civica/src/services/cache-store.ts`
- [x] `packages/memoria-civica/src/services/query-orchestrator.ts`
- [x] `tests/cache-store.test.ts`
- [x] `tests/query-orchestrator.test.ts`
- [x] `tests/consulta-entrypoint.test.ts`

## Validation Evidence

- [x] `2026-04-01`: `npm run lint`
- [x] `2026-04-01`: `npm run typecheck`
- [x] `2026-04-01`: `npm test`

## Notes

- A telemetria de cache foi mantida no `QueryExecutionRecord`, preservando o payload funcional da resposta para consumidores do CLI.
- O `ObservedCacheStore` permite instrumentacao por escopo sem acoplar o dominio a Redis, memoria ou qualquer backend especifico.
- O `QueryOrchestrator` passou a construir wrappers observados por consulta para registrar corretamente o ciclo `miss -> hit` em runs repetidos.
