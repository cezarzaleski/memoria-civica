---
title: Memoria Civica 2026 - Discovery
date: 2026-03-28
status: draft
---

# Memoria Civica 2026

## 1. Product Thesis

Memoria Civica 2026 deve ajudar o cidadao a fazer uma escolha consciente para deputado federal, validando se um candidato realmente o representa com base em evidencias publicas verificaveis.

O produto nao deve nascer como portal de dados nem como recomendador eleitoral opaco. A proposta inicial e atuar como ferramenta de checagem civica para escolha consciente.

## 2. Core Insight

O papel desejado do produto e apoiar o cidadao a participar da escolha consciente de seus representantes, avaliando dados de fontes oficiais, redes sociais, material de campanha e jornalismo para chegar o mais perto possivel de uma melhor escolha informada.

## 3. Primary Promise

Antes de votar em um candidato a deputado federal, o usuario consegue responder:

- Esse candidato realmente me representa?
- O que ele fez, apoiou ou disse que ajuda a responder isso?
- Ha alertas relevantes de integridade, incoerencia ou baixa evidencia?

## 4. Primary Audience

O foco inicial e o cidadao comum que:

- ja tem um candidato em mente ou esta prestes a escolher;
- nao acompanha politica de forma profissional;
- quer uma resposta clara, curta e verificavel;
- precisa de linguagem popular e opcao de aprofundar nas fontes.

## 5. Initial Scope

- Cargo inicial: deputado federal
- Cenario principal: eleicoes gerais de 2026
- Recorte de dados inicial: incumbentes, ex-parlamentares relevantes e candidatos registrados no TSE quando disponiveis
- Possivel expansao posterior: deputado distrital do DF

## 6. Main Experience

### 6.1 Main Flow

Fluxo principal: validar um candidato que o usuario ja tem em mente.

Entrada:

- nome do candidato
- prioridades ou valores do usuario, quando necessario

Saida:

- semaforo explicavel
- 3 a 5 motivos curtos
- alertas relevantes
- nivel de confianca
- fontes para verificacao
- opcoes para comparar ou ver alternativas

### 6.2 Supporting Flows

- Descobrir nomes compativeis por valores e prioridades
- Comparar candidatos de forma explicavel

## 7. Evaluation Model

### 7.1 Guiding Rule

Ordem de confianca da evidencia:

- fez
- apoiou
- disse

### 7.2 Evaluation Dimensions

O produto deve expor separadamente:

- Integridade
- Coerencia entre discurso e pratica
- Nivel de evidencia
- Aderencia aos valores e prioridades do usuario

### 7.3 Initial Ranking Logic

1. Primeiro, aplicar um piso civico minimo
2. Depois, ordenar por aderencia ao usuario

### 7.4 Signal Weight Direction

Todos os sinais entram com pesos diferentes:

- Integridade: maior peso negativo
- Coerencia: peso medio-alto
- Nivel de evidencia: afeta confianca e posicao
- Aderencia ao usuario: entra depois do filtro minimo

## 8. Communication Principles

- Linguagem popular e direta
- Sem juridiques
- Sem tom panfletario
- Fontes e metodologia acessiveis para aprofundamento
- Resposta curta na superficie, rastreabilidade embaixo

## 9. Regulatory Framing

Enquadramento desejado para a v1:

- ferramenta de checagem civica para escolha consciente
- nao propaganda eleitoral
- nao pesquisa eleitoral
- nao recomendador opaco de voto

## 10. Initial Product Boundaries

### 10.1 In

- validacao de candidato
- comparacao explicavel
- uso de fontes oficiais como base
- uso complementar de jornalismo, redes sociais oficiais e campanha
- exibicao clara de incerteza e lacunas

### 10.2 Out

- pedido direto de voto
- ranking absoluto de melhores candidatos
- score unico opaco
- cobertura irrestrita de qualquer nome sem evidencia
- divulgacao agregada de preferencia politica de usuarios

### 10.3 Needs Legal And Technical Validation

- matching por valores em escala
- campanhas pagas
- alertas juridicos sensiveis
- uso ampliado de IA para sintese de candidatos
- integracoes adicionais nao oficiais

## 11. 2026 Roadmap

### Phase 1

Validar a tese de uso: o produto realmente ajuda o usuario a revisar sua escolha?

### Phase 2

Construir prototipo funcional de validacao com semaforo explicavel, fontes e comparacao basica.

### Phase 3

Expandir para descoberta orientada por valores e shortlist explicavel.

### Phase 4

Adaptar o produto para a janela eleitoral de 2026 com distribuicao e cobertura ampliadas.

## 12. Open Questions

- Quais sinais oficiais sao robustos o bastante para compor o semaforo?
- Como tratar candidatos com pouca vida publica sem parecer injusto ou arbitrario?
- Como classificar alertas de integridade sem misturar fatos juridicos fortes com ruido jornalistico?
- Qual formato de distribuicao inicial maximiza uso e confianca sem elevar demais o risco regulatorio?

## 13. Distribution Direction

### 13.1 Recommended Product Format

A recomendacao inicial para a v1 nao e chat puro e nem WhatsApp como produto principal.

O formato mais promissor e:

- landing educativa
- ferramenta web de comparacao guiada
- resultado explicavel com fontes
- link compartilhavel

### 13.2 Why This Format

- gera mais confianca do que um chat opaco
- e mais util do que uma landing so editorial
- e mais transparente do que um quiz isolado
- reduz risco reputacional em relacao a WhatsApp-first
- deixa o caminho aberto para evoluir depois para chat e automacoes

### 13.3 Recommended Initial Channels

- Instagram para topo de funil
- YouTube para explicacao e busca
- WhatsApp como canal de compartilhamento e retorno
- creators e organizacoes civicas como parceiros de credibilidade
- SEO para capturar demanda intencional

### 13.4 Distribution Message

Mensagem central sugerida:

Nao diz em quem votar. Ajuda voce a validar com base em prioridades e fontes.

### 13.5 Distribution Risks

- chat puro pode parecer manipulacao algoritmica
- quiz puro pode parecer simplificacao excessiva
- WhatsApp-first aumenta risco de associacao com spam e desinformacao
- coleta identificavel de preferencias politicas exige cautela de LGPD

## 14. Data Architecture Viability

### 14.1 Viable Core Sources

Para a v1, as fontes mais fortes sao oficiais e estruturadas:

- Camara dos Deputados para votos nominais, proposicoes, orientacoes e despesas
- TSE para candidaturas, bens, contas, coligacoes e campos cadastrais quando os dados de 2026 estiverem disponiveis
- TCU e Portal da Transparencia como apoio a alertas de integridade

### 14.2 Practical Limitation

Nao ha paridade entre incumbentes e desafiantes.

- incumbentes possuem historico legislativo rico
- desafiantes tendem a ter sinais mais declaratorios e financeiros

Isso significa que a v1 nao deve fingir comparabilidade plena entre todos os nomes.

### 14.3 Current Availability Risk

Em 28/03/2026, os dados publicos de candidaturas 2026 do TSE ainda nao estao abertos no portal consultado. O produto precisa nascer aceitando esse atraso como restricao real.

### 14.4 Minimum Data Model

Camadas recomendadas para a arquitetura pos-pivot:

- `identity`: nome, aliases, partido, UF, ids oficiais e status de incumbencia
- `evidence`: fatos coletados de fontes oficiais e complementares
- `signals`: integridade, coerencia, nivel de evidencia e aderencia a valores
- `explanations`: semaforo, motivos curtos, alertas e fontes
- `experience`: validacao, comparacao e descoberta guiada

### 14.5 Signal Logic For V1

- `Integridade`: alertas oficiais e red flags formais
- `Coerencia`: alinhamento entre votos, orientacoes e temas priorizados
- `Nivel de evidencia`: quantos sinais observacionais e oficiais sustentam a resposta
- `Aderencia a valores`: matching entre watchlist tematica e historico observavel

### 14.6 Product Rule

Se faltarem dados, o produto deve responder `evidencia insuficiente`, e nao inventar confianca.

### 14.7 Architectural Principle

A arquitetura de dados da v1 nao deve partir da existencia de um ETL proprio como premissa.

Ela deve ser desenhada de fora para dentro:

- pergunta do usuario
- evidencia necessaria para responder
- sinais derivados dessa evidencia
- explicacao final com fontes

Se houver persistencia local, ela deve atuar como cache, indexacao ou materializacao auxiliar, e nao como fundamento obrigatorio do produto.

### 14.8 Methodological Risks

- comparar incumbentes e desafiantes no mesmo score gera vies estrutural
- matching de identidade entre fontes pode gerar falso positivo
- mapear valores do usuario para votacoes exige curadoria editorial consistente
- votos e proposicoes nao cobrem tudo o que importa sobre representacao politica

## 15. Working Recommendation

### 15.1 Product

Construir a v1 como:

- landing educativa
- comparacao guiada
- validacao de candidato com semaforo explicavel
- fontes oficiais como espinha dorsal

### 15.2 Data

Comecar com deputado federal incumbente e ex-parlamentar com historico forte, expandindo para candidatos TSE quando o dado oficial de 2026 estiver disponivel.

### 15.3 Distribution

Distribuicao inicial recomendada:

- Instagram
- YouTube
- compartilhamento via WhatsApp
- creators e organizacoes civicas
- SEO

### 15.4 Safety

Posicionar o produto como ferramenta de checagem civica e nao como recomendador eleitoral.
