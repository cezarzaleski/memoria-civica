---
title: V1 Fase 3 - Cache seletivo com TTL
status: Done
date: 2026-04-01
owner: dev
---

# Story

Consolidar a politica de cache do Memoria Civica com backend compartilhado e TTL explicito por escopo (`identity`, `evidence`, `signal`), reduzindo repeticao de chamadas oficiais sem alterar o comportamento funcional.

## Acceptance Criteria

- [x] o `QueryOrchestrator` usa uma `CacheStore` compartilhada para identidade, evidencia e sinal
- [x] a politica de TTL por escopo fica explicita e centralizada
- [x] o backend padrao continua em memoria, sem acoplar o dominio a um store especifico
- [x] testes cobrem hit/miss/expiracao para os caches relevantes
- [x] `npm run lint` passa
- [x] `npm run typecheck` passa
- [x] `npm test` passa

## Checklist

- [x] introduzir politica central de TTL por escopo
- [x] plugar uma `CacheStore` compartilhada no `QueryOrchestrator`
- [x] preservar o comportamento atual quando nao houver cache hit
- [x] cobrir expiracao e hit/miss em testes
- [x] validar quality gates

## File List

- [x] `packages/memoria-civica/src/services/cache-policy.ts`
- [x] `packages/memoria-civica/src/services/query-orchestrator.ts`
- [x] `tests/cache-store.test.ts`
- [x] `tests/identity-resolver.test.ts`
- [x] `tests/cached-evidence-collector.test.ts`
- [x] `tests/cached-signal-service.test.ts`

## Validation Evidence

- [x] `2026-04-01`: `npm run lint`
- [x] `2026-04-01`: `npm run typecheck`
- [x] `2026-04-01`: `npm test`

## Notes

- O `QueryOrchestrator` agora centraliza uma `CacheStore` compartilhada e aplica TTLs explicitos por escopo via `cache-policy.ts`.
- A implementacao manteve o backend padrao em memoria e nao alterou a semantica funcional da consulta quando nao ha cache hit.
- A cobertura de testes passou a incluir isolamento por `scope` no `InMemoryCacheStore` e expiracao para `evidence` e `signal`.
