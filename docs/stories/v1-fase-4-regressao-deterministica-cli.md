---
title: V1 Fase 4 - Regressao deterministica do fluxo CLI
status: Done
date: 2026-04-01
owner: dev
---

# Story

Endurecer o fluxo principal do CLI com um teste de regressao deterministico que trave o contrato de resposta para incumbente federal, sem depender do `mcp-brasil` externo.

## Acceptance Criteria

- [x] o teste do CLI cobre um caso deterministico de incumbente federal
- [x] o payload validado inclui `candidate`, `signals`, `observability.coherence`, `traffic_light` e `summary`
- [x] o `stderr` continua expondo o trace operacional do run
- [x] o teste nao depende de rede nem do `mcp-brasil` externo
- [x] `npm run lint` passa
- [x] `npm run typecheck` passa
- [x] `npm test` passa

## Checklist

- [x] enriquecer o teste do entrypoint com um payload deterministico completo
- [x] travar a serializacao do bloco `observability.coherence`
- [x] travar o trace escrito em `stderr`
- [x] validar quality gates

## File List

- [x] `tests/consulta-entrypoint.test.ts`

## Validation Evidence

- [x] `2026-04-01`: `npm run lint`
- [x] `2026-04-01`: `npm run typecheck`
- [x] `2026-04-01`: `npm test`

## Notes

- O teste do CLI agora trava um caso deterministico rico de incumbente federal com `observability.coherence` e `trace` em `stderr`.
- Foi adicionado tambem um caso deterministico `gray` para garantir que a ausencia de evidencias nao introduz `observability` indevida no payload.
