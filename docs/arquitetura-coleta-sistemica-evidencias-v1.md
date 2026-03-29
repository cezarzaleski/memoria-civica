---
title: Arquitetura de Coleta Sistemica de Evidencias da V1
date: 2026-03-28
status: draft
---

# Arquitetura de Coleta Sistemica de Evidencias da V1

## 1. Objetivo

Definir como os dados da V1 podem ser obtidos de forma repetivel, auditavel e suficientemente sistemica para sustentar os sinais do produto.

Esta arquitetura responde:

- o que da para buscar de forma sistemica hoje;
- o que depende de curadoria;
- o que depende de revisao manual;
- o que nao vale automatizar na V1.

## 2. Principio Central

A coleta da V1 deve ser desenhada por `pergunta -> sinal -> evidencia -> fonte`.

Nao por disponibilidade de dataset.

O sistema so deve consultar o que for necessario para:

- resolver identidade;
- coletar evidencias fortes ou medias;
- calcular sinais explicaveis;
- montar resposta com fontes.

## 3. Pipeline Logico de Coleta

### Etapa 1: Resolver identidade

Entrada:

- nome informado pelo usuario
- cargo alvo
- UF opcional

Saida:

- candidato resolvido com ids oficiais disponiveis
- status: incumbente, ex-parlamentar ou desafiante

### Etapa 2: Selecionar plano de coleta

O sistema decide quais fontes consultar com base no perfil resolvido.

Exemplo:

- incumbente federal: Camara primeiro
- nome sem mandato federal: TSE e fontes institucionais primeiro

### Etapa 3: Coletar evidencias por sinal

Cada sinal puxa somente as fontes necessarias.

### Etapa 4: Classificar forca da evidencia

O sistema marca cada item como:

- forte oficial
- oficial parcial
- complementar confiavel
- fraca
- insuficiente

### Etapa 5: Consolidar resposta

O sistema devolve:

- sinais
- confianca
- fontes
- lacunas

## 4. Tabela de Coleta por Sinal

| Sinal | Fonte primaria | Fonte secundaria | Como consultar | Chave de resolucao | Frequencia | Fallback | Risco |
|---|---|---|---|---|---|---|---|
| Identidade do incumbente | Camara | TSE | busca nominal e perfil parlamentar | nome + UF + id parlamentar | sob demanda | validacao manual se ambiguidade | homonimo |
| Identidade do nao incumbente | TSE | fontes institucionais oficiais | busca nominal em base eleitoral e institucional | nome + UF + contexto institucional | sob demanda | resposta parcial | baixa cobertura |
| Integridade eleitoral | TSE / TRE | TCU | decisoes, noticias oficiais, contas | nome resolvido + contexto eleitoral | sob demanda com cache | revisao manual em caso sensivel | confundir tipos de sancao |
| Integridade administrativa | TCU | Transparencia | pesquisa nominal por acordaos, sancoes e trilhas oficiais | nome resolvido | sob demanda com cache | marcar como parcial | falso positivo nominal |
| Coerencia de incumbente | Camara | fontes oficiais complementares | votos nominais, proposicoes, comissoes, autoria | id parlamentar | sob demanda | evidencia insuficiente | interpretacao sem recorte tematico |
| Nivel de evidencia | metacamada interna | todas as fontes usadas | contagem e qualificacao dos itens coletados | id do caso | em toda consulta | n/a | score opaco se mal desenhado |
| Aderencia a valores | watchlist tematica + Camara | TSE e fontes complementares | matching entre tema e evidencias permitidas | id do caso + tema | sob demanda | evidencia insuficiente | arbitrariedade editorial |

## 5. O Que Ja Parece Sistematizavel na V1

### 5.1 Identidade de incumbentes

Ja parece sistematizavel com boa confianca:

- resolver deputado federal na Camara;
- complementar com TSE para dados eleitorais e cadastrais;
- obter partido, UF, mandato e id parlamentar;
- usar isso como ancora da coleta.

### 5.2 Historico legislativo de incumbentes

Ja parece sistematizavel:

- votacoes nominais;
- proposicoes;
- comissoes;
- parte da atuacao formal.

### 5.3 Trilhas oficiais de integridade

Ja parece parcialmente sistematizavel:

- decisoes e noticias oficiais da Justica Eleitoral;
- dados de candidatura, contas e bens do TSE quando disponiveis;
- acordaos e buscas nominais do TCU;
- rastros oficiais no Portal da Transparencia.

Observacao:

essa camada ainda exige taxonomia clara para nao misturar tipos diferentes de alerta.

### 5.4 Nivel de evidencia

Ja parece totalmente sistematizavel:

- quantas fontes foram encontradas;
- quao oficiais sao;
- quao proximas estao da pergunta do usuario;
- quao atualizadas estao.

## 6. O Que Ainda Depende de Curadoria

### 6.1 Aderencia a valores

Nao sai automaticamente da fonte.

Precisa de:

- watchlist tematica;
- regra editorial publica;
- criterio de inclusao e exclusao;
- teste com nomes reais.

### 6.2 Coerencia substantiva

Ter votos e proposicoes nao basta.

Precisa de:

- recorte tematico;
- declaracoes publicas rastreaveis;
- regra para comparar discurso e pratica.

## 7. O Que Ainda Depende de Revisao Manual

### 7.1 Casos sensiveis de integridade

Quando a fonte apontar:

- sancao;
- processo;
- controversia juridica;
- representacao;

Pode ser necessario revisar manualmente para classificar corretamente.

### 7.2 Ambiguidade de identidade

Quando houver:

- homonimo;
- nome incompleto;
- partido ou UF incertos;
- transicao entre vida institucional e eleitoral.

### 7.3 Uso de jornalismo complementar

Na V1, jornalismo nao deve entrar automaticamente como base principal do sinal.

Se entrar, o ideal e passar por criterio editorial.

## 8. O Que Nao Vale Automatizar na V1

- ranking absoluto de melhores candidatos;
- leitura automatica ampla de redes sociais;
- inferencia de valores sem watchlist;
- conclusoes fortes sobre integridade a partir de manchetes ou sinais indiretos;
- comparacao plena entre incumbentes e desafiantes como se o dado fosse equivalente.

## 9. Estrutura Minima do Registro de Evidencia

Cada evidencia coletada deve poder ser registrada assim:

```json
{
  "person_id": "",
  "signal_type": "",
  "source_name": "",
  "source_url": "",
  "collected_at": "",
  "fact_date": "",
  "evidence_type": "",
  "strength": "",
  "summary": "",
  "notes": ""
}
```

Isso basta para:

- auditar a origem;
- recalcular sinais;
- montar explicacoes;
- revisar classificacoes depois.

## 10. Modo de Operacao Recomendado na V1

### 10.1 Sob demanda

Buscar evidencias quando o usuario consultar um nome.

Vantagem:

- menor custo inicial;
- menor necessidade de ingestao massiva;
- aderente ao pivot do produto.

Regra complementar:

- para incumbentes, consultar Camara e TSE como dupla principal;
- para nao incumbentes, priorizar TSE e fontes institucionais oficiais;
- usar TCU, Transparencia e outras fontes como camadas adicionais por sinal.

### 10.2 Cache seletivo

Persistir apenas:

- identidade resolvida;
- evidencias coletadas recentemente;
- classificacoes ja feitas;
- temas mais consultados.

Vantagem:

- acelera repeticao;
- evita depender de ETL pesado;
- permite revisao posterior.

### 10.3 Revisao assistida

Casos ambiguos ou sensiveis devem ser marcados para revisao humana ou editorial.

## 11. Decisao Estrategica

A V1 nao precisa de um pipeline massivo para nascer.

Ela precisa de:

- boa resolucao de identidade;
- consultas sob demanda a fontes oficiais prioritarias;
- um registro simples de evidencias;
- regras claras de classificacao;
- resposta honesta quando faltar dado.

## 12. Conclusao

Sim, a rodada 1 ja mostrou que parte relevante da coleta pode ser feita de forma sistemica, especialmente para:

- identidade de incumbentes;
- historico legislativo;
- trilhas oficiais iniciais de integridade;
- nivel de evidencia.

Mas a rodada tambem mostrou que:

- aderencia a valores ainda depende de watchlist;
- coerencia substantiva depende de recorte tematico;
- nao incumbentes exigem mais cautela;
- e ha uma camada de classificacao sensivel que nao deve ser automatizada sem criterio editorial.
