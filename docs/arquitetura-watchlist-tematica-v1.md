---
title: Arquitetura da Watchlist Tematica da V1
date: 2026-03-28
status: draft
---

# Arquitetura da Watchlist Tematica da V1

## 1. Objetivo

Definir a camada editorial minima que permite converter historico publico em um sinal defensavel de aderencia a valores.

Sem essa camada, a V1 consegue falar sobre:

- identidade
- integridade
- nivel de evidencia
- parte da coerencia

Mas nao consegue dizer, de forma auditavel:

`esse candidato parece alinhado com o que importa para voce`

## 2. Problema que a Watchlist Resolve

Os dados oficiais mostram:

- votos
- proposicoes
- emendas
- posicionamentos formais

Mas eles nao dizem sozinhos:

- qual tema esta em jogo;
- qual lado do tema um ato publico sinaliza;
- que peso aquele ato deve ter na leitura de um valor do usuario.

A watchlist existe para fazer essa ponte de forma:

- publica;
- simples;
- revisavel;
- explicavel.

## 3. Principio Central

A watchlist nao deve tentar interpretar toda a politica brasileira.

Ela deve comecar pequena e responder apenas:

- quais temas entram na V1;
- quais eventos contam como evidencias relevantes nesses temas;
- como cada evidencia se conecta a uma leitura de aderencia;
- quando a evidencia e ambigua demais para entrar.

## 4. Unidade Basica

A unidade minima da watchlist e o `item tematico`.

Cada item tematico liga:

- um tema
- um conjunto de evidencias observaveis
- uma regra de leitura
- uma justificativa publica

## 5. Estrutura Minima de um Item Tematico

Campos recomendados:

- `theme_id`
- `theme_name`
- `user_facing_label`
- `description`
- `why_it_matters`
- `included_signals`
- `excluded_signals`
- `source_types_allowed`
- `interpretation_rule`
- `confidence_rule`
- `notes`

Estrutura conceitual:

```json
{
  "theme_id": "seguranca_publica",
  "theme_name": "Seguranca Publica",
  "user_facing_label": "Seguranca",
  "description": "Posicoes e atos formais relacionados a seguranca, violencia e sistema penal.",
  "why_it_matters": "Ajuda o usuario a ver se o historico do candidato se aproxima de suas prioridades nesse tema.",
  "included_signals": [],
  "excluded_signals": [],
  "source_types_allowed": ["camara_vote", "bill_authorship", "official_statement"],
  "interpretation_rule": "",
  "confidence_rule": "",
  "notes": ""
}
```

## 6. Temas Iniciais da V1

A V1 precisa de poucos temas, mas temas legiveis para o cidadao comum.

Sugestao inicial:

- seguranca
- saude
- educacao
- economia e custo de vida
- direitos das mulheres
- direitos humanos e liberdades civis
- corrupcao e transparencia

Regra:

se um tema nao puder ser explicado em linguagem simples, ele nao entra na V1.

## 7. Tipos de Evidencia Aceitos

### 7.1 Forte

- voto nominal em tema claramente associado
- autoria ou coautoria de proposicao relevante
- relatoria ou atuacao formal diretamente ligada ao tema

### 7.2 Media

- participacao recorrente em comissoes relevantes
- emenda claramente vinculada ao tema
- posicionamento oficial do mandato, quando rastreavel

### 7.3 Fraca

- fala isolada
- post em rede social sem contexto
- cobertura jornalistica sem ato formal associado

Regra:

na V1, evidencia fraca nao deve carregar o sinal sozinha.

## 8. Regra de Interpretacao

Cada tema precisa de uma regra editorial publica.

Exemplo conceitual:

- `seguranca`: certos votos, projetos ou emendas contam como sinais de prioridade em seguranca
- `direitos das mulheres`: certas proposicoes, emendas ou votos contam como sinais formais nesse eixo

O ponto principal nao e dizer qual lado esta certo.

O ponto e dizer:

- qual ato foi considerado;
- por que ele entrou naquele tema;
- o que ele permite inferir;
- o que ele nao permite inferir.

## 9. Regra de Confianca

A aderencia a valores so deve ser calculada quando houver:

- pelo menos um item forte de evidencia, ou
- combinacao suficiente de itens medios coerentes entre si

Se nao houver isso:

- o resultado deve ser `evidencia insuficiente`

## 10. Regra de Exclusao

A watchlist nao deve incluir:

- temas cuja leitura dependa de opiniao partidaria oculta;
- eventos procedimentais dificeis de explicar ao usuario comum;
- evidencias que so especialistas entendem;
- sinais ambiguis sem justificativa publica clara;
- cortes de rede social ou manchetes isoladas como base principal.

## 11. Ligacao com a Experiencia do Usuario

O usuario nao deve ver a watchlist como taxonomia tecnica.

Na interface, ela vira:

- prioridades escolhidas pelo usuario;
- explicacao curta do tema;
- evidencias relevantes associadas ao candidato;
- nivel de confianca naquele tema.

Exemplo de saida:

- `Direitos das mulheres`: ha sinais formais de alinhamento
- `Corrupcao e transparencia`: evidencia insuficiente
- `Economia e custo de vida`: aderencia parcial

## 12. Ligacao com os Sinais da V1

A watchlist alimenta principalmente:

- `aderencia a valores`

E, em alguns casos, ajuda:

- `coerencia`

Ela nao substitui:

- `integridade`
- `nivel de evidencia`

## 13. Ordem Recomendada de Construcao

1. escolher 5 a 7 temas maximos
2. definir linguagem popular de cada tema
3. selecionar tipos de evidencia aceitos
4. escrever regra publica de interpretacao por tema
5. testar a watchlist com os casos da rodada 1
6. revisar onde houve ambiguidade ou arbitrariedade

## 14. Teste Minimo da Watchlist

A watchlist so deve entrar na V1 quando conseguir responder, com nomes reais:

- por que este voto entrou neste tema?
- por que esta proposicao vale como sinal?
- o que esta evidencia diz e o que nao diz?
- o que acontece quando nao ha base suficiente?

## 15. Riscos

- arbitrariedade editorial escondida
- temas largos demais
- evidencias fracas travestidas de sinal robusto
- linguagem enviesada
- excesso de complexidade antes da hora

## 16. Decisao Estrategica

Se for preciso simplificar muito, a V1 pode nascer com apenas:

- 3 a 5 temas
- somente evidencias fortes e medias
- resultado por tema em tres estados:
  - alinhamento observavel
  - aderencia parcial
  - evidencia insuficiente

Isso e melhor do que tentar cobrir tudo e perder credibilidade.
