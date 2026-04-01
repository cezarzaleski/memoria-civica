---
title: V1 Fase 10 - API HTTP minima para consulta na VPS
status: Ready for Review
date: 2026-04-01
owner: architect
---

# Story

Expor o motor atual do Memoria Civica como uma API HTTP minima, stateless e sem autenticacao, preparada para rodar na VPS e servir a primeira versao web do produto sem alterar a logica central da consulta.

## Acceptance Criteria

- [x] existe um endpoint `POST /consultas` que recebe o contrato minimo da consulta (`candidate_name`, `uf`, `party`, `user_priorities`)
- [x] o endpoint reaproveita o `QueryOrchestrator` e retorna o mesmo payload funcional ja validado no CLI, sem inventar uma segunda semantica de resposta
- [x] o backend retorna erros de validacao em formato HTTP legivel e consistente, sem stack trace no payload
- [x] a aplicacao sobe localmente em porta configuravel por `env`
- [x] existe endpoint simples de saude (`GET /health`) para deploy e smoke test
- [x] a implementacao permanece sem banco, sem fila e sem autenticacao
- [x] a story documenta as variaveis de ambiente minimas para rodar na VPS
- [x] testes cobrem pelo menos: `health`, consulta valida, erro de validacao e repasse correto do payload de ambiguidade
- [x] `npm run lint` passa
- [x] `npm run typecheck` passa
- [x] `npm test` passa

## Checklist

- [x] criar `apps/api` com servidor HTTP minimo em TypeScript
- [x] plugar o motor atual da consulta no endpoint HTTP
- [x] preservar o contrato funcional ja estabilizado no CLI
- [x] definir tratamento minimo de erro e serializacao JSON
- [x] adicionar configuracao por `PORT` e `HOST`
- [x] documentar execucao local e requisitos de `env`
- [x] cobrir o fluxo com testes automatizados
- [x] validar quality gates

## File List

- [x] `apps/api/package.json`
- [x] `apps/api/README.md`
- [x] `apps/api/src/server.ts`
- [x] `apps/api/src/routes/consultas.ts`
- [x] `apps/api/src/routes/health.ts`
- [x] `apps/api/src/app.ts`
- [x] `package.json`
- [x] `tsconfig.json`
- [x] `tests/api-health.test.ts`
- [x] `tests/api-consultas.test.ts`

## Validation Evidence

- [x] `2026-04-01`: `npm run lint`
- [x] `2026-04-01`: `npm run typecheck`
- [x] `2026-04-01`: `npm test`

## Notes

- Esta fase nao introduce Nest. A prioridade aqui e abrir uma borda HTTP simples sobre o core ja existente.
- O deploy alvo e uma VPS propria, com processo unico e sem dependencia de infraestrutura adicional.
- O contrato da API deve permanecer alinhado ao fluxo operacional ja validado no CLI e nas stories anteriores.
