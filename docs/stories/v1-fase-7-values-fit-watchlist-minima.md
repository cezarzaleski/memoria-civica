---
title: V1 Fase 7 - values_fit com watchlist minima auditavel
status: Ready for Review
date: 2026-04-01
owner: sm
---

# Story

Materializar a primeira versao operacional de `values_fit` no Memoria Civica usando uma watchlist tematica minima, publica e auditavel, sem reabrir curadoria editorial nem depender de jornalismo ou evidencias fracas como base principal do sinal.

## Acceptance Criteria

- [x] `editorial-config` passa a carregar uma watchlist minima de 3 a 5 temas, usando apenas regras publicas ja documentadas em `docs/arquitetura-watchlist-tematica-v1.md` e `docs/watchlist-tematica-v1-operacional.md`
- [x] prioridades do usuario passam a ser normalizadas apenas para os temas suportados nessa watchlist minima, sem inferir temas fora do conjunto congelado
- [x] `values_fit` deixa de ser sempre `insufficient` quando houver prioridade do usuario compatível com tema congelado e base suficiente de evidencia permitida
- [x] o sinal so sobe acima de `insufficient` quando houver pelo menos um item forte ou combinacao suficiente de itens medios coerentes entre si, conforme a regra de confianca da arquitetura da watchlist
- [x] evidencia fraca, manchete isolada ou jornalismo sem ato formal associado nao carregam `values_fit` sozinhos
- [x] a resposta continua auditavel, com razoes e limitacoes legiveis sobre o tema avaliado, a evidencia aceita e o que ficou de fora
- [x] testes cobrem pelo menos um caso com alinhamento observavel, um caso de aderencia parcial e um caso de evidencia insuficiente no tema
- [x] `npm run lint` passa
- [x] `npm run typecheck` passa
- [x] `npm test` passa

## Checklist

- [x] introduzir `editorial-config` minimo para watchlist tematica da V1
- [x] limitar a watchlist inicial a temas ja documentados e em quantidade compativel com o recorte da V1
- [x] plugar regras de watchlist no calculo de `values_fit`
- [x] normalizar prioridades do usuario apenas para temas suportados
- [x] restringir `values_fit` a tipos de evidencia aceitos pela arquitetura editorial
- [x] preservar `values_fit` como `insufficient` quando a base nao sustentar inferencia honesta
- [x] cobrir os estados `positive` ou `mixed` e `insufficient` com testes dedicados
- [x] validar quality gates

## File List

- [x] `packages/memoria-civica/src/services/editorial-config.ts`
- [x] `packages/memoria-civica/src/services/signal-engine.ts`
- [x] `packages/memoria-civica/src/services/cached-signal-service.ts`
- [x] `packages/memoria-civica/src/services/query-orchestrator.ts`
- [x] `packages/memoria-civica/src/services/response-assembler.ts`
- [x] `tests/signal-engine.test.ts`
- [x] `tests/query-orchestrator.test.ts`

## Validation Evidence

- [x] `2026-04-01`: `npm run lint`
- [x] `2026-04-01`: `npm run typecheck`
- [x] `2026-04-01`: `npm test`

## Notes

- Derivada da `Fase 3: Expansao Controlada` em `docs/plano-implementacao-v1.md`, que preve `values_fit` com regras editoriais ja congeladas.
- Usa a arquitetura em `docs/arquitetura-watchlist-tematica-v1.md`: watchlist pequena, publica, revisavel e explicavel, com evidencia fraca proibida como base principal do sinal.
- O maior valor de produto neste momento vem de aproximar a resposta da promessa da V1 de validar se o candidato representa prioridades do usuario, mantendo a regra metodologica de dizer `evidencia insuficiente` quando a base nao sustenta a inferencia.
- O recorte inicial deve permanecer pequeno e defensavel, alinhado ao `one-pager`: a V1 precisa de uma watchlist enxuta antes de qualquer ampliacao tematica.
