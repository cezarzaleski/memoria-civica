---
title: V1 Fase 8 - Desambiguacao de identidade acionavel
status: Ready for Review
date: 2026-04-01
owner: sm
---

# Story

Tornar a desambiguacao de identidade da V1 mais acionavel e compreensivel para usuario leigo, preservando a regra de parar a consulta quando houver ambiguidade forte, mas transformando a resposta em um proximo passo simples e objetivo para informar `uf` e/ou `party`.

## Acceptance Criteria

- [x] quando houver ambiguidade forte, a resposta continua interrompendo a coleta e nao segue para sinais nem semaforo final
- [x] a saida explicita em linguagem simples que faltou contexto para identificar a pessoa correta, sem jargao tecnico desnecessario
- [x] a resposta informa de forma estruturada quais campos faltam para desambiguar (`uf` e/ou `party`) e preserva os metadados ja existentes de ambiguidade
- [x] o CLI expõe uma mensagem de desambiguacao utilizavel por futuro fluxo PWA/mobile-first, sem depender ainda de interface grafica
- [x] o fluxo continua compativel com a persona da Dona Maria: um proximo passo claro, curto e sem excesso de explicacao visivel de primeira
- [x] testes cobrem pelo menos um caso ambiguo pedindo `uf` e `party`, um caso em que apenas um dos campos baste e um caso resolvido sem ambiguidade
- [x] `npm run lint` passa
- [x] `npm run typecheck` passa
- [x] `npm test` passa

## Checklist

- [x] revisar o contrato de resposta para ambiguidade forte e manter consistencia com o fluxo operacional da consulta
- [x] ajustar a mensagem principal de desambiguacao para linguagem simples e acionavel
- [x] preservar `requires`, `match_count`, `resolution_kind` e demais metadados necessarios para UX futura
- [x] garantir que a execucao continue parando antes da coleta quando a identidade estiver ambigua
- [x] cobrir cenarios de desambiguacao com testes dedicados no orchestrator e no entrypoint
- [x] validar quality gates

## File List

- [x] `packages/memoria-civica/src/services/query-orchestrator.ts`
- [x] `tests/query-orchestrator.test.ts`
- [x] `tests/consulta-entrypoint.test.ts`

## Validation Evidence

- [x] `2026-04-01`: `npm run lint`
- [x] `2026-04-01`: `npm run typecheck`
- [x] `2026-04-01`: `npm test`

## Notes

- Derivada de `docs/fluxo-operacional-consulta-v1.md`, que define: se houver ambiguidade forte de identidade, a consulta nao segue para sinais e deve responder com necessidade de desambiguacao.
- Reaproveita a base ja entregue na `v1-fase-1`, mas muda o foco de robustez interna para clareza de proximo passo para usuario leigo.
- Alinha a experiencia futura do PWA para Dona Maria sem abrir ainda uma implementacao de UI: primeiro o contrato e a mensagem precisam estar certos.
- Mantem a regra da Constitution `CLI First -> Observability Second -> UI Third`.
