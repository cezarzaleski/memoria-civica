---
title: Taxonomia de Alertas - Corrupcao e Transparencia V1
date: 2026-03-28
status: draft
---

# Taxonomia de Alertas - Corrupcao e Transparencia V1

## 1. Objetivo

Definir uma taxonomia simples e publica para o tema `Corrupcao e Transparencia`, de modo que o produto consiga classificar alertas sem exagerar a interpretacao.

## 2. Regra Central

O produto nao deve dizer que alguem e corrupto.

O produto deve dizer apenas:

- se ha alerta oficial relevante;
- qual o tipo do alerta;
- qual o nivel do alerta;
- e qual a confianca dessa leitura.

## 3. Niveis de Alerta

### 3.1 Sem alerta relevante observado

Usar quando:

- nao houver sancao formal relevante encontrada;
- nao houver problema oficial forte identificado na rodada;
- ou houver apenas trilha administrativa sem irregularidade formal.

Exemplos:

- existencia de emendas e empenhos rastreaveis
- representacao analisada sem indicios suficientes

### 3.2 Alerta moderado

Usar quando:

- houver sancao eleitoral formal sem gravidade maxima;
- houver contas com ressalvas;
- houver determinacao oficial de ajuste, recolhimento ou correcao sem desfecho mais grave;
- houver problema formal que exige cautela, mas nao sustenta leitura maxima.

Exemplos:

- multa eleitoral formal
- contas aprovadas com ressalvas
- recolhimento ao Tesouro por falha formal em contas

### 3.3 Alerta relevante

Usar quando:

- houver desfecho oficial mais forte, com irregularidade formal robusta;
- houver contas desaprovadas;
- houver sancao administrativa ou eleitoral de maior peso;
- houver acordao nominal com conclusao materialmente mais grave.

Exemplos:

- contas desaprovadas
- acordao com contas irregulares
- sancao formal relevante em base oficial

### 3.4 Alerta grave

Este nivel so deve existir na V1 se houver base oficial muito clara e risco baixo de erro.

Usar apenas quando:

- houver desfecho oficial nominal, grave e inequivoco;
- a identidade estiver plenamente resolvida;
- a categoria juridica puder ser explicada ao usuario comum sem distorcao.

Observacao:

Se houver duvida entre `relevante` e `grave`, usar `relevante`.

## 4. Tipos de Evidencia por Categoria

| Evidencia | Categoria sugerida | Observacao |
|---|---|---|
| Representacao sem indicios suficientes | sem alerta relevante observado | nao penalizar automaticamente |
| Trilhas de emenda ou empenho sem irregularidade | sem alerta relevante observado | transparencia nao e culpa |
| Multa eleitoral formal | alerta moderado | nao equiparar a crime |
| Contas com ressalvas | alerta moderado | explicar natureza da ressalva |
| Recolhimento ao Tesouro por falha formal | alerta moderado ou relevante | depende do contexto e do peso do caso |
| Contas desaprovadas | alerta relevante | categoria mais forte que ressalva |
| Acordao com contas irregulares | alerta relevante | confirmar identidade e contexto |
| Sancao formal grave e inequivoca | alerta grave | usar com extrema cautela |

## 5. Tipos de Evidencia que Nao Mudam o Nivel Sozinhos

- materia jornalistica
- mencao em busca textual sem contexto
- valor alto de emenda
- volume de gasto
- acusacao sem desfecho oficial

Esses itens podem:

- contextualizar
- motivar revisao
- ou reforcar uma leitura ja sustentada por fonte oficial

Mas nao devem elevar sozinhos o alerta.

## 6. Regra de Confianca

### 6.1 Confianca alta

Quando houver:

- documento oficial nominal;
- desfecho formal claro;
- identidade resolvida sem ambiguidade.

### 6.2 Confianca media

Quando houver:

- base oficial suficiente;
- mas interpretacao ainda dependente de contexto juridico simples.

### 6.3 Confianca baixa

Quando houver:

- ocorrencia oficial incompleta;
- mencao indireta;
- duvida relevante de enquadramento.

## 7. Regra de Linguagem Publica

### 7.1 Frases recomendadas

- encontramos um alerta oficial moderado
- ha ressalvas formais nas contas
- houve sancao eleitoral formal
- nao encontramos alerta oficial robusto nesta rodada
- encontramos trilha oficial, mas sem irregularidade formal confirmada

### 7.2 Frases a evitar

- corrupto
- roubou
- ficha suja
- criminoso
- desonesto

## 8. Aplicacao nos casos da rodada 1

### 8.1 Nikolas Ferreira

- evidencia: multa eleitoral formal no TSE
- leitura: `alerta moderado`

### 8.2 Fred Linhares

- evidencia: contas aprovadas com ressalvas e recolhimento ao Tesouro
- leitura: `alerta moderado`, podendo subir para `relevante` se a politica final decidir que recolhimento formal pesa mais

### 8.3 Erika Hilton

- evidencia: representacao formal sem indicios suficientes
- leitura: `sem alerta relevante observado`

### 8.4 Ricardo Cappelli

- evidencia: trilha oficial auditavel sem red flag formal forte na rodada
- leitura: `sem alerta relevante observado`

## 9. Regra de Produto

Na V1, o produto deve preferir errar por prudencia.

Isso significa:

- subir o nivel de alerta devagar;
- nunca usar linguagem condenatoria;
- e assumir `evidencia insuficiente` quando a classificacao nao estiver clara.

## 10. Decisao Estrategica

Esta taxonomia ja parece suficiente para a primeira versao do tema `Corrupcao e Transparencia`.

Se for preciso simplificar mais, a V1 pode operar com apenas tres estados publicos:

- sem alerta relevante observado
- alerta moderado
- alerta relevante

E manter `grave` apenas como categoria interna reservada para casos muito claros.
