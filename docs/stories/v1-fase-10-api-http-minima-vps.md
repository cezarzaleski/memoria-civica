---
title: V1 Fase 10 - API HTTP minima para consulta na VPS
status: Ready
date: 2026-04-01
owner: architect
---

# Story

Expor o motor atual do Memoria Civica como uma API HTTP minima, stateless e sem autenticacao, preparada para rodar na VPS e servir a primeira versao web do produto sem alterar a logica central da consulta.

## Acceptance Criteria

- [ ] existe um endpoint `POST /consultas` que recebe o contrato minimo da consulta (`candidate_name`, `uf`, `party`, `user_priorities`)
- [ ] o endpoint reaproveita o `QueryOrchestrator` e retorna o mesmo payload funcional ja validado no CLI, sem inventar uma segunda semantica de resposta
- [ ] o backend retorna erros de validacao em formato HTTP legivel e consistente, sem stack trace no payload
- [ ] a aplicacao sobe localmente em porta configuravel por `env`
- [ ] existe endpoint simples de saude (`GET /health`) para deploy e smoke test
- [ ] a implementacao permanece sem banco, sem fila e sem autenticacao
- [ ] a story documenta as variaveis de ambiente minimas para rodar na VPS
- [ ] testes cobrem pelo menos: `health`, consulta valida, erro de validacao e repasse correto do payload de ambiguidade
- [ ] `npm run lint` passa
- [ ] `npm run typecheck` passa
- [ ] `npm test` passa

## Checklist

- [ ] criar `apps/api` com servidor HTTP minimo em TypeScript
- [ ] plugar o motor atual da consulta no endpoint HTTP
- [ ] preservar o contrato funcional ja estabilizado no CLI
- [ ] definir tratamento minimo de erro e serializacao JSON
- [ ] adicionar configuracao por `PORT` e `HOST`
- [ ] documentar execucao local e requisitos de `env`
- [ ] cobrir o fluxo com testes automatizados
- [ ] validar quality gates

## File List

- [ ] `apps/api/package.json`
- [ ] `apps/api/src/server.ts`
- [ ] `apps/api/src/routes/consultas.ts`
- [ ] `apps/api/src/routes/health.ts`
- [ ] `apps/api/src/app.ts`
- [ ] `package.json`
- [ ] `tests/api-health.test.ts`
- [ ] `tests/api-consultas.test.ts`

## Validation Evidence

- [ ] `2026-04-01`: `npm run lint`
- [ ] `2026-04-01`: `npm run typecheck`
- [ ] `2026-04-01`: `npm test`

## Notes

- Esta fase nao introduce Nest. A prioridade aqui e abrir uma borda HTTP simples sobre o core ja existente.
- O deploy alvo e uma VPS propria, com processo unico e sem dependencia de infraestrutura adicional.
- O contrato da API deve permanecer alinhado ao fluxo operacional ja validado no CLI e nas stories anteriores.
