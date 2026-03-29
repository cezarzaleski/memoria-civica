---
title: One Pager de Produto da V1
date: 2026-03-28
status: draft
---

# Memoria Civica V1

## Problema

Na escolha para deputado federal, o cidadao comum costuma decidir com pouca clareza, muito ruido e baixa capacidade de verificar se um candidato realmente o representa.

Ha excesso de narrativa e pouca traducao confiavel de evidencias publicas em uma resposta simples, auditavel e util antes do voto.

## Promessa

Memoria Civica nasce como ferramenta de checagem civica para escolha consciente.

Nao diz em quem votar.

Ajuda o usuario a validar, com base em evidencias publicas verificaveis, se um candidato o representa, o que esse nome fez, apoiou ou disse, e se ha alertas relevantes de integridade, incoerencia ou baixa evidencia.

## Publico

O foco inicial e o cidadao comum que:

- ja tem um candidato em mente, ou esta perto de escolher;
- nao acompanha politica de forma profissional;
- quer uma resposta curta, clara e verificavel;
- prefere linguagem popular com opcao de aprofundar nas fontes.

## Experiencia principal

A experiencia central da V1 e a validacao de um candidato que o usuario ja quer checar.

A saida deve trazer:

- semaforo explicavel
- 3 a 5 motivos curtos
- alertas relevantes
- nivel de confianca
- links para as fontes

Comparacao guiada entre nomes pode existir como apoio, mas a tese principal da V1 e validar uma escolha, e nao produzir ranking absoluto.

## Diferenciais

O produto se diferencia por:

- combinar linguagem simples com rastreabilidade;
- usar fontes oficiais como espinha dorsal;
- expor separadamente integridade, coerencia, nivel de evidencia e aderencia a valores.

Regra metodologica central:

- fez pesa mais que apoiou
- apoiou pesa mais que disse

Quando a base nao sustenta a resposta, o produto deve dizer `evidencia insuficiente`, em vez de inventar confianca.

## Limites da V1

A V1 nao deve nascer como:

- portal de dados
- chat opaco
- recomendador eleitoral

Tambem nao deve oferecer:

- pedido direto de voto
- score unico fechado
- ranking final de melhores candidatos

Ha assimetria estrutural entre incumbentes e desafiantes:

- incumbentes tem historico legislativo muito mais rico

Por isso, a entrada mais segura da V1 e com deputado federal incumbente e ex-parlamentar com historico forte.

Em 28/03/2026, os dados publicos de candidaturas 2026 do TSE ainda nao estavam abertos no portal consultado. A cobertura de candidatos novos precisa assumir essa restricao.

A camada de aderencia a valores ainda depende de uma watchlist tematica pequena, publica e auditavel.

## Stack de dados em alto nivel

A V1 deve operar de fora para dentro:

- pergunta do usuario
- evidencia necessaria
- sinais derivados
- explicacao final com fontes

Fontes centrais:

- Camara dos Deputados para votos, proposicoes e atuacao legislativa
- TSE para dados de candidatura e contas quando disponiveis
- TCU e Portal da Transparencia como apoio a alertas de integridade

Arquitetura em alto nivel:

- `identity`
- `evidence`
- `signals`
- `explanations`
- `experience`

Se houver persistencia local, ela deve funcionar como cache, indexacao ou materializacao auxiliar, e nao como premissa obrigatoria de um ETL pesado desde o dia um.

## Proximos passos

O caminho mais defensavel e:

1. fechar a V1 para validacao de incumbentes
2. materializar uma watchlist tematica enxuta de 3 a 5 temas
3. testar essa leitura em casos reais
4. transformar isso em prototipo funcional com semaforo explicavel e comparacao basica
5. depois ampliar cobertura para candidatos com dados oficiais do TSE
6. so mais adiante evoluir para descoberta orientada por valores e shortlist explicavel
