---
title: Arquitetura Tecnica da V1
date: 2026-03-28
status: draft
---

# Arquitetura Tecnica da V1

## 1. Objetivo tecnico

A V1 deve responder uma consulta nominal sobre candidato a deputado federal com:

- semaforo
- sinais explicaveis
- fontes verificaveis
- grau de confianca

O sistema nasce como consulta sob demanda, e nao como pipeline massivo.

A unidade central do sistema e a pergunta do usuario, e nao o dataset.

## 2. Componentes da V1

### 2.1 CLI ou API de Consulta

Responsavel por:

- receber `nome` e, opcionalmente, `UF`, `partido` e `prioridades do usuario`;
- retornar payload explicavel pronto para UI ou CLI.

### 2.2 Orquestrador da Consulta

Responsavel por:

- coordenar o fluxo ponta a ponta;
- decidir plano de coleta conforme tipo de candidato e sinais necessarios.

### 2.3 Resolver de Identidade

Responsavel por:

- resolver nome canonico, aliases, cargo, partido, UF, status e IDs oficiais;
- bloquear a consulta quando houver ambiguidade forte.

### 2.4 Planejador de Coleta

Responsavel por:

- traduzir `perfil do candidato + pergunta` em lista minima de fontes e consultas;
- evitar chamadas desnecessarias.

### 2.5 Conectores de Fontes

Responsavel por:

- acessar `mcp-brasil`, APIs oficiais e fontes complementares;
- normalizar respostas externas.

### 2.6 Registro de Evidencias

Responsavel por:

- armazenar cada evidencia com origem, data, tipo, forca e vinculo com sinal e pessoa;
- permitir auditoria e reuso.

### 2.7 Classificador de Evidencia

Responsavel por:

- marcar cada item como `forte oficial`, `oficial parcial`, `complementar confiavel`, `fraca` ou `insuficiente`.

### 2.8 Motor de Sinais

Responsavel por:

- calcular `integridade`, `coerencia`, `nivel de evidencia` e `aderencia a valores`;
- sempre expor justificativa curta e lista de evidencias usadas.

### 2.9 Camada Editorial

Responsavel por:

- manter watchlist tematica e regras publicas de interpretacao;
- impactar o sinal de aderencia e complementos interpretativos.

### 2.10 Montador de Resposta

Responsavel por:

- converter sinais em semaforo, razoes, alertas, confianca e fontes.

## 3. Interfaces logicas

### 3.1 Entrada da consulta

```json
{
  "candidate_name": "string",
  "uf": "string?",
  "party": "string?",
  "user_priorities": ["string"]
}
```

### 3.2 Saida da consulta

```json
{
  "candidate": {
    "canonical_name": "string",
    "status": "incumbent|former|challenger",
    "party": "string?",
    "uf": "string?",
    "official_ids": {}
  },
  "traffic_light": "green|yellow|red|gray",
  "confidence": "high|medium|low",
  "summary": "string",
  "reasons": ["string"],
  "alerts": ["string"],
  "signals": {
    "integrity": {},
    "coherence": {},
    "evidence_level": {},
    "values_fit": {}
  },
  "sources": ["string"]
}
```

### 3.3 Registro de evidencia

```json
{
  "person_id": "string",
  "signal_type": "integrity|coherence|evidence_level|values_fit",
  "source_name": "string",
  "source_url": "string",
  "collected_at": "datetime",
  "fact_date": "date?",
  "evidence_type": "string",
  "strength": "strong_official|official_partial|complementary|weak|insufficient",
  "summary": "string",
  "notes": "string?"
}
```

## 4. Dependencias externas

### 4.1 Primarias

- `mcp-brasil` como gateway preferencial
- `API da Camara` para incumbentes e ex-parlamentares com historico legislativo
- `Dados Abertos do TSE` para identidade eleitoral, candidatura e contas

### 4.2 Complementares

- `Portal da Transparencia` para rastros administrativos e financeiros
- `TCU` para alertas formais de controle externo
- `DataJud` apenas como fonte complementar sob regra editorial estrita

### 4.3 Editoriais

- RSS ou News com allowlist de veiculos brasileiros
- nunca sustentam sozinhas semaforo de integridade

## 5. Responsabilidades por fluxo

### 5.1 Identity Layer

- resolver pessoa
- evitar homonimo

### 5.2 Evidence Layer

- coletar e registrar fatos rastreaveis

### 5.3 Signal Layer

- produzir leitura interpretavel
- nunca score opaco

### 5.4 Editorial Layer

- definir temas e regras de aderencia

### 5.5 Explanation Layer

- entregar resposta honesta, inclusive `cinza`

## 6. Modo de operacao sob demanda

Fluxo base:

- resolver identidade
- classificar candidato
- selecionar plano
- consultar fontes
- registrar evidencias
- classificar forca
- calcular sinais
- calcular semaforo
- montar resposta

### 6.1 Ordem de coleta

Para incumbente:

1. Camara
2. TSE
3. TCU
4. Transparencia
5. editorial, se necessario

Para ex-parlamentar:

1. TSE
2. historico legislativo
3. TCU
4. Transparencia

Para desafiante:

1. TSE
2. fontes institucionais
3. TCU
4. Transparencia
5. editorial, se necessario

### 6.2 Regra operacional

- so consultar o necessario para responder com honestidade
- se identidade falhar, parar
- se evidencia for insuficiente, responder `cinza`

## 7. Cache seletivo

Persistir somente:

- identidade resolvida
- evidencias recentes
- classificacoes ja produzidas
- watchlists e regras editoriais

### 7.1 Politica pratica

- `identity cache`: TTL maior, invalida por ciclo eleitoral ou mudanca partidaria
- `evidence cache`: TTL por fonte e sensibilidade do dado
- `signal cache`: deriva das evidencias e invalida junto com evidencia nova

### 7.2 Objetivo

- reduzir latencia
- evitar ETL pesado na V1
- permitir reuso auditavel em consultas repetidas

## 8. Riscos tecnicos

### 8.1 Resolucao de identidade

- homonimos
- nomes incompletos
- mudanca de partido ou UF

### 8.2 Assimetria entre candidatos

- incumbentes tem mais evidencia que desafiantes
- o sistema precisa explicitar essa desigualdade

### 8.3 Taxonomia de integridade

- misturar condenacao, investigacao, processo e mencao jornalistica quebra a confianca do produto

### 8.4 Dependencia de fontes externas

- APIs instaveis
- paginacao inconsistente
- mudancas de schema

### 8.5 Aderencia a valores

- sem watchlist publica e regras estaveis, o sinal vira arbitrariedade

### 8.6 Jornalismo complementar

- risco de superinterpretacao se entrar antes das fontes oficiais

### 8.7 Cache desatualizado

- pode devolver leitura antiga em contexto eleitoral sensivel

## 9. Proposta de implementacao minima

- `query-orchestrator`
- `source-connectors`
- `evidence-store`
- `signal-engine`
- `editorial-config`

Persistencia recomendada:

- banco relacional simples para identidade, evidencias, classificacoes e metadados de coleta

Regra de produto:

- CLI funcional primeiro
- UI apenas como camada de apresentacao

## 10. Decisao arquitetural da V1

A V1 deve ser:

- `query-first`
- `source-backed`
- `auditavel`
- `frugal`

Ela nao precisa de ingestao massiva para nascer.

Ela precisa de:

- resolucao confiavel de identidade
- coleta sob demanda por sinal
- armazenamento minimo de evidencias
- motor de sinais explicito
- resposta com limites visiveis
