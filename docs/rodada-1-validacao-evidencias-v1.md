---
title: Rodada 1 - Validacao de Evidencias da V1
date: 2026-03-28
status: draft
---

# Rodada 1 - Validacao de Evidencias da V1

## 1. Objetivo

Executar uma primeira rodada curta e controlada da matriz de viabilidade para descobrir quais sinais sobrevivem ao teste com nomes reais.

Esta rodada nao serve para fechar o produto inteiro.

Ela serve para responder:

- o que ja e defensavel;
- o que exige cautela;
- o que ainda nao deve entrar na V1.

## 2. Escopo da Rodada

Esta rodada testa:

- resolucao de identidade;
- cobertura de fontes;
- sinais de integridade;
- sinais de coerencia;
- nivel de evidencia;
- comparabilidade entre perfis.

Esta rodada ainda nao fecha:

- ranking final;
- metodologia completa de aderencia a valores;
- distribuicao;
- UX final.

## 3. Casos de Teste Iniciais

O conjunto inicial deve ser pequeno e variado.

### Caso 1: Incumbente com historico forte

Perfil esperado:

- deputado federal em exercicio;
- bastante atividade legislativa;
- presenca clara em fontes oficiais.

Objetivo:

testar o melhor cenario de cobertura.

Nome-base sugerido:

- Nikolas Ferreira (PL-MG)

### Caso 2: Incumbente com perfil controverso

Perfil esperado:

- deputado federal em exercicio;
- historico publico polarizado ou com controversias;
- presenca forte em rede e imprensa.

Objetivo:

testar separacao entre evidencia oficial, narrativa e ruido.

Nome-base sugerido:

- Erika Hilton (PSOL-SP)

### Caso 3: Ex-parlamentar ou figura publica com trajetoria conhecida

Perfil esperado:

- nome com vida publica rastreavel;
- sem necessariamente ocupar mandato atual.

Objetivo:

testar transicao entre historico observavel e cobertura parcial.

Nome-base sugerido:

- Fred Linhares (Republicanos-DF)

### Caso 4: Candidato ou pre-candidato sem mandato atual

Perfil esperado:

- nome com menor densidade de historico legislativo;
- mais dependencia de dados cadastrais, financeiros e declaratorios.

Objetivo:

testar o limite inferior da comparabilidade.

Nome-base sugerido:

- Ricardo Cappelli

## 4. Template por Caso

Preencher um bloco por nome testado.

### 4.1 Identidade

- nome consultado:
- nome resolvido:
- aliases encontrados:
- cargo alvo:
- partido:
- UF:
- status: incumbente / ex-parlamentar / desafiante
- ids oficiais localizados:
- risco de homonimo: baixo / medio / alto

### 4.2 Fontes Testadas

| Fonte | Encontrou dados? | Tipo de dado | Qualidade inicial | Observacoes |
|---|---|---|---|---|
| Camara |  |  |  |  |
| TSE |  |  |  |  |
| TCU |  |  |  |  |
| Transparencia |  |  |  |  |
| Fonte complementar 1 |  |  |  |  |
| Fonte complementar 2 |  |  |  |  |

### 4.3 Sinal: Integridade

- evidencias encontradas:
- classificacao das evidencias:
- leitura inicial:
- confianca:
- decisao:

### 4.4 Sinal: Coerencia

- evidencias encontradas:
- classificacao das evidencias:
- leitura inicial:
- confianca:
- decisao:

### 4.5 Sinal: Nivel de Evidencia

- volume de sinais oficiais:
- diversidade de fontes:
- atualidade:
- proximidade com a pergunta do usuario:
- classificacao final:

### 4.6 Sinal: Aderencia a Valores

- tema ou prioridade testada:
- watchlist usada:
- evidencias encontradas:
- leitura inicial:
- confianca:
- decisao:

### 4.7 Parecer do Caso

- validacao de candidato: viavel / viavel com cautela / parcial / nao viavel
- comparacao com incumbentes: viavel / viavel com cautela / parcial / nao viavel
- comparacao com desafiantes: viavel / viavel com cautela / parcial / nao viavel
- observacao final:

## 5. Escala Padrao de Classificacao

### 5.1 Forca da Evidencia

- forte oficial
- oficial parcial
- complementar confiavel
- fraca ou declaratoria
- insuficiente

### 5.2 Confianca do Sinal

- alta
- media
- baixa
- insuficiente

### 5.3 Decisao de Escopo

- entra
- entra com cautela
- entra depois
- nao entra

## 6. Checklist de Decisao

Um sinal so pode `entrar` se todas as respostas abaixo forem satisfatorias:

- a identidade do nome foi resolvida sem ambiguidade relevante?
- existe ao menos uma fonte auditavel?
- a evidencia encontrada responde diretamente a pergunta do usuario?
- a explicacao cabe em linguagem simples?
- a comparacao com esse tipo de candidato e justa?
- ha criterio claro para dizer `evidencia insuficiente` quando necessario?

Se alguma resposta for `nao`, o sinal nao entra sem ressalva.

## 7. Quadro de Consolidacao da Rodada

| Sinal | Incumbente forte | Incumbente controverso | Ex-parlamentar | Desafiante | Parecer geral |
|---|---|---|---|---|---|
| Integridade |  |  |  |  |  |
| Coerencia |  |  |  |  |  |
| Nivel de evidencia |  |  |  |  |  |
| Aderencia a valores |  |  |  |  |  |

## 8. Saida Esperada da Rodada 1

Ao final desta rodada, o time deve conseguir afirmar:

- quais sinais ja podem sustentar validacao de incumbentes;
- quais sinais funcionam apenas com cautela;
- quais sinais ainda dependem de metodologia adicional;
- em quais cenarios o produto deve responder `evidencia insuficiente`;
- se a V1 deve começar por incumbentes antes de ampliar cobertura.

## 9. Proxima Decisao Depois da Rodada

Depois desta rodada, a equipe deve escolher entre:

1. seguir para uma rodada 2 com mais casos;
2. fechar o escopo da V1 apenas para incumbentes;
3. abrir uma frente editorial para watchlist tematica e aderencia a valores;
4. iniciar desenho de implementacao com o que ja se mostrou viavel.

## 10. Fichas da Rodada 1

### 10.1 Nikolas Ferreira

#### 10.1.1 Identidade

- nome consultado: Nikolas Ferreira
- nome resolvido: Nikolas Ferreira de Oliveira
- aliases encontrados: Nikolas Ferreira
- cargo alvo: deputado federal
- partido: PL
- UF: MG
- status: incumbente
- ids oficiais localizados: Camara dos Deputados `209787`
- risco de homonimo: baixo

#### 10.1.2 Fontes Testadas

| Fonte | Encontrou dados? | Tipo de dado | Qualidade inicial | Observacoes |
|---|---|---|---|---|
| Camara | sim | identidade, mandato, votacoes, proposicoes, comissoes e emendas | alta | principal fonte do caso; confirma mandato 2023-2027 |
| TSE | sim | decisoes e noticias oficiais sobre sancoes eleitorais de 2023 | alta | forte para integridade; nao foi localizada ficha indexavel de candidatura nesta rodada |
| TCU | parcial | mencoes em pesquisa textual | baixa | sem decisao nominal clara de contas irregulares ou sancao pessoal nesta busca |
| Transparencia | sim | emendas parlamentares atribuidas ao nome | media | util para rastrear recursos, nao para concluir integridade sozinho |
| Fonte complementar 1 | sim | historico institucional anterior na CMBH | media | util para identidade e historico |
| Fonte complementar 2 | sim | trilha oficial complementar do TSE | alta | reforca camada de integridade eleitoral |

#### 10.1.3 Sinal: Integridade

- evidencias encontradas: TSE informou em 28/03/2023 manutencao de multa de R$ 30 mil e exclusao definitiva de conteudo; TSE informou em 11/05/2023 multa individual por propaganda irregular e desinformativa nas Eleicoes 2022
- classificacao das evidencias: sancoes eleitorais oficiais; nao confundir com condenacao criminal ou julgamento de contas
- leitura inicial: ha alerta oficial relevante de integridade no campo eleitoral
- confianca: media
- decisao: alerta moderado

#### 10.1.4 Sinal: Coerencia

- evidencias encontradas: a Camara oferece historico robusto de presenca, votacoes nominais, proposicoes e atuacao em comissoes desde 2023
- classificacao das evidencias: a base oficial existe, mas nesta rodada nao houve pareamento entre declaracao rastreavel e voto ou proposicao especifica
- leitura inicial: ha material para testar coerencia, mas a conclusao substantiva ainda nao fecha de forma honesta
- confianca: media na existencia dos dados; baixa para concluir coerencia
- decisao: evidencia insuficiente

#### 10.1.5 Sinal: Nivel de Evidencia

- volume de sinais oficiais: alto para identidade e atuacao parlamentar; moderado para integridade
- diversidade de fontes: Camara, TSE, TCU, Transparencia, CMBH e fonte oficial complementar do TSE
- atualidade: Camara e Transparencia com dados recentes; TSE com decisoes de 2023 ainda disponiveis e atualizadas em 2025
- proximidade com a pergunta do usuario: boa para identidade e integridade; parcial para coerencia e aderencia
- classificacao final: media evidencia

#### 10.1.6 Sinal: Aderencia a Valores

- tema ou prioridade testada: nao definido nesta rodada
- watchlist usada: nenhuma watchlist tematica curada aplicada
- evidencias encontradas: apenas historico bruto de atuacao; sem matching editorial auditavel com prioridades do usuario
- leitura inicial: nao e honesto concluir aderencia sem watchlist e curadoria
- confianca: baixa
- decisao: depende de watchlist e curadoria; evidencia insuficiente

#### 10.1.7 Parecer do Caso

- validacao de candidato: viavel
- comparacao com incumbentes: viavel
- comparacao com desafiantes: cobertura oficial melhor do que a de um desafiante tipico, por haver mandato federal observavel
- observacao final: o caso ja apresenta alerta oficial moderado de integridade no TSE; coerencia e aderencia a valores nao devem ser fechadas sem recorte tematico e watchlist

### 10.2 Erika Hilton

#### 10.2.1 Identidade

- nome consultado: Erika Hilton
- nome resolvido: Erika Hilton
- aliases encontrados: Erika Hilton; ERIKA SANTOS SILVA
- cargo alvo: deputado federal
- partido: PSOL-SP | Federacao PSOL-REDE
- UF: SP
- status: incumbente
- ids oficiais localizados: Camara `220645`
- risco de homonimo: baixo

#### 10.2.2 Fontes Testadas

| Fonte | Encontrou dados? | Tipo de dado | Qualidade inicial | Observacoes |
|---|---|---|---|---|
| Camara | sim | perfil parlamentar, atividade legislativa, comissoes e gastos | forte oficial | mandato 2023-2027; nome civil ERIKA SANTOS SILVA |
| TSE | parcial | candidatura, contas e certidoes | insuficiente | registro individual nao confirmado com seguranca nesta passada |
| TCU | sim | representacao e acordao | forte oficial | Acordao 1690/2025 registrou ausencia de indicios suficientes para processar pedido |
| Transparencia | sim | emendas e empenhos | forte oficial | localizadas emendas 202443680020, 202443680017, 202543680001 e empenho 2024NE000022 |
| Fonte complementar 1 | sim | inteiro teor do PL 4224/2023 | forte oficial | proposicao de autoria ligada a direitos reprodutivos |
| Fonte complementar 2 | sim | detalhe de empenho 2024NE000022 | oficial parcial | util para rastreio material, nao basta sozinha para inferir integridade |

#### 10.2.3 Sinal: Integridade

- evidencias encontradas: no TCU houve representacao formal sobre a emenda 43680020; o Tribunal registrou que a peca inicial nao apresentava indicios suficientes de irregularidade ou ilegalidade para processamento; no Portal da Transparencia foram localizados rastros de emendas e empenhos associados ao nome
- classificacao das evidencias: forte oficial para existencia e desfecho do acordao; oficial parcial para rastreio orcamentario; insuficiente para concluir ausencia total de alertas em todo o ecossistema oficial
- leitura inicial: nesta rodada nao apareceu alerta oficial robusto que sustente juizo negativo de integridade; apareceu controversia formalizada e apreciada pelo TCU com desfecho desfavoravel a acusacao
- confianca: media
- decisao: entra com cautela

#### 10.2.4 Sinal: Coerencia

- evidencias encontradas: atuacao em comissoes de direitos humanos e direitos da mulher; autoria do PL 4224/2023; emendas no Portal da Transparencia em direitos LGBTQIA+ e autonomia economica das mulheres
- classificacao das evidencias: forte oficial
- leitura inicial: ha alinhamento observavel entre agenda publica associada ao nome e atos formais localizados em fontes oficiais
- confianca: media
- decisao: entra

#### 10.2.5 Sinal: Nivel de Evidencia

- volume de sinais oficiais: medio-alto
- diversidade de fontes: boa em Camara, TCU e Transparencia; TSE permaneceu pendente
- atualidade: boa; ha registros de 2023, 2024, 2025 e pagina parlamentar ativa em 2026
- proximidade com a pergunta do usuario: alta para identidade e coerencia; media para integridade; baixa para aderencia a valores sem watchlist
- classificacao final: oficial parcial

#### 10.2.6 Sinal: Aderencia a Valores

- tema ou prioridade testada: direitos humanos e direitos LGBTQIA+
- watchlist usada: nao consolidada nem publica nesta rodada
- evidencias encontradas: ha material oficial potencialmente relevante, mas a traducao disso para aderencia a valores ainda depende de watchlist e curadoria auditavel
- leitura inicial: nao concluir nesta rodada
- confianca: insuficiente
- decisao: entra depois

#### 10.2.7 Parecer do Caso

- validacao de candidato: viavel com cautela
- comparacao com incumbentes: viavel com cautela
- comparacao com desafiantes: parcial
- observacao final: caso bom para V1 em identidade e coerencia; integridade permite leitura cautelosa com base oficial; TSE ainda ficou incompleto nesta passada e aderencia a valores segue dependente de watchlist e curadoria

### 10.3 Fred Linhares

#### 10.3.1 Identidade

- nome consultado: Fred Linhares
- nome resolvido: Davys Frederico Teixeira Linhares
- aliases encontrados: Fred Linhares
- cargo alvo: deputado federal
- partido: Republicanos
- UF: DF
- status: incumbente
- ids oficiais localizados: deputado federal na Camara `220534`
- risco de homonimo: baixo

#### 10.3.2 Fontes Testadas

| Fonte | Encontrou dados? | Tipo de dado | Qualidade inicial | Observacoes |
|---|---|---|---|---|
| Camara | sim | perfil parlamentar, biografia, proposicoes, votacoes, emendas e gastos | forte oficial | identidade e mandato resolvidos com clareza; ha historico legislativo observavel |
| TSE | parcial | evidencia eleitoral e contas via Justica Eleitoral | oficial parcial | nao foi localizada pagina nominal limpa do TSE ou DivulgaCand nesta busca |
| TCU | nao | busca nominal | insuficiente | sem retorno nominal auditavel nas buscas testadas |
| Transparencia | sim | emendas parlamentares e documentos relacionados | forte oficial | ha registros nominais de emendas de 2024 e 2025 |
| Fonte complementar 1 | sim | TRE-DF, prestacao de contas eleitoral | forte oficial | achado central para integridade |
| Fonte complementar 2 | nao acionada | - | - | nao foi necessaria para fechar identidade e sinal inicial |

#### 10.3.3 Sinal: Integridade

- evidencias encontradas: no TRE-DF, o candidato eleito Davys Frederico Teixeira Linhares teve contas de 2022 aprovadas com ressalvas; houve apontamentos de atraso em relatorio financeiro, falhas na parcial e irregularidades em despesas com recursos publicos; o voto determinou recolhimento de R$ 15.851,28 ao Tesouro Nacional
- classificacao das evidencias: forte oficial
- leitura inicial: existe sinal oficial relevante de integridade eleitoral e contabil; nao equivale, por si so, a condenacao criminal ou inelegibilidade, mas tambem nao e sinal neutro
- confianca: alta
- decisao: entra com cautela

#### 10.3.4 Sinal: Coerencia

- evidencias encontradas: o perfil oficial da Camara o apresenta como defensor das mulheres; na Camara ha proposicoes autorais alinhadas a esse eixo, como PL 2552/2023 e PL 5695/2023, alem de propostas sobre protecao de criancas e adolescentes
- classificacao das evidencias: oficial parcial
- leitura inicial: ha sinal tematico inicial de coerencia entre discurso publico e agenda autoral, mas esta rodada nao fechou cruzamento robusto entre discurso e votos nominais em temas curados
- confianca: media
- decisao: evidencia insuficiente para juizo forte; no maximo, coerencia parcial

#### 10.3.5 Sinal: Nivel de Evidencia

- volume de sinais oficiais: medio
- diversidade de fontes: media a boa
- atualidade: boa, com dados da Camara e Transparencia em 2024-2026 e Justica Eleitoral de 2022 com atualizacao em 21/02/2025
- proximidade com a pergunta do usuario: alta para identidade e integridade; media para coerencia; baixa para aderencia a valores
- classificacao final: media evidencia

#### 10.3.6 Sinal: Aderencia a Valores

- tema ou prioridade testada: nao definido nesta rodada
- watchlist usada: nenhuma metodologia tematica explicita aplicada
- evidencias encontradas: insuficientes para afirmar aderencia a valores sem metodologia tematica
- leitura inicial: ainda depende de watchlist e curadoria
- confianca: insuficiente
- decisao: entra depois

#### 10.3.7 Parecer do Caso

- validacao de candidato: viavel com cautela
- comparacao com incumbentes: viavel com cautela
- comparacao com desafiantes: parcial
- observacao final: identidade resolvida com seguranca e ha evidencia oficial suficiente para um parecer inicial; o principal achado e um sinal oficial de integridade em contas eleitorais com ressalvas; coerencia ainda precisa de cruzamento tematico mais forte com votos nominais; aderencia a valores permanece dependente de watchlist e curadoria

### 10.4 Ricardo Cappelli

#### 10.4.1 Identidade

- nome consultado: Ricardo Cappelli
- nome resolvido: Ricardo Garcia Cappelli
- aliases encontrados: Ricardo Cappelli; Ricardo Garcia Cappelli
- cargo alvo: deputado federal
- partido: evidencia insuficiente em fonte oficial prioritaria consultada
- UF: DF como eixo de atuacao publica recente observavel; UF eleitoral nao confirmada em fonte oficial prioritaria
- status: desafiante ou figura publica sem mandato federal atual
- ids oficiais localizados: CPF mascarado `***.320.407-**` no Portal da Transparencia; cargo institucional de presidente da ABDI; registros oficiais no MJSP
- risco de homonimo: baixo

#### 10.4.2 Fontes Testadas

| Fonte | Encontrou dados? | Tipo de dado | Qualidade inicial | Observacoes |
|---|---|---|---|---|
| Camara | sim | mencoes em noticias/eventos | oficial parcial | nao localizei perfil parlamentar nem mandato |
| TSE | nao | candidatura, contas ou filiacao | insuficiente | nao localizei pagina nominal util nesta rodada |
| TCU | sim | ocorrencias nominais e julgamento historico | forte oficial | destaque para contas regulares com quitacao plena |
| Transparencia | sim | vinculos com governo federal e viagens | forte oficial | trilha auditavel de atuacao publica |
| Fonte complementar 1 | sim | bio institucional na ABDI | forte oficial | cargo atual de presidente da ABDI |
| Fonte complementar 2 | sim | cargos no MJSP e intervencao federal no DF | forte oficial | confirma atuacao publica recente |

#### 10.4.3 Sinal: Integridade

- evidencias encontradas: Portal da Transparencia mostra vinculos auditaveis com a administracao federal; TCU localizou julgamento historico com contas regulares e quitacao plena; nao apareceu sancao formal nominal conclusiva na varredura curta
- classificacao das evidencias: oficial parcial
- leitura inicial: ha lastro oficial suficiente para dizer que existe trilha auditavel e nenhum red flag formal forte apareceu nas fontes priorizadas; isso nao equivale a atestado amplo de ausencia de problemas
- confianca: media
- decisao: entra com cautela

#### 10.4.4 Sinal: Coerencia

- evidencias encontradas: ha coerencia de trajeto em cargos executivos publicos federais e paraestatais, mas nao ha historico legislativo ou votacoes para aplicar o sinal principal da V1
- classificacao das evidencias: insuficiente
- leitura inicial: o caso nao entrega base oficial suficiente para medir coerencia politico-legislativa de forma justa
- confianca: baixa
- decisao: entra depois

#### 10.4.5 Sinal: Nivel de Evidencia

- volume de sinais oficiais: medio
- diversidade de fontes: boa para identidade e cargos publicos; fraca para camada eleitoral
- atualidade: alta, com registros oficiais de 2024 a 2026
- proximidade com a pergunta do usuario: media para identidade e integridade; baixa para comparacao eleitoral
- classificacao final: oficial parcial

#### 10.4.6 Sinal: Aderencia a Valores

- tema ou prioridade testada: nao aplicavel nesta rodada
- watchlist usada: nenhuma
- evidencias encontradas: nao validadas
- leitura inicial: ainda depende de watchlist tematica e curadoria editorial
- confianca: insuficiente
- decisao: entra depois

#### 10.4.7 Parecer do Caso

- validacao de candidato: parcial
- comparacao com incumbentes: nao viavel
- comparacao com desafiantes: parcial
- observacao final: identidade civil e institucional foi resolvida com boa seguranca em fontes oficiais, mas a camada eleitoral ficou insuficiente nesta rodada, especialmente em TSE; o caso testa bem o limite inferior de comparabilidade e reforca a necessidade de resposta explicita de `evidencia insuficiente` quando a pergunta exigir filiacao, candidatura ou historico eleitoral confirmado
