---
title: V1 Fase 1 - Nucleo do MVP
status: Draft
date: 2026-03-31
owner: dev
---

# Story

Endurecer o nucleo do MVP da V1 do Memoria Civica com resolucao de identidade mais confiavel, classificacao explicita do perfil do candidato e fluxo objetivo de desambiguacao, sem reabrir discovery, watchlist editorial ou expandir fontes alem do necessario.

## Acceptance Criteria

- [ ] `identity-resolver` classifica explicitamente o candidato como `incumbent`, `former` ou `challenger`
- [ ] consultas com multiplos matches plausiveis param antes da coleta e retornam pedido objetivo de desambiguacao por `uf` e/ou `party`
- [ ] `query-orchestrator` preserva no payload final o resultado da resolucao de identidade e o nivel de ambiguidade, inclusive em respostas `gray`
- [ ] `collection-planner` escolhe trilha compativel com `incumbent`, `former` e `challenger`
- [ ] casos minimos cobrindo um incumbente da Camara, um nome apenas na trilha TSE e um caso ambiguo ficam cobertos por testes
- [ ] `npm run lint` passa
- [ ] `npm run typecheck` passa
- [ ] `npm test` passa

## Checklist

- [ ] Endurecer `identity-resolver` para distinguir melhor identidade resolvida, ambigua e nao encontrada
- [ ] Introduzir classificacao explicita de perfil de candidato no modelo de dominio
- [ ] Ajustar `query-orchestrator` para interromper coleta em caso de ambiguidade forte com mensagem acionavel
- [ ] Ajustar `collection-planner` para perfis `incumbent`, `former` e `challenger`
- [ ] Cobrir cenarios negativos e de desambiguacao com testes dedicados
- [ ] Validar o CLI com casos representativos de identidade resolvida e ambigua
- [ ] Validar quality gates

## File List

- [ ] `packages/memoria-civica/src/domain/models.ts`
- [ ] `packages/memoria-civica/src/services/identity-resolver.ts`
- [ ] `packages/memoria-civica/src/services/query-orchestrator.ts`
- [ ] `packages/memoria-civica/src/services/collection-planner.ts`
- [ ] `packages/memoria-civica/src/source-connectors/mcp-brasil.ts`
- [ ] `tests/identity-resolver.test.ts`
- [ ] `tests/query-orchestrator.test.ts`
- [ ] `tests/collection-planner.test.ts`
- [ ] `tests/mcp-brasil-source.test.ts`
