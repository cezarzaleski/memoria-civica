---
title: Mapa de Arquitetura do Sistema da V1
date: 2026-03-28
status: draft
---

# Mapa de Arquitetura do Sistema da V1

## 1. Objetivo

Consolidar a arquitetura logica da V1 do Memoria Civica em um unico mapa, conectando:

- produto
- evidencias
- sinais
- fontes
- resposta ao usuario

## 2. Tese do Sistema

A V1 e uma ferramenta de checagem civica para escolha consciente de candidatos a deputado federal.

O sistema nao comeca por ETL, ranking ou recomendacao.

Ele comeca por uma consulta do usuario e responde com:

- semaforo
- razoes curtas
- alertas
- confianca
- fontes

## 3. Componentes Principais

### 3.1 Camada de Experiencia

Responsabilidade:

- receber o nome do candidato;
- coletar contexto opcional do usuario;
- exibir resultado explicavel.

Entradas:

- nome
- UF opcional
- partido opcional
- prioridades do usuario, quando houver

Saidas:

- resposta curta
- explicacao expandida
- fontes abertas

### 3.2 Camada de Orquestracao da Consulta

Responsabilidade:

- coordenar o fluxo da consulta;
- decidir quais fontes consultar;
- encadear identidade, coleta, sinais e resposta.

Funcoes:

- resolver identidade
- classificar tipo de candidato
- selecionar plano de coleta
- consolidar evidencias
- montar resposta final

### 3.3 Camada de Identidade

Responsabilidade:

- descobrir exatamente quem esta sendo avaliado;
- evitar erro de homonimo;
- conectar a pessoa entre fontes.

Saida:

- pessoa resolvida com ids e metadados minimos

### 3.4 Camada de Coleta de Evidencias

Responsabilidade:

- consultar fontes oficiais e complementares;
- coletar apenas o necessario para os sinais da consulta;
- registrar o que foi encontrado.

Subdivisao:

- fontes primarias
- fontes complementares
- fontes editoriais

### 3.5 Camada de Registro de Evidencias

Responsabilidade:

- armazenar cada item de evidencia com origem e contexto;
- permitir auditoria;
- permitir recalculo posterior.

Campos minimos:

- pessoa
- sinal
- fonte
- url
- data de coleta
- data do fato
- tipo
- resumo
- forca da evidencia

### 3.6 Camada de Classificacao de Evidencias

Responsabilidade:

- dizer quao forte e cada evidencia;
- diferenciar forte oficial de parcial, complementar e insuficiente.

Saida:

- evidencias classificadas

### 3.7 Camada de Sinais

Responsabilidade:

- transformar evidencias em leitura util para o produto.

Sinais da V1:

- integridade
- coerencia
- nivel de evidencia
- aderencia a valores

### 3.8 Camada Editorial

Responsabilidade:

- definir a watchlist tematica;
- explicitar regras de interpretacao;
- impedir arbitrariedade.

Saida:

- temas
- eventos aceitos
- regras de leitura
- regras de confianca

### 3.9 Camada de Explicacao

Responsabilidade:

- converter sinais em resposta legivel;
- compor semaforo, razoes, alertas e confianca;
- explicitar limites e lacunas.

## 4. Fontes por Papel

### 4.1 Fontes Primarias

- mcp-brasil
- Camara
- TSE

### 4.2 Fontes Complementares

- TCU
- Portal da Transparencia
- DataJud
- fontes institucionais oficiais

### 4.3 Fontes Editoriais

- RSS e News com allowlist
- jornalismo brasileiro confiavel

Regra:

fontes editoriais complementam; nao mandam no semaforo.

## 5. Fluxo Entre Componentes

```text
Usuario
-> Experiencia
-> Orquestracao da Consulta
-> Identidade
-> Plano de Coleta
-> Coleta de Evidencias
-> Registro de Evidencias
-> Classificacao de Evidencias
-> Sinais
-> Explicacao
-> Resposta ao Usuario
```

Quando houver prioridade do usuario:

```text
Prioridades do usuario
-> Camada Editorial / Watchlist
-> Sinal de Aderencia a Valores
-> Explicacao
```

## 6. Regras Arquiteturais

### 6.1 Nao adivinhar identidade

Sem identidade resolvida, nao ha consulta valida.

### 6.2 Nao calcular sem base

Sem evidencia suficiente, o sistema deve responder `cinza`.

### 6.3 Nao colapsar tudo em score opaco

Os sinais precisam continuar visiveis.

### 6.4 Nao usar jornalismo como prova principal de integridade

Jornalismo contextualiza; nao sentencia.

### 6.5 Nao esconder assimetria entre tipos de candidato

Incumbentes e desafiantes nao entram com a mesma densidade de evidencia.

## 7. Modo de Operacao

### 7.1 Consulta sob demanda

O sistema consulta as fontes quando o usuario pede.

### 7.2 Cache seletivo

Persistir apenas:

- identidade resolvida
- evidencias recentes
- classificacoes feitas
- itens editoriais

### 7.3 Revisao assistida

Casos ambiguos ou sensiveis podem exigir:

- revisao humana
- revisao editorial

## 8. Documentos Relacionados

- [memoria-civica-2026-discovery.md](/Users/cezar.zaleski/workspace/pessoal/memoria_civica/docs/memoria-civica-2026-discovery.md)
- [matriz-viabilidade-dados-evidencias-v1.md](/Users/cezar.zaleski/workspace/pessoal/memoria_civica/docs/matriz-viabilidade-dados-evidencias-v1.md)
- [arquitetura-minima-sinais-v1.md](/Users/cezar.zaleski/workspace/pessoal/memoria_civica/docs/arquitetura-minima-sinais-v1.md)
- [arquitetura-watchlist-tematica-v1.md](/Users/cezar.zaleski/workspace/pessoal/memoria_civica/docs/arquitetura-watchlist-tematica-v1.md)
- [arquitetura-coleta-sistemica-evidencias-v1.md](/Users/cezar.zaleski/workspace/pessoal/memoria_civica/docs/arquitetura-coleta-sistemica-evidencias-v1.md)
- [stack-dados-recomendado-v1.md](/Users/cezar.zaleski/workspace/pessoal/memoria_civica/docs/stack-dados-recomendado-v1.md)
- [fluxo-operacional-consulta-v1.md](/Users/cezar.zaleski/workspace/pessoal/memoria_civica/docs/fluxo-operacional-consulta-v1.md)
- [rodada-1-validacao-evidencias-v1.md](/Users/cezar.zaleski/workspace/pessoal/memoria_civica/docs/rodada-1-validacao-evidencias-v1.md)

## 9. Leitura Final

Se for preciso resumir a arquitetura da V1 em uma linha:

`consulta do usuario -> identidade -> evidencias oficiais -> sinais explicaveis -> semaforo com fontes`

Esse e o centro do sistema.
