---
title: Rodada 2 - Validacao de Evidencias da V1
date: 2026-04-01
status: draft
---

# Rodada 2 - Validacao de Evidencias da V1

## 1. Objetivo

Executar uma rodada controlada com casos reais para sair da hipotese e medir a viabilidade da V1 com base em comportamento observado do sistema.

Esta rodada responde principalmente:

- onde a V1 ja e defensavel;
- onde a V1 e defensavel com cautela;
- onde a comparabilidade quebra;
- quando o produto deve responder `evidencia insuficiente`.

## 2. Escopo da Rodada

A rodada cobre:

- resolucao de identidade;
- cobertura real de fontes;
- comportamento dos sinais `integrity`, `coherence`, `evidence_level` e `values_fit`;
- fronteira de comparabilidade entre perfis de candidato.

Esta rodada ainda nao fecha:

- ranking;
- recomendacao de melhor candidato;
- expansao de cobertura para qualquer nome;
- experiencia final de distribuicao.

## 3. Casos Executados

### Caso 1: Incumbente com historico forte

- nome-base: Nikolas Ferreira
- cargo alvo: deputado federal
- UF: MG
- prioridade testada: nenhuma

### Caso 2: Incumbente com perfil controverso

- nome-base: Erika Hilton
- cargo alvo: deputado federal
- UF: SP
- prioridade testada: direitos das mulheres

### Caso 3: Figura publica com vida parlamentar observavel

- nome-base: Fred Linhares
- cargo alvo: deputado federal
- UF: DF
- prioridade testada: transparencia

### Caso 4: Nome com cobertura limitada

- nome-base: Ricardo Cappelli
- cargo alvo: deputado federal
- UF: DF
- prioridade testada: transparencia

## 4. Resultado por Caso

### Caso 1: Nikolas Ferreira

#### 4.1 Identidade

- nome consultado: Nikolas Ferreira
- nome resolvido: Nikolas Ferreira de Oliveira
- aliases encontrados: Nikolas Ferreira
- cargo alvo: deputado federal
- partido: PL
- UF: MG
- status: incumbente
- ids oficiais localizados: `camara_id=209787`
- risco de homonimo: baixo

#### 4.2 Fontes Testadas

| Fonte | Encontrou dados? | Tipo de dado | Qualidade inicial | Observacoes |
|---|---|---|---|---|
| Camara | sim | perfil parlamentar e atividade legislativa | forte oficial | identidade resolvida com seguranca |
| TSE | sim | resultado eleitoral | forte oficial | suporte de identidade e historico eleitoral |
| Transparencia | sim | triagem de alertas administrativos | oficial parcial | sem conclusao grave isolada |
| Fonte complementar | sim | contexto adicional do caso | complementar confiavel | nao foi base principal do parecer |

#### 4.3 Sinal: Integridade

- evidencias encontradas: triagem oficial sem red flag determinante
- classificacao das evidencias: oficial parcial
- leitura inicial: ha material para screening, mas nao para conclusao grave
- confianca: media
- decisao: entra com cautela

#### 4.4 Sinal: Coerencia

- evidencias encontradas: historico parlamentar observavel e suficiente para leitura inicial
- classificacao das evidencias: forte oficial
- leitura inicial: o sistema sustenta comparacao com base legislativa
- confianca: alta
- decisao: entra

#### 4.5 Sinal: Nivel de Evidencia

- volume de sinais oficiais: alto
- diversidade de fontes: alta
- atualidade: suficiente
- proximidade com a pergunta do usuario: alta
- classificacao final: positiva

#### 4.6 Sinal: Aderencia a Valores

- tema ou prioridade testada: nao informado
- watchlist usada: minima
- evidencias encontradas: nao aplicavel para inferencia tematica
- leitura inicial: o sistema se comportou corretamente ao nao inferir sem prioridade
- confianca: insuficiente
- decisao: entra com regra de insuficiencia explicita

#### 4.7 Parecer do Caso

- validacao de candidato: viavel
- comparacao com incumbentes: viavel
- comparacao com desafiantes: nao viavel
- observacao final: confirma que a espinha dorsal da V1 funciona melhor quando ha mandato observavel e fontes oficiais densas

### Caso 2: Erika Hilton

#### 4.1 Identidade

- nome consultado: Erika Hilton
- nome resolvido: Erika Hilton
- aliases encontrados: Erika Hilton
- cargo alvo: deputado federal
- partido: PSOL
- UF: SP
- status: incumbente
- ids oficiais localizados: `camara_id=220645`
- risco de homonimo: baixo

#### 4.2 Fontes Testadas

| Fonte | Encontrou dados? | Tipo de dado | Qualidade inicial | Observacoes |
|---|---|---|---|---|
| Camara | sim | perfil parlamentar e atividade legislativa | forte oficial | base principal do caso |
| TSE | sim | resultado eleitoral | forte oficial | suporte de identidade |
| Transparencia | sim | triagem de alertas administrativos | oficial parcial | sem base para conclusao forte isolada |
| Fonte complementar | sim | contexto adicional do caso | complementar confiavel | apoio, nao espinha dorsal |

#### 4.3 Sinal: Integridade

- evidencias encontradas: screening oficial sem conclusao grave automatica
- classificacao das evidencias: oficial parcial
- leitura inicial: sinal util para alerta e triagem, nao para julgamento forte
- confianca: media
- decisao: entra com cautela

#### 4.4 Sinal: Coerencia

- evidencias encontradas: historico legislativo suficiente para leitura observavel
- classificacao das evidencias: forte oficial
- leitura inicial: o sistema sustenta comparacao entre fala publica e mandato
- confianca: alta
- decisao: entra

#### 4.5 Sinal: Nivel de Evidencia

- volume de sinais oficiais: alto
- diversidade de fontes: alta
- atualidade: suficiente
- proximidade com a pergunta do usuario: alta
- classificacao final: positiva

#### 4.6 Sinal: Aderencia a Valores

- tema ou prioridade testada: direitos das mulheres
- watchlist usada: minima
- evidencias encontradas: insuficientes para a taxonomia atual
- leitura inicial: a watchlist minima ainda nao cobre esse tema com base suficiente para inferencia segura
- confianca: insuficiente
- decisao: entra com cautela

#### 4.7 Parecer do Caso

- validacao de candidato: viavel com cautela
- comparacao com incumbentes: viavel com cautela
- comparacao com desafiantes: nao viavel
- observacao final: reforca a base forte para incumbentes, mas mostra que `values_fit` ainda depende do recorte tematico adotado

### Caso 3: Fred Linhares

#### 4.1 Identidade

- nome consultado: Fred Linhares
- nome resolvido: Fred Linhares
- aliases encontrados: Fred Linhares
- cargo alvo: deputado federal
- partido: Republicanos
- UF: DF
- status: incumbente
- ids oficiais localizados: `camara_id=220534`
- risco de homonimo: baixo

#### 4.2 Fontes Testadas

| Fonte | Encontrou dados? | Tipo de dado | Qualidade inicial | Observacoes |
|---|---|---|---|---|
| Camara | sim | perfil parlamentar, atividade e votos | forte oficial | um endpoint de votacoes devolveu `504`, mas retry automatico recuperou a consulta |
| TSE | sim | resultado eleitoral | forte oficial | suporte de identidade |
| Transparencia | parcial | triagem de alertas administrativos | oficial parcial | houve `400` em parte da triagem nominal, sem impedir resposta final |
| Fonte complementar | sim | contexto adicional do caso | complementar confiavel | nao foi base principal do parecer |

#### 4.3 Sinal: Integridade

- evidencias encontradas: screening oficial parcial, sem red flag determinante
- classificacao das evidencias: oficial parcial
- leitura inicial: util como camada de cautela, nao como score forte
- confianca: media
- decisao: entra com cautela

#### 4.4 Sinal: Coerencia

- evidencias encontradas: base parlamentar suficiente para leitura observavel
- classificacao das evidencias: forte oficial
- leitura inicial: comparacao legislativa defensavel
- confianca: alta
- decisao: entra

#### 4.5 Sinal: Nivel de Evidencia

- volume de sinais oficiais: alto
- diversidade de fontes: media a alta
- atualidade: suficiente
- proximidade com a pergunta do usuario: alta
- classificacao final: positiva

#### 4.6 Sinal: Aderencia a Valores

- tema ou prioridade testada: transparencia
- watchlist usada: minima
- evidencias encontradas: uma evidencia oficial forte suficiente para alinhamento observavel
- leitura inicial: a implementacao minima de `values_fit` funciona quando o tema esta coberto e ha rastro legislativo
- confianca: media
- decisao: entra com cautela

#### 4.7 Parecer do Caso

- validacao de candidato: viavel com cautela
- comparacao com incumbentes: viavel com cautela
- comparacao com desafiantes: nao viavel
- observacao final: prova que a watchlist minima ja gera sinal util em tema suportado, mas ainda com alcance restrito

### Caso 4: Ricardo Cappelli

#### 4.1 Identidade

- nome consultado: Ricardo Cappelli
- nome resolvido: Ricardo Cappelli
- aliases encontrados: nenhum com correspondencia oficial confirmada
- cargo alvo: deputado federal
- partido: nao localizado
- UF: DF
- status: desafiante ou nome com cobertura limitada
- ids oficiais localizados: nenhum
- risco de homonimo: alto por ausencia de identidade oficial resolvida

#### 4.2 Fontes Testadas

| Fonte | Encontrou dados? | Tipo de dado | Qualidade inicial | Observacoes |
|---|---|---|---|---|
| Camara | nao | identidade parlamentar | insuficiente | nenhuma identidade oficial localizada |
| TSE | nao | candidatura oficial confirmada no fluxo atual | insuficiente | sem match para a consulta executada |
| Transparencia | nao aplicavel | screening dependente de identidade resolvida | insuficiente | a consulta parou antes da triagem util |
| Fonte complementar | nao aplicavel | contexto adicional | insuficiente | nao deve substituir identidade oficial ausente |

#### 4.3 Sinal: Integridade

- evidencias encontradas: nenhuma util
- classificacao das evidencias: insuficiente
- leitura inicial: sem identidade resolvida, o sinal nao deve ser calculado
- confianca: insuficiente
- decisao: nao entra

#### 4.4 Sinal: Coerencia

- evidencias encontradas: nenhuma util
- classificacao das evidencias: insuficiente
- leitura inicial: sem historico observavel e sem identidade oficial, nao ha base de comparacao
- confianca: insuficiente
- decisao: nao entra

#### 4.5 Sinal: Nivel de Evidencia

- volume de sinais oficiais: inexistente no fluxo atual
- diversidade de fontes: inexistente
- atualidade: nao aplicavel
- proximidade com a pergunta do usuario: insuficiente
- classificacao final: insuficiente

#### 4.6 Sinal: Aderencia a Valores

- tema ou prioridade testada: transparencia
- watchlist usada: minima
- evidencias encontradas: nenhuma util
- leitura inicial: `values_fit` nao pode ser inferido sem identidade e historico
- confianca: insuficiente
- decisao: nao entra

#### 4.7 Parecer do Caso

- validacao de candidato: nao viavel
- comparacao com incumbentes: nao viavel
- comparacao com desafiantes: parcial
- observacao final: fixa o limite inferior atual da V1 e confirma que o produto precisa responder `evidencia insuficiente` cedo nesses casos

## 5. Quadro de Consolidacao da Rodada

| Sinal | Incumbente forte | Incumbente controverso | Figura com vida parlamentar observavel | Nome com cobertura limitada | Parecer geral |
|---|---|---|---|---|---|
| Integridade | entra com cautela | entra com cautela | entra com cautela | nao entra | viavel como triagem cautelosa, nao como juizo forte |
| Coerencia | entra | entra | entra | nao entra | viavel quando ha historico legislativo |
| Nivel de evidencia | entra | entra | entra | nao entra | viavel e util como metacamada explicita |
| Aderencia a valores | entra com insuficiencia quando nao ha prioridade | entra com cautela | entra com cautela | nao entra | parcialmente viavel na watchlist minima atual |

## 6. Quadro de Comparabilidade

| Comparacao | Parecer | Observacao |
|---|---|---|
| incumbente vs incumbente | viavel | base oficial e historico observavel sustentam comparacao inicial |
| incumbente vs figura com vida parlamentar observavel | viavel com cautela | ainda ha comparabilidade, mas a densidade de historico pode variar |
| incumbente vs desafiante ou nome sem identidade resolvida | nao viavel | assimetria de dados rompe comparacao justa |
| desafiante vs desafiante | parcialmente viavel | depende de identidade oficial e cobertura minima por fonte |

## 7. Criterio Operacional de `evidencia insuficiente`

O produto deve responder `evidencia insuficiente` quando qualquer uma destas condicoes ocorrer:

- a identidade oficial nao for resolvida com seguranca;
- nao houver ao menos uma fonte auditavel conectada diretamente ao sinal;
- a watchlist do tema nao tiver base suficiente para inferencia honesta;
- a comparacao exigir tratar historicos estruturalmente desiguais como equivalentes;
- a explicacao depender mais de narrativa complementar do que de evidencia oficial ou oficial parcial suficiente.

## 8. Parecer da Rodada 2

Esta rodada confirma que a V1 ja tem base defensavel para incumbentes e para nomes com vida parlamentar observavel, desde que:

- a espinha dorsal continue oficial;
- `integrity` permaneça como triagem cautelosa;
- `values_fit` fique limitado a temas realmente cobertos;
- nomes sem identidade oficial resolvida recebam resposta curta de insuficiencia, sem forcar inferencia.

Tambem confirma que a assimetria de dados nao e detalhe de implementacao. Ela e uma fronteira real do produto.
