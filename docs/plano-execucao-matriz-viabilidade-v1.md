---
title: Plano de Execucao da Matriz de Viabilidade da V1
date: 2026-03-28
status: draft
---

# Plano de Execucao da Matriz de Viabilidade da V1

## 1. Objetivo

Executar a matriz de viabilidade de dados e evidencias para descobrir, com base em testes reais, quais sinais entram de forma defensavel na V1 do Memoria Civica.

O objetivo nao e construir o produto ainda.

O objetivo e validar:

- quais perguntas do usuario sao realmente respondiveis;
- com quais fontes;
- com qual nivel de confianca;
- para quais tipos de candidato;
- com quais limitacoes.

## 2. Nome da Frente

Nome recomendado:

`Validacao de Evidencia e Viabilidade de Sinais`

Esse trabalho pode ser conduzido por um agente dedicado ou por uma trilha de discovery separada.

## 3. Papel Desse Agente ou Frente

Esse agente nao implementa UX nem pipeline final.

Ele faz:

- teste de fontes;
- teste de cobertura;
- teste de comparabilidade;
- classificacao da forca da evidencia;
- parecer de escopo da V1.

## 4. Entradas

Documentos-base:

- `docs/memoria-civica-2026-discovery.md`
- `docs/matriz-viabilidade-dados-evidencias-v1.md`
- `docs/arquitetura-minima-sinais-v1.md`

Perguntas prioritarias do produto:

- esse candidato me representa?
- ha alertas de integridade?
- ha coerencia entre discurso e historico?
- ha evidencia suficiente para avaliar?
- o historico conhecido se aproxima das prioridades do usuario?

## 5. Saidas Esperadas

### 5.1 Matriz Executada

Versao preenchida com evidencias reais, por sinal e por tipo de candidato.

### 5.2 Parecer por Funcionalidade

- viavel
- viavel com cautela
- parcialmente viavel
- nao viavel agora

### 5.3 Catalogo de Fontes

Para cada fonte:

- o que ela cobre
- quando ela fica disponivel
- que tipo de evidencia ela sustenta
- confiabilidade
- principais lacunas

### 5.4 Regras Operacionais

- quando responder `evidencia insuficiente`
- quando nao comparar
- quando nao usar um sinal
- quando exigir revisao humana

## 6. Etapas de Execucao

### Etapa 1: Selecionar Casos de Teste

Montar um conjunto pequeno, mas diverso, de nomes reais:

- incumbente com historico forte
- incumbente com perfil controverso
- ex-parlamentar ou figura com vida publica conhecida
- candidato ou pre-candidato sem mandato atual

Objetivo:

testar assimetria de cobertura.

### Etapa 2: Testar Resolucao de Identidade

Validar se o sistema consegue resolver corretamente:

- nome
- partido
- UF
- ids por fonte
- homonimos

Objetivo:

evitar erro de pessoa errada antes de qualquer inferencia.

### Etapa 3: Testar Fontes Oficiais

Para cada caso de teste, validar:

- Camara
- TSE
- TCU
- Transparencia
- outras fontes oficiais candidatas

Objetivo:

descobrir cobertura real, nao cobertura presumida.

### Etapa 4: Classificar Forca da Evidencia

Para cada evidencia encontrada, marcar:

- forte oficial
- oficial parcial
- complementar confiavel
- fraca ou declaratoria
- insuficiente

Objetivo:

separar dado existente de dado realmente util.

### Etapa 5: Testar Cada Sinal

Executar, para cada caso:

- integridade
- coerencia
- nivel de evidencia
- aderencia a valores

Objetivo:

validar se o sinal pode ser calculado com honestidade metodologica.

### Etapa 6: Testar Comparabilidade

Responder explicitamente:

- incumbente vs incumbente e comparavel?
- incumbente vs novato e comparavel?
- novato vs novato e comparavel?

Objetivo:

definir fronteiras reais do produto.

### Etapa 7: Emitir Parecer de Escopo

Consolidar por funcionalidade:

- validar incumbente
- comparar incumbentes
- validar novato
- descoberta guiada
- shortlist

Objetivo:

fechar o que entra e o que nao entra na V1.

## 7. Criterios de Aceitacao

Uma pergunta do produto so pode ser considerada viavel quando:

- houver pelo menos uma fonte principal forte ou oficial parcial suficiente;
- a explicacao puder apontar a evidencia usada;
- o tipo de candidato estiver claramente enquadrado;
- a comparabilidade estiver explicitada;
- existir regra clara para insuficiencia de evidencia.

## 8. Artefatos Que Devem Sair Dessa Execucao

1. tabela de casos de teste
2. tabela de fontes por caso
3. tabela de sinais por caso
4. quadro de comparabilidade
5. parecer final de escopo da V1

## 9. Perguntas Que Essa Execucao Precisa Responder

- quais sinais realmente sobrevivem a teste com nomes reais?
- para quais perfis de candidato a V1 e defensavel?
- onde o produto precisa responder `nao sei`?
- onde a comparacao deixa de ser justa?
- o que depende de curadoria editorial antes de virar funcionalidade?

## 10. Recomendacao

Sim, isso e escopo de uma frente propria.

Nao precisa ser um agente separado para sempre, mas precisa ser tratado como um trabalho formal e independente de:

- UX
- implementacao
- distribuicao

Sem executar essa matriz, a V1 corre o risco de parecer inteligente, mas ser metodologicamente fraca.
