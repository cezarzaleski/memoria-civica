---
title: V1 Fase 2 - Coherence Incremental via Camara
status: Done
date: 2026-04-01
owner: dev
---

# Story

Expandir `coherence` para incumbentes federais com base em blocos oficiais da Camara, mantendo uma regra conservadora e auditavel por cobertura estrutural, sem inferencia editorial nem score politico opaco.

## Acceptance Criteria

- [x] `collection-planner` adiciona uma trilha explicita de votacoes nominais recentes da Camara para incumbentes quando `coherence` e solicitado
- [x] o conector `mcp-brasil` coleta `voting_summary` apenas quando encontra participacao nominal do deputado nas votacoes recentes consultadas
- [x] `signal-engine` passa a avaliar `coherence` por cobertura de blocos oficiais distintos da Camara, e nao por contagem cega de evidencias textuais
- [x] o alerta do `query-orchestrator` reflete a nova realidade: atuacao formal e votos nominais recentes entram, mas autoria, relatoria e proposicoes por deputado continuam fora
- [x] testes cobrem planner, conector, `signal-engine` e regressao do `query-orchestrator`
- [x] `npm run lint` passa
- [x] `npm run typecheck` passa
- [x] `npm test` passa

## Checklist

- [x] Adicionar objetivo `coletar_votacoes_nominais` para incumbentes na trilha da Camara
- [x] Implementar coleta minima de votacoes nominais recentes no conector `mcp-brasil`
- [x] Limitar o coletor a um numero pequeno de votacoes recentes para manter o fluxo responsivo
- [x] Identificar o deputado por nome canonico e aliases antes de produzir `voting_summary`
- [x] Ajustar `signal-engine` para promover `coherence` apenas quando houver dois blocos oficiais distintos
- [x] Atualizar o alerta de limitacao do `query-orchestrator`
- [x] Registrar que `propositions_summary` foi adiado por falta de vinculo confiavel por autor no contrato atual do `mcp-brasil`
- [x] Validar quality gates e smoke test do CLI

## File List

- [x] `packages/memoria-civica/src/services/collection-planner.ts`
- [x] `packages/memoria-civica/src/source-connectors/mcp-brasil.ts`
- [x] `packages/memoria-civica/src/services/signal-engine.ts`
- [x] `packages/memoria-civica/src/services/query-orchestrator.ts`
- [x] `tests/collection-planner.test.ts`
- [x] `tests/mcp-brasil-source.test.ts`
- [x] `tests/signal-engine.test.ts`
- [x] `tests/query-orchestrator.test.ts`
- [x] `docs/plans/2026-04-01-coherence-incremental-design.md`
- [x] `docs/superpowers/plans/2026-04-01-coherence-incremental.md`

## Validation Evidence

- [x] `2026-04-01`: `npm run lint`
- [x] `2026-04-01`: `npm run typecheck`
- [x] `2026-04-01`: `npm test`
- [x] `2026-04-01`: `npm run consultar-candidato -- --candidate 'Tabata Amaral' --office deputado_federal --uf sp`

## Notes

- O smoke test executou a trilha nova de votacoes nominais da Camara com sucesso, mas o caso `Tabata Amaral` ainda nao produziu `voting_summary` no recorte consultado; por isso `coherence` permaneceu `mixed`.
- `propositions_summary` ficou explicitamente fora deste slice porque o contrato atual do `mcp-brasil` nao oferece filtro confiavel por autor/deputado para sustentar essa evidencia com rigor.
