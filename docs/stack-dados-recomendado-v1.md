---
title: Stack de Dados Recomendado da V1
date: 2026-03-28
status: draft
---

# Stack de Dados Recomendado da V1

## 1. Objetivo

Definir o conjunto de MCPs, APIs e fontes que devem sustentar a coleta de evidencias da V1 do Memoria Civica.

O stack deve separar claramente:

- fontes oficiais primarias;
- fontes complementares;
- fontes editoriais e jornalisticas.

## 2. Principio de Uso

A V1 deve usar uma hierarquia simples:

1. fontes oficiais primarias
2. fontes oficiais complementares
3. fontes editoriais e jornalisticas

Regra:

quanto mais sensivel o sinal, maior deve ser a dependencia de fonte oficial.

## 3. Fontes Oficiais Primarias

### 3.1 mcp-brasil

Papel:

- MCP principal da V1
- camada de automacao unificada para fontes governamentais brasileiras

Uso recomendado:

- Camara
- TSE
- Portal da Transparencia
- TCU
- DataJud
- Senado
- outras fontes publicas relevantes expostas pelo servidor

Por que entra:

- concentra boa parte das consultas em uma interface unica;
- reduz necessidade de construir conectores proprios na v1;
- encaixa bem no modelo de coleta sob demanda.

Referencia:

- https://github.com/jxnxts/mcp-brasil

### 3.2 API da Camara

Papel:

- fonte primaria para incumbentes e ex-parlamentares com historico legislativo federal

Uso recomendado:

- identidade parlamentar
- mandato
- votacoes nominais
- proposicoes
- comissoes
- parte da atuacao formal

Referencia:

- https://dadosabertos.camara.leg.br/swagger/api.html?tab=api

### 3.3 Dados Abertos do TSE

Papel:

- fonte primaria eleitoral para incumbentes e nao incumbentes

Uso recomendado:

- candidaturas
- bens declarados
- contas
- redes sociais oficiais
- coligacoes
- dados cadastrais eleitorais

Observacao:

mesmo para incumbentes, o TSE deve ser consultado junto com a Camara.

Referencia:

- https://dadosabertos.tse.jus.br/group/candidatos

## 4. Fontes Oficiais Complementares

### 4.1 mcpcand

Papel:

- MCP especializado em DivulgaCandContas e dados do TSE

Quando usar:

- se o fluxo eleitoral do TSE no `mcp-brasil` nao for suficiente;
- se voce quiser maior previsibilidade ou granularidade em dados de candidatura e contas.

Referencia:

- https://github.com/karnagge/mcpcand

### 4.2 mcp-portal-transparencia

Papel:

- MCP especializado na API do Portal da Transparencia

Quando usar:

- quando for necessario aprofundar emendas, sancoes, despesas, convenios e trilhas administrativas;
- quando a camada de Transparencia do `mcp-brasil` nao bastar.

Referencia:

- https://github.com/dutradotdev/mcp-portal-transparencia

### 4.3 Portal da Transparencia API

Papel:

- fonte oficial complementar para rastros administrativos e financeiros

Uso recomendado:

- emendas
- sancoes
- despesas
- empenhos
- trilhas auditaveis do Executivo Federal

Referencia:

- https://api.portaldatransparencia.gov.br/changelog

### 4.4 TCU

Papel:

- fonte complementar para red flags formais, acordaos e trilhas de controle externo

Uso recomendado:

- contas irregulares
- acordaos
- decisoes nominais

Observacao:

exige taxonomia cuidadosa para nao superinterpretar ocorrencias textuais.

Referencia:

- https://portal.tcu.gov.br/carta-de-servicos/certidoes/lista-de-responsaveis-com-contas-julgadas-irregulares

### 4.5 DataJud

Papel:

- fonte complementar para trilhas judiciais

Uso recomendado:

- processos judiciais e movimentacoes, com cautela metodologica

Observacao:

nao deve entrar automaticamente no semaforo sem regra editorial muito clara.

Referencias:

- https://datajud-wiki.cnj.jus.br/api-publica/
- https://datajud-wiki.cnj.jus.br/api-publica/endpoints/

### 4.6 Senado e LexML

Papel:

- expansao futura e complemento legislativo

Uso recomendado:

- senadores
- busca em legislacao, proposicoes e normas

Referencias:

- https://www12.senado.leg.br/dados-abertos
- https://www12.senado.leg.br/dados-abertos/legislativo/legislacao/acervo-do-portal-lexml

## 5. Fontes Editoriais e Jornalisticas

### 5.1 Papel dessas fontes

Essas fontes nao devem sustentar sozinhas:

- integridade juridica
- score principal
- aderencia a valores

Elas servem para:

- contexto publico;
- linha do tempo;
- controversias relevantes;
- apoio a revisao editorial;
- explicacao complementar.

### 5.2 Estrategia recomendada

Em vez de buscar um MCP de jornalismo brasileiro altamente especializado, a estrategia mais pragmatica para a V1 e:

- usar um MCP de RSS ou News genérico;
- aplicar allowlist de veiculos brasileiros;
- tratar o resultado como camada editorial complementar.

### 5.3 MCPs e conectores uteis

#### mcp-rss-aggregator

Referencia:

- https://github.com/imprvhub/mcp-rss-aggregator

#### mcp_rss

Referencia:

- https://github.com/buhe/mcp_rss

#### news-api-mcp

Referencia:

- https://github.com/berlinbra/news-api-mcp

### 5.4 Fontes jornalisticas e de feed que valem investigar

- UOL RSS: https://rss.uol.com.br/indice.html
- Barra UOL RSS: https://barrauol.uol.com.br/rss.jhtm
- gov.br RSS: https://www.gov.br/pt-br/rss

Observacao:

vale montar depois uma allowlist editorial com veiculos brasileiros confiaveis e adequados ao posicionamento do produto.

## 6. Recomendacao de Integracao

### Camada 1: obrigatoria

- mcp-brasil
- Camara
- TSE

### Camada 2: complementar

- mcpcand
- mcp-portal-transparencia
- TCU
- DataJud

### Camada 3: editorial

- RSS ou News MCP genérico
- allowlist de fontes brasileiras

## 7. Ordem Recomendada de Integracao

1. integrar `mcp-brasil`
2. validar fluxo de incumbente usando Camara + TSE
3. validar trilha de integridade usando TSE + TCU + Transparencia
4. adicionar camada de cache e registro de evidencias
5. integrar jornalismo apenas como camada complementar

## 8. Decisao Estrategica

Para a V1, o stack mais sensato e:

- `mcp-brasil` como espinha dorsal;
- `Camara + TSE` como dupla primaria para incumbentes;
- `TSE + fontes institucionais` para nao incumbentes;
- `TCU + Transparencia` para reforco de integridade;
- jornalismo apenas como contexto complementar.
