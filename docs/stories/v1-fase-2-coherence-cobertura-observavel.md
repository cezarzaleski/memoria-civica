---
title: V1 Fase 2 - Coherence com Cobertura Observavel
status: Done
date: 2026-04-01
owner: dev
---

# Story

Melhorar a auditabilidade de `coherence` para incumbentes federais, expondo no payload quais blocos oficiais da Camara foram coletados e quais ainda faltam, enquanto `propositions_summary` permanece preparado como proximo bloco estrutural do sinal.

## Acceptance Criteria

- [x] `signal-engine` descreve `coherence` por blocos coletados e faltantes, em vez de manter apenas uma leitura generica
- [x] `propositions_summary` passa a existir como bloco esperado na cobertura de `coherence`, sem ativacao prematura no coletor
- [x] `query-orchestrator` expõe alerta explicito com cobertura atual e lacunas da trilha de `coherence`
- [x] testes cobrem cobertura coletada e faltante no `signal-engine` e a regressao do payload final
- [x] `npm run lint` passa
- [x] `npm run typecheck` passa
- [x] `npm test` passa

## Checklist

- [x] Introduzir lista explicita de blocos esperados para `coherence` da Camara
- [x] Expor blocos coletados e faltantes no `signal-engine`
- [x] Atualizar mensagem de `coherence` para refletir lacunas reais
- [x] Adicionar alerta de cobertura no `query-orchestrator`
- [x] Cobrir cenarios de cobertura parcial em testes
- [x] Validar quality gates

## File List

- [x] `packages/memoria-civica/src/services/signal-engine.ts`
- [x] `packages/memoria-civica/src/services/query-orchestrator.ts`
- [x] `tests/signal-engine.test.ts`
- [x] `tests/query-orchestrator.test.ts`

## Validation Evidence

- [x] `2026-04-01`: `npm run lint`
- [x] `2026-04-01`: `npm run typecheck`
- [x] `2026-04-01`: `npm test`
