---
title: Indice Mestre da V1
date: 2026-03-28
status: draft
---

# Indice Mestre da V1

## 1. Objetivo

Organizar os documentos produzidos ate aqui para que eles possam ser usados como contexto por proximos agentes, sem perder foco nem duplicar trabalho.

## 2. Como Ler Este Indice

Cada documento esta classificado por:

- papel
- prioridade
- quando usar
- quem pode usar

## 3. Documentos Canonicos

Esses sao os documentos-base da V1. Sao os primeiros que um proximo agente deve ler.

### 3.1 Discovery do Produto

Arquivo:

- [memoria-civica-2026-discovery.md](/Users/cezar.zaleski/workspace/pessoal/memoria_civica/docs/memoria-civica-2026-discovery.md)

Papel:

- tese do produto
- promessa
- publico
- direcao da V1
- riscos e distribuicao

Quando usar:

- qualquer agente que precise entender o que o produto e

### 3.2 Matriz de Viabilidade

Arquivo:

- [matriz-viabilidade-dados-evidencias-v1.md](/Users/cezar.zaleski/workspace/pessoal/memoria_civica/docs/matriz-viabilidade-dados-evidencias-v1.md)

Papel:

- define o que e defensavel em dados e evidencias

Quando usar:

- agentes de dados
- agentes de arquitetura
- agentes de produto

### 3.3 Arquitetura Minima de Sinais

Arquivo:

- [arquitetura-minima-sinais-v1.md](/Users/cezar.zaleski/workspace/pessoal/memoria_civica/docs/arquitetura-minima-sinais-v1.md)

Papel:

- define a logica dos sinais da V1

Quando usar:

- agentes de sistema
- agentes de implementacao
- agentes de produto

### 3.4 Fluxo Operacional da Consulta

Arquivo:

- [fluxo-operacional-consulta-v1.md](/Users/cezar.zaleski/workspace/pessoal/memoria_civica/docs/fluxo-operacional-consulta-v1.md)

Papel:

- mostra como a consulta deve funcionar ponta a ponta

Quando usar:

- agentes de backend
- agentes de arquitetura
- agentes de UX funcional

## 4. Documentos Estruturantes

Esses documentos refinam partes criticas da V1.

### 4.1 Arquitetura da Watchlist Tematica

Arquivo:

- [arquitetura-watchlist-tematica-v1.md](/Users/cezar.zaleski/workspace/pessoal/memoria_civica/docs/arquitetura-watchlist-tematica-v1.md)
- [watchlist-tematica-v1-rascunho.md](/Users/cezar.zaleski/workspace/pessoal/memoria_civica/docs/watchlist-tematica-v1-rascunho.md)
- [watchlist-tematica-v1-operacional.md](/Users/cezar.zaleski/workspace/pessoal/memoria_civica/docs/watchlist-tematica-v1-operacional.md)
- [teste-watchlist-rodada-1.md](/Users/cezar.zaleski/workspace/pessoal/memoria_civica/docs/teste-watchlist-rodada-1.md)
- [taxonomia-alertas-corrupcao-transparencia-v1.md](/Users/cezar.zaleski/workspace/pessoal/memoria_civica/docs/taxonomia-alertas-corrupcao-transparencia-v1.md)
- [taxonomia-economia-custo-vida-v1.md](/Users/cezar.zaleski/workspace/pessoal/memoria_civica/docs/taxonomia-economia-custo-vida-v1.md)

Papel:

- define a camada editorial de aderencia a valores
- materializa temas, exemplos e taxonomias iniciais

Quando usar:

- agentes editoriais
- agentes de produto
- agentes de interpretacao tematica

### 4.2 Arquitetura de Coleta Sistemica

Arquivo:

- [arquitetura-coleta-sistemica-evidencias-v1.md](/Users/cezar.zaleski/workspace/pessoal/memoria_civica/docs/arquitetura-coleta-sistemica-evidencias-v1.md)

Papel:

- define o que pode ser coletado de forma repetivel

Quando usar:

- agentes de dados
- agentes de backend
- agentes de integracao

### 4.3 Stack de Dados Recomendado

Arquivo:

- [stack-dados-recomendado-v1.md](/Users/cezar.zaleski/workspace/pessoal/memoria_civica/docs/stack-dados-recomendado-v1.md)

Papel:

- define MCPs, APIs e fontes recomendadas

Quando usar:

- agentes de integracao
- agentes tecnicos
- agentes de arquitetura

### 4.4 Mapa de Arquitetura do Sistema

Arquivo:

- [mapa-arquitetura-sistema-v1.md](/Users/cezar.zaleski/workspace/pessoal/memoria_civica/docs/mapa-arquitetura-sistema-v1.md)

Papel:

- conecta todos os componentes logicos da V1

Quando usar:

- agentes de arquitetura
- agentes de implementacao
- agentes de consolidacao

## 5. Documentos de Execucao e Evidencia

Esses documentos mostram trabalho executado ou como executar.

### 5.1 Plano de Execucao da Matriz

Arquivo:

- [plano-execucao-matriz-viabilidade-v1.md](/Users/cezar.zaleski/workspace/pessoal/memoria_civica/docs/plano-execucao-matriz-viabilidade-v1.md)

Papel:

- define como executar a validacao de evidencias

Quando usar:

- agentes exploradores
- agentes de discovery

### 5.2 Rodada 1 de Validacao

Arquivo:

- [rodada-1-validacao-evidencias-v1.md](/Users/cezar.zaleski/workspace/pessoal/memoria_civica/docs/rodada-1-validacao-evidencias-v1.md)

Papel:

- mostra a primeira validacao concreta com nomes reais

Quando usar:

- agentes que precisam de exemplos reais
- agentes que vao evoluir metodologia

## 6. Ordem Recomendada de Leitura por Tipo de Agente

### 6.1 Agente de Produto

Ler nesta ordem:

1. `memoria-civica-2026-discovery.md`
2. `matriz-viabilidade-dados-evidencias-v1.md`
3. `arquitetura-watchlist-tematica-v1.md`
4. `rodada-1-validacao-evidencias-v1.md`

### 6.2 Agente de Arquitetura

Ler nesta ordem:

1. `memoria-civica-2026-discovery.md`
2. `arquitetura-minima-sinais-v1.md`
3. `arquitetura-coleta-sistemica-evidencias-v1.md`
4. `stack-dados-recomendado-v1.md`
5. `fluxo-operacional-consulta-v1.md`
6. `mapa-arquitetura-sistema-v1.md`

### 6.3 Agente de Dados e Integracao

Ler nesta ordem:

1. `matriz-viabilidade-dados-evidencias-v1.md`
2. `arquitetura-coleta-sistemica-evidencias-v1.md`
3. `stack-dados-recomendado-v1.md`
4. `rodada-1-validacao-evidencias-v1.md`

### 6.4 Agente Editorial

Ler nesta ordem:

1. `memoria-civica-2026-discovery.md`
2. `arquitetura-watchlist-tematica-v1.md`
3. `watchlist-tematica-v1-rascunho.md`
4. `watchlist-tematica-v1-operacional.md`
5. `teste-watchlist-rodada-1.md`
6. `taxonomia-alertas-corrupcao-transparencia-v1.md`
7. `taxonomia-economia-custo-vida-v1.md`
8. `rodada-1-validacao-evidencias-v1.md`

### 6.5 Agente Juridico ou Regulatorio

Ler nesta ordem:

1. `memoria-civica-2026-discovery.md`
2. `matriz-viabilidade-dados-evidencias-v1.md`
3. `rodada-1-validacao-evidencias-v1.md`

## 7. Regra de Uso Como Contexto

Nenhum proximo agente precisa ler todos os arquivos.

O correto e:

- carregar apenas os documentos necessarios para a tarefa;
- usar o discovery como ancora;
- usar os demais como especializacao por frente.

## 8. Estado Atual

O estado atual do projeto, em termos de definicao da V1, pode ser resumido assim:

- tese do produto definida
- fronteiras da V1 definidas
- sinais minimos definidos
- coleta sistemica parcialmente mapeada
- rodada inicial de validacao executada
- camada editorial iniciada, com dois temas mais maduros

## 9. Proximo Uso Recomendado

Se um novo agente for trabalhar agora, o melhor uso deste indice e:

- escolher a frente
- carregar apenas os documentos daquela frente
- produzir o proximo artefato sem reabrir decisoes ja tomadas
