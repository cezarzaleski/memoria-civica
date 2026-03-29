---
title: Fluxo Operacional da Consulta da V1
date: 2026-03-28
status: draft
---

# Fluxo Operacional da Consulta da V1

## 1. Objetivo

Definir o fluxo minimo de uma consulta da V1 do Memoria Civica, do nome digitado pelo usuario ate a resposta final com semaforo, razoes e fontes.

## 2. Pergunta Principal

Pergunta canonica da V1:

`Esse candidato a deputado federal realmente me representa?`

## 3. Entrada da Consulta

Entrada minima:

- nome do candidato

Entrada opcional:

- UF
- partido
- tema prioritario
- conjunto de prioridades do usuario

## 4. Fluxo Geral

```text
Usuario informa nome
-> resolver identidade
-> classificar tipo de candidato
-> selecionar plano de coleta
-> consultar fontes
-> registrar evidencias
-> classificar forca da evidencia
-> calcular sinais
-> calcular semaforo
-> montar resposta explicavel
```

## 5. Etapa 1: Resolver Identidade

### Objetivo

Descobrir exatamente quem esta sendo avaliado.

### Entradas

- nome digitado
- UF, se houver
- partido, se houver

### Saida esperada

- nome canonico
- aliases
- partido
- UF
- cargo
- status: incumbente, ex-parlamentar ou desafiante
- ids oficiais disponiveis
- nivel de ambiguidade

### Regra

Se houver ambiguidade forte de identidade:

- nao seguir para sinais;
- responder com necessidade de desambiguacao.

## 6. Etapa 2: Classificar Tipo de Candidato

### Objetivo

Escolher o caminho de coleta adequado.

### Tipos

- incumbente federal
- ex-parlamentar
- desafiante sem mandato federal atual

### Regra

O tipo define a profundidade e a ordem das consultas.

## 7. Etapa 3: Selecionar Plano de Coleta

### 7.1 Incumbente federal

Ordem recomendada:

1. Camara
2. TSE
3. TCU
4. Portal da Transparencia
5. jornalismo complementar, se necessario

### 7.2 Ex-parlamentar

Ordem recomendada:

1. TSE
2. historico legislativo disponivel
3. TCU
4. Portal da Transparencia
5. fontes institucionais complementares

### 7.3 Desafiante

Ordem recomendada:

1. TSE
2. fontes institucionais oficiais
3. TCU
4. Portal da Transparencia
5. jornalismo complementar, se necessario

## 8. Etapa 4: Consultar Fontes

### Fontes primarias

- mcp-brasil
- Camara
- TSE

### Fontes complementares

- TCU
- Portal da Transparencia
- DataJud, se fizer sentido no caso
- fontes institucionais oficiais

### Fontes editoriais

- RSS ou News com allowlist

### Regra

Jornalismo nao deve ser consultado antes de esgotar as fontes oficiais relevantes para o sinal.

## 9. Etapa 5: Registrar Evidencias

Cada item coletado deve registrar:

- pessoa avaliada
- sinal a que pode servir
- fonte
- URL
- data de coleta
- data do fato
- tipo de evidencia
- resumo curto
- forca inicial da evidencia

## 10. Etapa 6: Classificar Forca da Evidencia

Escala:

- forte oficial
- oficial parcial
- complementar confiavel
- fraca
- insuficiente

### Regra

A classificacao deve considerar:

- oficialidade
- atualidade
- proximidade com a pergunta
- comparabilidade

## 11. Etapa 7: Calcular Sinais

### 11.1 Integridade

Pergunta:

`Ha alertas oficiais relevantes que exigem cautela?`

### 11.2 Coerencia

Pergunta:

`O historico observavel combina com o posicionamento publico conhecido?`

### 11.3 Nivel de Evidencia

Pergunta:

`Ha base suficiente para avaliar esse nome com seriedade?`

### 11.4 Aderencia a Valores

Pergunta:

`O historico conhecido se aproxima das prioridades do usuario?`

### Regra

Se o candidato nao tiver base suficiente para um sinal:

- esse sinal retorna `evidencia insuficiente`

## 12. Etapa 8: Calcular Semaforo

### Estados

- verde
- amarelo
- vermelho
- cinza

### Regra recomendada

- `verde`: sem alertas graves conhecidos, boa evidencia e historico minimamente coerente
- `amarelo`: ha cautelas, lacunas ou sinais mistos
- `vermelho`: ha alerta grave ou combinacao forte de sinais negativos com boa evidencia
- `cinza`: evidencia insuficiente para conclusao honesta

## 13. Etapa 9: Montar Resposta

### Saida minima

- nome resolvido
- semaforo
- resumo curto
- 3 a 5 motivos
- alertas
- nivel de confianca
- fontes

### Exemplo conceitual

```json
{
  "candidate": "Nome",
  "traffic_light": "yellow",
  "confidence": "medium",
  "reasons": [],
  "alerts": [],
  "signals": {
    "integrity": "",
    "coherence": "",
    "evidence_level": "",
    "values_fit": ""
  },
  "sources": []
}
```

## 14. Regras de Resposta

### 14.1 Nunca esconder incerteza

Se faltar base:

- responder explicitamente `evidencia insuficiente`

### 14.2 Nunca usar jornalismo como prova principal de integridade

Jornalismo pode contextualizar, nao sentenciar.

### 14.3 Nunca comparar tipos desiguais sem explicacao

Incumbente e desafiante nao devem parecer equivalentes quando a densidade de evidencia for diferente.

### 14.4 Nunca colapsar tudo em score opaco

O usuario precisa ver:

- por que o resultado apareceu;
- com quais fontes;
- com quanta confianca.

## 15. Fluxo Especial para Ambiguidade

Se o nome nao puder ser resolvido com seguranca:

- pedir UF, partido ou contexto adicional;
- nao calcular sinais;
- nao tentar adivinhar.

## 16. Fluxo Especial para Evidencia Insuficiente

Se a coleta oficial nao trouxer base suficiente:

- retornar semaforo cinza;
- explicar o que faltou;
- indicar quais fontes nao confirmaram a avaliacao.

## 17. Decisao Estrategica

O fluxo da V1 deve nascer para consultas sob demanda.

Isso significa:

- sem ingestao massiva obrigatoria;
- sem pipeline pesado como premissa;
- com foco em responder bem cada consulta;
- com cache seletivo quando houver repeticao.
