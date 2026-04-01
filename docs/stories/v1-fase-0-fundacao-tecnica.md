---
title: V1 Fase 0 - Fundacao Tecnica
status: Done
date: 2026-03-29
owner: dev
---

# Story

Implementar a fundacao tecnica da V1 do Memoria Civica e iniciar o nucleo da Fase 1 sem reabrir discovery, tese de produto, watchlist editorial ou discussao regulatoria.

## Acceptance Criteria

- [x] Estrutura minima do projeto criada com `bin/`, `packages/` e `tests/`
- [x] Contratos de entrada e saida da consulta modelados em TypeScript
- [x] Modelo minimo para identidade, evidencias, classificacoes, execucoes e cache definido
- [x] `consulta-entrypoint` funcional em CLI
- [x] `query-orchestrator` com fluxo minimo ponta a ponta
- [x] `identity-resolver` com esqueleto operacional e tratamento de ambiguidade
- [x] `npm run lint` passa
- [x] `npm run typecheck` passa
- [x] `npm test` passa

## Checklist

- [x] Criar base Node/TypeScript do projeto
- [x] Escrever testes para contratos e fluxo inicial
- [x] Implementar modulos da Fase 0
- [x] Iniciar Fase 1 com `identity-resolver`
- [x] Integrar `mcp-brasil` com trilha TSE operacional por `tse_resultado_por_estado` para `deputado_federal` e `deputado_distrital/DF`
- [x] Introduzir `evidence-store` minimo e persistencia de evidencias oficiais no `query-orchestrator`
- [x] Implementar `evidence-classifier` minimo e `signal-engine` para `evidence_level`
- [x] Implementar `integrity` minimo com default honesto em `insufficient`
- [x] Implementar `coherence` minimo apenas para incumbentes federais
- [x] Endurecer `integrity` com screening oficial conservador via Transparencia
- [x] Introduzir `response-assembler` minimo para `traffic_light` e `confidence`
- [x] Substituir proxy de `coherence` por evidencia formal dedicada da Camara
- [x] Explicitar no pipeline a limitacao atual de `coherence` sem autoria, relatoria ou voto nominal por deputado
- [x] Validar quality gates
- [x] Validar o CLI com integracao real de `Camara`, `TSE` e `Transparencia` no ambiente com Zscaler

## File List

- [x] `package.json`
- [x] `package-lock.json`
- [x] `tsconfig.json`
- [x] `eslint.config.js`
- [x] `vitest.config.ts`
- [x] `bin/consultar-candidato.ts`
- [x] `scripts/inspect-mcp-brasil.mjs`
- [x] `scripts/search-mcp-brasil-tools.mjs`
- [x] `scripts/call-mcp-brasil-tool.mjs`
- [x] `packages/memoria-civica/src/index.ts`
- [x] `packages/memoria-civica/src/cli/consulta-entrypoint.ts`
- [x] `packages/memoria-civica/src/contracts/consultation.ts`
- [x] `packages/memoria-civica/src/domain/models.ts`
- [x] `packages/memoria-civica/src/observability/query-execution.ts`
- [x] `packages/memoria-civica/src/services/collection-planner.ts`
- [x] `packages/memoria-civica/src/services/evidence-classifier.ts`
- [x] `packages/memoria-civica/src/services/evidence-store.ts`
- [x] `packages/memoria-civica/src/services/identity-resolver.ts`
- [x] `packages/memoria-civica/src/services/query-orchestrator.ts`
- [x] `packages/memoria-civica/src/services/response-assembler.ts`
- [x] `packages/memoria-civica/src/services/signal-engine.ts`
- [x] `packages/memoria-civica/src/source-connectors/mcp-brasil.ts`
- [x] `packages/memoria-civica/src/source-connectors/tse-identity-strategy.ts`
- [x] `tests/consultation-contracts.test.ts`
- [x] `tests/collection-planner.test.ts`
- [x] `tests/evidence-classifier.test.ts`
- [x] `tests/query-orchestrator.test.ts`
- [x] `tests/response-assembler.test.ts`
- [x] `tests/identity-resolver.test.ts`
- [x] `tests/signal-engine.test.ts`
- [x] `tests/consulta-entrypoint.test.ts`
- [x] `tests/mcp-brasil-source.test.ts`
- [x] `tests/tse-identity-strategy.test.ts`

## Validation Evidence

- [x] `2026-03-31`: `npm run lint`
- [x] `2026-03-31`: `npm run typecheck`
- [x] `2026-03-31`: `npm test`
- [x] `2026-03-31`: `npm run consultar-candidato -- --candidate 'Tabata Amaral' --office deputado_federal --uf sp`
- [x] `2026-03-31`: bootstrap do `mcp-brasil` endurecido com `truststore` para compatibilidade com ambiente corporativo usando Zscaler, mantendo verificacao TLS
