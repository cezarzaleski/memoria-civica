---
title: V1 Fase 2 - Observabilidade final da trilha Camara
status: Done
date: 2026-04-01
owner: dev
---

# Story

Consolidar a observabilidade da trilha de `coherence` da Camara para incumbentes federais, expondo no payload o estado estruturado da cobertura oficial sem depender apenas de alertas textuais.

## Acceptance Criteria

- [x] a resposta final expõe um bloco estruturado de observabilidade para `coherence` da Camara
- [x] o bloco informa tipos esperados, coletados, faltantes e a base do status atual
- [x] o payload continua preservando os alertas textuais para leitura humana
- [x] testes cobrem a nova estrutura de observabilidade no assembler e no orchestrator
- [x] `npm run lint` passa
- [x] `npm run typecheck` passa
- [x] `npm test` passa

## Checklist

- [x] adicionar tipo de observabilidade ao contrato de resposta
- [x] montar observabilidade estruturada no `query-orchestrator`
- [x] manter coerencia entre observabilidade estruturada e alertas textuais
- [x] cobrir cenarios elegiveis e nao elegiveis em testes
- [x] validar quality gates

## File List

- [x] `packages/memoria-civica/src/domain/models.ts`
- [x] `packages/memoria-civica/src/services/query-orchestrator.ts`
- [x] `packages/memoria-civica/src/services/response-assembler.ts`
- [x] `tests/query-orchestrator.test.ts`
- [x] `tests/response-assembler.test.ts`

## Validation Evidence

- [x] `2026-04-01`: `npm run lint`
- [x] `2026-04-01`: `npm run typecheck`
- [x] `2026-04-01`: `npm test`

## Notes

- O payload agora expõe `observability.coherence` com `expected_types`, `collected_types`, `missing_types`, `collected_evidence_ids`, `scope`, `status_basis` e `limitation`.
- Os alertas textuais foram mantidos para leitura humana e continuam coerentes com a observabilidade estruturada.
