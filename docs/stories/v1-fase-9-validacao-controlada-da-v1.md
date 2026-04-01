---
title: V1 Fase 9 - Validacao controlada da V1
status: Ready for Review
date: 2026-04-01
owner: sm
---

# Story

Executar uma validacao controlada da V1 com casos reais para produzir um parecer claro de viabilidade do projeto, principalmente quanto a dados, comparabilidade e honestidade metodologica, sem reabrir discovery nem inventar novas frentes de produto.

## Acceptance Criteria

- [x] a validacao usa um conjunto pequeno e diverso de casos reais, cobrindo pelo menos: incumbente com historico forte, incumbente controverso, ex-parlamentar ou figura publica com trajetoria conhecida, e desafiante ou nome com cobertura limitada
- [x] para cada caso, a execucao registra: identidade resolvida, fontes testadas, qualidade inicial das evidencias e parecer por sinal (`integrity`, `coherence`, `evidence_level`, `values_fit`)
- [x] o trabalho consolida explicitamente o que e `viavel`, `viavel com cautela`, `parcialmente viavel` e `nao viavel agora` para a V1
- [x] o parecer final explicita a fronteira de comparabilidade entre incumbentes, ex-parlamentares ou figuras com vida parlamentar observavel, e desafiantes
- [x] o resultado inclui criterio claro de quando o produto deve responder `evidencia insuficiente`
- [x] o resultado produz uma nota argumentada de viabilidade da V1, com foco principal em dados e cobertura real das fontes
- [x] os artefatos finais deixam claro o que ja esta pavimentado para continuar construindo e o que ainda precisa de validacao adicional antes de ampliar escopo

## Checklist

- [x] selecionar e congelar a amostra minima de casos reais a partir da matriz de viabilidade e da rodada 1
- [x] executar a bateria de consultas nesses casos com o estado atual da V1
- [x] registrar por caso: identidade, fontes, evidencias, sinais e limitacoes observadas
- [x] consolidar um quadro de comparabilidade entre perfis de candidato
- [x] consolidar um quadro de decisao de escopo: entra, entra com cautela, entra depois, nao entra
- [x] redigir parecer final de viabilidade com foco em dados, metodo e experiencia minima defensavel

## File List

- [x] `docs/rodada-2-validacao-evidencias-v1.md`
- [x] `docs/parecer-viabilidade-v1.md`
- [x] `docs/stories/v1-fase-9-validacao-controlada-da-v1.md`

## Validation Evidence

- [x] `2026-04-01`: execucao documentada da bateria de casos reais da rodada 2 em `docs/rodada-2-validacao-evidencias-v1.md`
- [x] `2026-04-01`: quadro consolidado de sinais por perfil de candidato em `docs/rodada-2-validacao-evidencias-v1.md`
- [x] `2026-04-01`: parecer final de viabilidade da V1 em `docs/parecer-viabilidade-v1.md`

## Notes

- Derivada diretamente de `docs/plano-execucao-matriz-viabilidade-v1.md`, que trata a validacao de evidencia e viabilidade de sinais como frente formal separada de UX e implementacao.
- Usa como base `docs/matriz-viabilidade-dados-evidencias-v1.md`, que explicita que nenhuma funcionalidade entra na V1 apenas porque a fonte existe.
- Continua a trilha iniciada em `docs/rodada-1-validacao-evidencias-v1.md`, mas agora com objetivo de produzir um parecer claro de projeto: o que ja sustenta a V1 e onde ainda falta base real.
- Alinha com o `one-pager`: depois de materializar a watchlist minima, o proximo passo defensavel e testar essa leitura em casos reais antes de ampliar cobertura ou sofisticar o produto.
- O escopo desta story foi alinhado ao handoff operacional e a `docs/rodada-1-validacao-evidencias-v1.md`, que congelam o terceiro perfil como `ex-parlamentar ou figura publica com trajetoria conhecida`.
