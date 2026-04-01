---
title: V1 Fase 1 - Nucleo do MVP
status: Done
date: 2026-03-31
owner: dev
---

# Story

Endurecer o nucleo do MVP da V1 do Memoria Civica com resolucao de identidade mais confiavel, classificacao explicita do perfil do candidato e fluxo objetivo de desambiguacao, sem reabrir discovery, watchlist editorial ou expandir fontes alem do necessario.

## Acceptance Criteria

- [x] `identity-resolver` classifica explicitamente o candidato como `incumbent`, `former` ou `challenger`
- [x] consultas com multiplos matches plausiveis param antes da coleta e retornam pedido objetivo de desambiguacao por `uf` e/ou `party`
- [x] `query-orchestrator` preserva no payload final o resultado da resolucao de identidade e o nivel de ambiguidade, inclusive em respostas `gray`
- [x] `collection-planner` escolhe trilha compativel com `incumbent`, `former` e `challenger`
- [x] casos minimos cobrindo um incumbente da Camara, um nome apenas na trilha TSE e um caso ambiguo ficam cobertos por testes
- [x] `npm run lint` passa
- [x] `npm run typecheck` passa
- [x] `npm test` passa

## Checklist

- [x] Endurecer `identity-resolver` para distinguir melhor identidade resolvida, ambigua e nao encontrada
- [x] Introduzir classificacao explicita de perfil de candidato no modelo de dominio
- [x] Ajustar `query-orchestrator` para interromper coleta em caso de ambiguidade forte com mensagem acionavel
- [x] Ajustar `collection-planner` para perfis `incumbent`, `former` e `challenger`
- [x] Cobrir cenarios negativos e de desambiguacao com testes dedicados
- [x] Validar o CLI com caso representativo de identidade resolvida e preservar metadados explicitos para ambiguidade via testes automatizados
- [x] Validar quality gates

## File List

- [x] `packages/memoria-civica/src/domain/models.ts`
- [x] `packages/memoria-civica/src/contracts/consultation.ts`
- [x] `packages/memoria-civica/src/services/response-assembler.ts`
- [x] `packages/memoria-civica/src/services/identity-resolver.ts`
- [x] `packages/memoria-civica/src/services/query-orchestrator.ts`
- [x] `packages/memoria-civica/src/services/collection-planner.ts`
- [x] `packages/memoria-civica/src/source-connectors/mcp-brasil.ts`
- [x] `tests/identity-resolver.test.ts`
- [x] `tests/query-orchestrator.test.ts`
- [x] `tests/collection-planner.test.ts`
- [x] `tests/mcp-brasil-source.test.ts`

## Validation Evidence

- [x] `2026-03-31`: `npm run lint`
- [x] `2026-03-31`: `npm run typecheck`
- [x] `2026-03-31`: `npm test`
- [x] `2026-03-31`: `npm run consultar-candidato -- --candidate 'Tabata Amaral' --office deputado_federal --uf sp`
