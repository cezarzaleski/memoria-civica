# Plan: Coherence Incremental via Camara

Date: 2026-04-01

## File Map

- `packages/memoria-civica/src/services/collection-planner.ts`
  - adicionar tarefas de coleta de `coherence` para blocos oficiais extras da Camara
- `packages/memoria-civica/src/source-connectors/mcp-brasil.ts`
  - implementar coleta e mapeamento de `voting_summary`
- `packages/memoria-civica/src/services/signal-engine.ts`
  - derivar `coherence` por cobertura de blocos oficiais da Camara
- `tests/collection-planner.test.ts`
  - cobrir novas tarefas para incumbentes
- `tests/mcp-brasil-source.test.ts`
  - cobrir evidencias novas da Camara
- `tests/signal-engine.test.ts`
  - cobrir regras novas de `coherence`

## Tasks

- [x] Mapear ferramentas da Camara no `mcp-brasil` para votacoes e confirmar bloqueio atual para proposicoes por autor
- [x] Escrever testes falhos do `collection-planner` para novas tarefas de `coherence`
- [x] Escrever testes falhos do conector para `voting_summary`
- [x] Escrever testes falhos do `signal-engine` para cobertura de blocos
- [x] Implementar coleta minima no conector
- [x] Implementar planejamento das novas tarefas
- [x] Implementar regra de `coherence` por cobertura de blocos
- [x] Rodar `npm run lint`
- [x] Rodar `npm run typecheck`
- [x] Rodar `npm test`
- [x] Rodar smoke test do CLI para incumbente
