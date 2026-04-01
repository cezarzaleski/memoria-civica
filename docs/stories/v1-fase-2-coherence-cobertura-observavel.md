---
title: V1 Fase 2 - Coherence com Cobertura Observavel
status: Done
date: 2026-04-01
owner: dev
---

# Story

Melhorar a auditabilidade de `coherence` para incumbentes federais, expondo no payload quais blocos oficiais da Camara foram coletados e quais ainda faltam, e consolidar `propositions_summary` como bloco estrutural validado localmente para a trilha da Camara.

## Acceptance Criteria

- [x] `signal-engine` descreve `coherence` por blocos coletados e faltantes, em vez de manter apenas uma leitura generica
- [x] `propositions_summary` passa a existir como bloco esperado na cobertura de `coherence`
- [x] `propositions_summary` e validado localmente no coletor da Camara contra o PR `jxnxts/mcp-brasil#4`, sem depender ainda de merge upstream
- [x] `query-orchestrator` expõe alerta explicito com cobertura atual e lacunas da trilha de `coherence`
- [x] testes cobrem cobertura coletada e faltante no `signal-engine` e a regressao do payload final
- [x] smoke test real do CLI mostra `formal_activity_record + propositions_summary` elevando `coherence` para `positive`
- [x] `npm run lint` passa
- [x] `npm run typecheck` passa
- [x] `npm test` passa

## Checklist

- [x] Introduzir lista explicita de blocos esperados para `coherence` da Camara
- [x] Expor blocos coletados e faltantes no `signal-engine`
- [x] Atualizar mensagem de `coherence` para refletir lacunas reais
- [x] Adicionar alerta de cobertura no `query-orchestrator`
- [x] Ativar `coletar_proposicoes_autorais` para incumbentes federais na trilha da Camara
- [x] Integrar `propositions_summary` no conector `mcp-brasil` usando `id_deputado_autor` em validacao local contra o PR upstream
- [x] Cobrir cenarios de cobertura parcial em testes
- [x] Validar quality gates

## File List

- [x] `packages/memoria-civica/src/services/signal-engine.ts`
- [x] `packages/memoria-civica/src/services/collection-planner.ts`
- [x] `packages/memoria-civica/src/services/query-orchestrator.ts`
- [x] `packages/memoria-civica/src/source-connectors/mcp-brasil.ts`
- [x] `tests/collection-planner.test.ts`
- [x] `tests/mcp-brasil-source.test.ts`
- [x] `tests/signal-engine.test.ts`
- [x] `tests/query-orchestrator.test.ts`
- [x] `docs/plans/2026-04-01-relatoria-spike.md`

## Validation Evidence

- [x] `2026-04-01`: `npm run lint`
- [x] `2026-04-01`: `npm run typecheck`
- [x] `2026-04-01`: `npm test`
- [x] `2026-04-01`: `MCP_BRASIL_LOCAL_PATH=/Users/cezar.zaleski/workspace/pessoal/mcp-brasil npm run consultar-candidato -- --candidate 'Tabata Amaral' --office deputado_federal --uf sp`

## Notes

- `propositions_summary` foi validado localmente no Memoria Civica contra o PR [jxnxts/mcp-brasil#4](https://github.com/jxnxts/mcp-brasil/pull/4), sem depender ainda de merge/release upstream.
- O smoke test local com `Tabata Amaral` passou a produzir `formal_activity_record + propositions_summary`, elevando `coherence` para `positive`.
- `relatoria` nao vira story agora. Ela permanece apenas como spike em `docs/plans/2026-04-01-relatoria-spike.md`, porque a trilha oficial parece depender de eventos, pauta, parecer e vinculo indireto com proposicao.
