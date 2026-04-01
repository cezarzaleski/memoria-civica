---
title: Handoff Operacional - V1 Fase 9 Validacao Controlada
date: 2026-04-01
status: ready
---

# Handoff Operacional - V1 Fase 9

## Objetivo

Executar uma rodada controlada de validacao da V1 para responder, com base em casos reais, se o projeto ja e viavel principalmente quanto a dados, comparabilidade e honestidade metodologica.

## Story alvo

- [v1-fase-9-validacao-controlada-da-v1.md](/Users/cezar.zaleski/workspace/pessoal/memoria_civica/docs/stories/v1-fase-9-validacao-controlada-da-v1.md)

## Artefatos-base obrigatorios

- [matriz-viabilidade-dados-evidencias-v1.md](/Users/cezar.zaleski/workspace/pessoal/memoria_civica/docs/matriz-viabilidade-dados-evidencias-v1.md)
- [plano-execucao-matriz-viabilidade-v1.md](/Users/cezar.zaleski/workspace/pessoal/memoria_civica/docs/plano-execucao-matriz-viabilidade-v1.md)
- [rodada-1-validacao-evidencias-v1.md](/Users/cezar.zaleski/workspace/pessoal/memoria_civica/docs/rodada-1-validacao-evidencias-v1.md)
- [one-pager-produto-v1.md](/Users/cezar.zaleski/workspace/pessoal/memoria_civica/docs/one-pager-produto-v1.md)

## Casos congelados da rodada 2

Usar a mesma diversidade defendida nos artefatos anteriores:

1. incumbente com historico forte
2. incumbente controverso
3. ex-parlamentar ou figura publica com trajetoria conhecida
4. desafiante ou nome com cobertura limitada

## Perguntas que a rodada precisa fechar

1. Para quais perfis de candidato a V1 ja e defensavel hoje?
2. Onde a comparabilidade entre perfis deixa de ser justa?
3. Em quais cenarios o produto deve responder `evidencia insuficiente`?
4. O `values_fit` minimo se sustenta em casos reais ou ainda entra com cautela?
5. Qual nota argumentada de viabilidade a V1 merece hoje, principalmente em dados?

## Sequencia recomendada

### Etapa 1: Congelar a amostra

- confirmar os 4 casos reais da rodada
- registrar por que cada caso entrou
- impedir troca de casos no meio da execucao sem justificativa escrita

### Etapa 2: Rodar a bateria

Para cada caso:

- registrar identidade resolvida
- registrar fontes consultadas
- registrar qualidade inicial da evidencia
- registrar leitura por sinal:
  - `integrity`
  - `coherence`
  - `evidence_level`
  - `values_fit`

### Etapa 3: Consolidar comparabilidade

Responder explicitamente:

- incumbente vs incumbente
- incumbente vs ex-parlamentar
- incumbente vs desafiante
- ex-parlamentar vs desafiante

## Saidas obrigatorias

1. [rodada-2-validacao-evidencias-v1.md](/Users/cezar.zaleski/workspace/pessoal/memoria_civica/docs/rodada-2-validacao-evidencias-v1.md)
2. [parecer-viabilidade-v1.md](/Users/cezar.zaleski/workspace/pessoal/memoria_civica/docs/parecer-viabilidade-v1.md)

## Estrutura minima do parecer final

O parecer final deve conter:

1. nota de viabilidade da V1
2. justificativa principal focada em dados
3. o que ja esta pavimentado
4. o que ainda e parcial ou fraco
5. o que nao deve entrar agora
6. recomendacao de backlog apos a validacao

## Definicao de pronto

A `v1-fase-9` so pode ser considerada pronta quando:

1. a rodada 2 estiver documentada por caso real
2. houver quadro consolidado de comparabilidade
3. houver quadro de decisao de escopo:
   - entra
   - entra com cautela
   - entra depois
   - nao entra
4. o parecer final responder claramente se o projeto e viavel hoje e com quais limites

## Papel dos agentes

- `@sm`: garante escopo, checklist e definicao de pronto
- `@dev`: executa a bateria e registra comportamento real do sistema
- `@pm`: fecha leitura de valor e implicacoes de produto
- `@qa`: revisa a consistencia do parecer final

## Regra de ouro

Esta frente nao existe para provar que o produto vai dar certo.

Ela existe para descobrir, de forma documentada e defensavel, o quanto ele ja se sustenta hoje.
