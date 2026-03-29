---
title: Matriz de Viabilidade de Dados e Evidencias da V1
date: 2026-03-28
status: draft
---

# Matriz de Viabilidade de Dados e Evidencias da V1

## 1. Objetivo

Este documento define como validar se os dados necessarios para o Memoria Civica V1 sao realmente suficientes para sustentar o produto.

O foco nao e apenas descobrir se uma fonte existe. O foco e responder:

- o dado existe para o caso de uso certo?
- ele chega no momento certo?
- ele e comparavel entre tipos de candidato?
- ele sustenta um sinal explicavel sem exagero metodologico?
- ele pode entrar na V1 com seguranca civica, juridica e reputacional?

## 2. Regra de Produto

Nenhuma funcionalidade entra na V1 apenas porque a fonte existe.

Ela so entra quando houver base suficiente para:

- gerar sinal minimamente defensavel;
- explicar a conclusao com fontes;
- mostrar incerteza quando necessario;
- evitar comparacoes estruturalmente injustas.

## 3. Escala de Forca da Evidencia

### 3.1 Evidencia Forte Oficial

Dados publicos oficiais, estruturados, auditaveis e diretamente conectados ao comportamento do agente politico.

Exemplos:

- votos nominais na Camara
- dados oficiais de candidatura no TSE
- prestacao de contas eleitoral oficial

### 3.2 Evidencia Oficial Parcial

Dados oficiais validos, mas incompletos para a pergunta do usuario ou insuficientes para comparacao plena.

Exemplos:

- dados cadastrais de candidatura sem historico de mandato
- dados de bens declarados sem contexto suficiente

### 3.3 Evidencia Complementar Confiavel

Dados nao centrais, mas uteis para complementar contexto, desde que a origem seja clara e rastreavel.

Exemplos:

- site oficial do candidato
- redes sociais oficiais do candidato
- cobertura jornalistica de veiculo confiavel

### 3.4 Evidencia Fraca ou Declaratoria

Dados que dizem o que a pessoa afirma, mas nao provam conduta ou representacao.

Exemplos:

- slogan de campanha
- promessa eleitoral isolada
- fala sem lastro observavel

### 3.5 Evidencia Insuficiente

Quando nao ha volume, qualidade, atualidade ou comparabilidade suficientes para sustentar conclusao minimamente honesta.

Nesses casos, o produto deve responder `evidencia insuficiente`.

## 4. Matriz de Validacao

| Pergunta do usuario | Sinal necessario | Fonte principal | Forca esperada | Cobertura inicial | Risco principal | Decisao V1 |
|---|---|---|---|---|---|---|
| Esse deputado federal realmente me representa? | Historico observavel de voto e posicionamento | Camara dos Deputados | Forte oficial | Alta para incumbentes | Curadoria tematica ruim pode enviesar leitura | Entra |
| Como esse deputado votou em temas importantes para mim? | Votos nominais por tema | Camara dos Deputados | Forte oficial | Alta para incumbentes | Mapeamento de tema para votacao | Entra |
| Esse candidato parece coerente com o que diz? | Relacao entre discurso e historico observavel | Camara + fontes publicas complementares | Oficial parcial + complementar | Media | Comparacao injusta entre incumbente e novato | Entra com cautela |
| Esse candidato tem alertas graves de integridade? | Red flags oficiais e juridicas relevantes | TCU, TSE, Transparencia e outras bases oficiais | Oficial parcial | Media | Confundir processo, investigacao e condenacao | Entra com taxonomia estrita |
| Esse candidato tem evidencia suficiente para ser avaliado? | Quantidade e qualidade de sinais disponiveis | Metacamada interna por fonte | Forte derivada | Alta | Score opaco de confianca | Entra |
| Esse candidato novo me representa? | Perfil, contas, sinais publicos e contexto partidario | TSE + fontes complementares | Parcial | Media a baixa | Pouca comparabilidade | Entra como avaliacao limitada |
| Quais candidatos mais combinam comigo? | Matching entre valores e sinais publicos | Camara, TSE e camada metodologica | Parcial a forte, dependendo do caso | Desigual | Virar recomendador opaco | Entra depois |
| Qual e o melhor candidato? | Ranking final normativo | Multiplas fontes | Fraca para afirmacao absoluta | Baixa | Alto risco metodologico e regulatorio | Nao entra |

## 5. Regras de Exclusao

Sinais nao entram na V1 quando:

- nao houver fonte auditavel;
- houver risco alto de confundir fato juridico com cobertura narrativa;
- a comparacao entre candidatos depender de premissas desiguais nao explicitadas;
- o sinal parecer robusto, mas na pratica for apenas declaratorio;
- a conclusao nao puder ser explicada em linguagem simples com prova.

## 6. Regras de Comparabilidade

### 6.1 Incumbentes

Podem ser avaliados com maior confianca porque existe historico de mandato observavel.

### 6.2 Desafiantes e Novatos

Devem ser avaliados com regime diferente:

- menor confianca estrutural;
- mais dependencia de dados cadastrais e financeiros;
- mais frequencia de `evidencia insuficiente`;
- proibicao pratica de compara-los como se tivessem a mesma densidade de historico que incumbentes.

### 6.3 Regra Geral

O produto nao deve esconder assimetria de dados. Assimetria precisa aparecer como parte da explicacao.

## 7. Taxonomia Inicial de Sinais

### 7.1 Integridade

Entram:

- contas julgadas irregulares em base oficial
- sancoes e alertas oficiais
- problemas formais em prestacao de contas quando houver fonte valida

Nao entram sem validacao extra:

- rumor
- recorte de rede social
- cobertura jornalistica tratada como sentenca

### 7.2 Coerencia

Entram:

- comparacao entre posicionamento publico e votos observados
- comparacao entre tema defendido e historico legislativo

Exigem cautela:

- fala isolada
- corte fora de contexto

### 7.3 Nivel de Evidencia

Deve considerar:

- quantidade de fontes
- diversidade de fontes
- oficialidade
- atualidade
- proximidade entre o sinal e a pergunta do usuario

### 7.4 Aderencia a Valores

Exige uma camada editorial propria:

- conjunto inicial de temas
- watchlist legislativa por tema
- regra de interpretacao publica
- limite claro do que e inferencia

## 8. Parecer Inicial de Viabilidade por Funcionalidade

### 8.1 Validar incumbente a deputado federal

Parecer: viavel

Razao:

- ha historico observavel
- ha base forte de votos e comportamento legislativo
- a explicacao pode ser sustentada por fonte oficial

### 8.2 Comparar incumbentes entre si

Parecer: viavel com cautela

Razao:

- a comparabilidade e melhor
- ainda depende de boa curadoria tematica e regra de pesos

### 8.3 Validar candidato nao incumbente

Parecer: parcialmente viavel

Razao:

- ha alguns sinais oficiais
- falta historico equivalente
- o produto deve explicitar que a avaliacao e limitada

### 8.4 Shortlist de candidatos compativeis

Parecer: viavel depois

Razao:

- depende de metodologia mais madura
- depende de camada de valores bem definida
- aumenta risco de percepcao como recomendador

### 8.5 Ranking absoluto de melhores candidatos

Parecer: nao viavel para V1

Razao:

- risco metodologico alto
- risco reputacional alto
- risco regulatorio maior

## 9. Entregaveis do Agente de Viabilidade de Evidencia

Uma frente ou agente com esse papel deve produzir:

1. matriz de perguntas, sinais e fontes;
2. classificacao de forca da evidencia por sinal;
3. parecer de cobertura por tipo de candidato;
4. lista do que entra, nao entra e entra depois;
5. criterios de `evidencia insuficiente`.

## 10. Recomendacao Final

A validacao de viabilidade de dados e evidencias precisa virar etapa formal do projeto.

Sem ela, o risco e construir uma boa experiencia sobre sinais fracos, desiguais ou metodologicamente injustos.

Para a V1, a decisao mais segura e:

- priorizar incumbentes e comparacoes defensaveis;
- tratar novatos com regime de confianca menor;
- adiar ranking absoluto;
- usar fontes oficiais como espinha dorsal;
- transformar a falta de dados em resposta honesta, e nao em inferencia forte.
