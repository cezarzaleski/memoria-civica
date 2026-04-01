---
title: V1 Fase 6 - Review queue para casos ambiguos e sensiveis
status: Ready for Review
date: 2026-04-01
owner: dev
---

# Story

Introduzir uma `review-queue` minima no Memoria Civica para marcar consultas que exigem revisao humana ou editorial por sensibilidade de integridade, ambiguidade de identidade ou uso excepcional de evidencias complementares, sem bloquear o fluxo principal nem alterar a regra de `CLI First`.

## Acceptance Criteria

- [x] a execucao registra de forma estruturada quando um caso deve ir para `review-queue`
- [x] a marcacao cobre pelo menos tres gatilhos ja previstos nos artefatos: ambiguidade de identidade, caso sensivel de integridade e uso de jornalismo complementar
- [x] o payload funcional da consulta continua sendo retornado normalmente, com a revisao tratada como observabilidade ou metadado operacional
- [x] os motivos de revisao ficam auditaveis e legiveis para uso humano posterior
- [x] testes cobrem ao menos um caso para cada gatilho de revisao
- [x] `npm run lint` passa
- [x] `npm run typecheck` passa
- [x] `npm test` passa

## Checklist

- [x] definir o contrato minimo da `review-queue` no dominio ou camada de observabilidade
- [x] plugar a marcacao de revisao no fluxo do `query-orchestrator`
- [x] registrar motivos estruturados para `identity_ambiguity`, `integrity_sensitive_case` e `complementary_journalism`
- [x] preservar o comportamento funcional atual da resposta
- [x] cobrir a nova trilha em testes unitarios
- [x] validar quality gates

## File List

- [x] `packages/memoria-civica/src/domain/models.ts`
- [x] `packages/memoria-civica/src/observability/query-execution.ts`
- [x] `packages/memoria-civica/src/services/query-orchestrator.ts`
- [x] `tests/query-orchestrator.test.ts`
- [x] `tests/consulta-entrypoint.test.ts`
- [x] `docs/superpowers/plans/2026-04-01-review-queue-casos-sensiveis.md`

## Validation Evidence

- [x] `2026-04-01`: `npm run lint`
- [x] `2026-04-01`: `npm run typecheck`
- [x] `2026-04-01`: `npm test`

## Notes

- Derivada diretamente de `docs/plano-implementacao-v1.md`, que preve `review-queue` na expansao controlada da V1.
- Usa os gatilhos ja descritos em `docs/arquitetura-coleta-sistemica-evidencias-v1.md`: casos sensiveis de integridade, ambiguidade de identidade e jornalismo complementar.
- Mantem a regra `query-first`, `source-backed`, auditavel e frugal: marcar revisao nao substitui nem bloqueia a resposta principal.
