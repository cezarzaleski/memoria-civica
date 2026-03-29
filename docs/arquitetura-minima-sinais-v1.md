---
title: Arquitetura Minima de Sinais da V1
date: 2026-03-28
status: draft
---

# Arquitetura Minima de Sinais da V1

## 1. Objetivo

Definir a menor arquitetura capaz de sustentar a V1 do Memoria Civica como ferramenta de checagem civica para escolha consciente de candidatos a deputado federal.

A arquitetura deve responder a pergunta do usuario com:

- evidencia suficiente;
- explicacao curta;
- fontes verificaveis;
- tratamento honesto de incerteza.

## 2. Principio Central

A arquitetura nao parte de datasets. Ela parte da pergunta do usuario.

Fluxo logico:

1. usuario faz uma pergunta;
2. o sistema identifica quais sinais sao necessarios;
3. o sistema busca evidencias nas fontes certas;
4. os sinais sao calculados com regras explicaveis;
5. o produto devolve semaforo, motivos, alertas e fontes.

## 3. Pergunta Canonica da V1

Pergunta principal:

`Esse candidato a deputado federal realmente me representa?`

Subperguntas:

- ha alertas relevantes de integridade?
- ha historico observavel coerente com o que ele diz?
- existe evidencia suficiente para avaliar esse nome?
- o historico conhecido se aproxima das prioridades do usuario?

## 4. Camadas da Arquitetura

### 4.1 Identity Layer

Responsavel por resolver quem esta sendo avaliado.

Campos minimos:

- nome canonico
- aliases de nome
- cargo
- partido
- UF
- status de incumbencia
- ids oficiais disponiveis por fonte

Funcao:

- evitar ambiguidade de nomes;
- conectar o mesmo ator politico em fontes diferentes;
- distinguir incumbente, ex-parlamentar e desafiante.

### 4.2 Evidence Layer

Responsavel por armazenar fatos coletados.

Cada item de evidencia deve ter:

- fonte
- URL ou referencia oficial
- data de coleta
- data do fato
- tipo de evidencia
- ator politico associado
- escopo tematico
- grau de confianca
- observacao metodologica, quando necessario

Tipos iniciais de evidencia:

- voto nominal
- proposicao associada
- orientacao partidaria
- despesa ou dado financeiro oficial
- dado cadastral de candidatura
- prestacao de contas
- alerta oficial de integridade
- declaracao publica rastreavel
- cobertura jornalistica complementar

### 4.3 Signal Layer

Responsavel por transformar evidencias em sinais interpretaveis.

Sinais da V1:

- integridade
- coerencia
- nivel de evidencia
- aderencia a valores

Cada sinal precisa ter:

- resultado
- justificativa curta
- evidencias usadas
- nivel de confianca
- limitacoes aplicaveis

### 4.4 Explanation Layer

Responsavel por montar a resposta para o usuario.

Saida minima:

- semaforo geral
- status por dimensao
- 3 a 5 motivos curtos
- alertas
- nivel de confianca
- fontes abertas

### 4.5 Experience Layer

Responsavel por encaixar a logica em fluxos de produto.

Fluxos da V1:

- validar um candidato
- comparar candidatos
- descoberta guiada limitada

## 5. Sinais Minimos da V1

### 5.1 Integridade

Pergunta que responde:

`Ha sinais oficiais relevantes que exigem cautela?`

Entradas possiveis:

- contas irregulares em base oficial
- sancoes oficiais
- problemas formais de prestacao de contas
- outros alertas publicos com classificacao juridica clara

Saida esperada:

- sem alerta relevante
- alerta moderado
- alerta grave
- evidencia insuficiente

Regra:

Nunca misturar condenacao, investigacao, processo e cobertura narrativa no mesmo balde.

### 5.2 Coerencia

Pergunta que responde:

`O historico observavel combina com o posicionamento publico?`

Entradas possiveis:

- votos nominais
- proposicoes apoiadas
- orientacoes seguidas ou contrariadas
- declaracoes publicas rastreaveis

Saida esperada:

- coerente
- parcialmente coerente
- incoerente
- evidencia insuficiente

Regra:

Para nao incumbentes, a coerencia deve operar em regime de baixa confianca, porque o historico observavel tende a ser menor.

### 5.3 Nivel de Evidencia

Pergunta que responde:

`Ha dados suficientes para avaliar esse nome com seriedade?`

Entradas possiveis:

- volume de sinais oficiais
- diversidade de fontes
- atualidade
- proximidade entre evidencia e pergunta do usuario

Saida esperada:

- alta evidencia
- media evidencia
- baixa evidencia
- evidencia insuficiente

Regra:

Esse sinal nao julga o candidato. Ele julga a capacidade do produto de avaliar o candidato.

### 5.4 Aderencia a Valores

Pergunta que responde:

`O historico conhecido se aproxima das prioridades declaradas pelo usuario?`

Entradas possiveis:

- prioridades do usuario
- watchlist tematica curada
- votos e posicionamentos vinculados a temas
- sinais complementares para casos sem mandato

Saida esperada:

- alta aderencia
- aderencia parcial
- baixa aderencia
- evidencia insuficiente

Regra:

Esse sinal depende de uma camada editorial publica e auditavel. Sem watchlist tematica bem definida, a aderencia vira arbitrariedade.

## 6. Semaforo da V1

O semaforo geral deve ser derivado dos sinais, sem esconder a composicao.

Logica recomendada:

- `vermelho`: alerta grave de integridade ou combinacao forte de incoerencia com boa evidencia
- `amarelo`: aderencia parcial, alertas moderados ou baixa confianca
- `verde`: sem alertas graves conhecidos, historico suficientemente coerente e boa evidencia
- `cinza`: evidencia insuficiente para conclusao minimamente honesta

Regra:

Cinza nao e erro. Cinza e resposta valida do produto.

## 7. Regras de Decisao

### 7.1 Regra de Forca

Hierarquia base:

- fez
- apoiou
- disse

### 7.2 Regra de Comparabilidade

Nao comparar incumbente e desafiante como se tivessem o mesmo tipo de evidencias.

### 7.3 Regra de Transparencia

Todo resultado precisa responder:

- com base em que?
- com quanta confianca?
- o que ficou de fora?

### 7.4 Regra de Exclusao

Se a evidencia nao for auditavel, explicavel ou comparavel, ela nao entra no semaforo.

## 8. Interfaces Logicas

### 8.1 Input de Produto

- nome do candidato
- cargo
- UF opcional
- prioridades do usuario, quando houver

### 8.2 Output de Produto

- candidato resolvido
- semaforo geral
- sinais por dimensao
- lista de motivos
- lista de alertas
- conjunto de fontes

### 8.3 Output Interno Esperado

Estrutura conceitual:

```json
{
  "candidate": {},
  "signals": {
    "integrity": {},
    "coherence": {},
    "evidence_level": {},
    "values_fit": {}
  },
  "overall": {
    "traffic_light": "yellow",
    "confidence": "medium"
  },
  "reasons": [],
  "alerts": [],
  "sources": []
}
```

## 9. Ordem Recomendada de Implementacao Conceitual

1. resolver identidade do candidato
2. coletar evidencias oficiais minimas
3. calcular `nivel de evidencia`
4. calcular `integridade`
5. calcular `coerencia`
6. calcular `aderencia a valores`
7. montar explicacao final

## 10. Limites da V1

A arquitetura minima da V1 nao deve tentar resolver:

- ranking absoluto de melhores candidatos;
- comparacao plena entre qualquer tipo de nome;
- leitura automatica ampla de jornalismo como base principal;
- conclusoes fortes quando a evidencia for fraca;
- recomendacao eleitoral direta.

## 11. Decisao Estrategica

Se for preciso simplificar mais, a ordem correta de corte e:

1. manter `integridade`
2. manter `nivel de evidencia`
3. manter `coerencia`
4. simplificar `aderencia a valores`

Isso porque a aderencia depende mais de curadoria editorial, enquanto integridade e evidencia sao a base minima para nao enganar o usuario.
