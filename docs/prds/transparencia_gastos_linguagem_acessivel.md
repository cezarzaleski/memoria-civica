# 🔍 PRD — Transparência de Gastos e Linguagem Acessível

> "A democracia não funciona sem cidadãos informados. E informação que ninguém entende não é informação."

---

**Status:** Draft
**Autor:** Cezar Zaleski
**Data:** 2026-02-22

---

## 1. Visão do Produto

O Memória Cívica hoje funciona como um painel técnico-legislativo — um Diário Oficial com interface moderna. Exibe votações, placar e deputados, mas não gera engajamento cívico real porque:

1. A linguagem é inacessível para a maioria da população
2. Falta a camada de **accountability** — gastos e privilégios parlamentares
3. O dado bruto existe, mas falta a **narrativa** que conecta o cidadão à política

Esta PRD define duas evoluções complementares que transformam o produto de "consulta legislativa" para **ferramenta de cidadania ativa**:

- **Linguagem Acessível**: LLM traduz juridiquês legislativo para português simples
- **Transparência de Gastos**: Dados da Cota Parlamentar (CEAP) expostos no app

---

## 2. Público-Alvo

### 2.1 Dona Maria — Cidadã Comum

| Atributo | Descrição |
|----------|-----------|
| **Perfil** | Dona de casa, 45-65 anos, ensino médio |
| **Relação com política** | Pouco acompanha, pouco conhece, mas tem poder de voto |
| **Motivação** | Quer saber "o que muda pra mim" sem precisar entender juridiquês |
| **Frustração atual** | Abre o app, vê "PL 108/2022 — Dispõe sobre..." e fecha em 10 segundos |
| **Gatilho de engajamento** | Linguagem simples + impacto concreto ("vão mexer no preço do gás") |
| **Dispositivo** | Celular Android, conexão móvel |

### 2.2 Julia — Cidadã Engajada

| Atributo | Descrição |
|----------|-----------|
| **Perfil** | Advogada, 28-40 anos, acompanha política ativamente |
| **Relação com política** | Entende o sistema, indignada com privilégios e corrupção |
| **Motivação** | Cobrar accountability — "ninguém aguenta mais privilégios dessa categoria" |
| **Frustração atual** | Não consegue ver gastos do deputado dela, nem quem votou contra o partido |
| **Gatilho de engajamento** | Rankings de gastos + cruzamento voto x orientação de bancada |
| **Dispositivo** | iPhone/Desktop, busca dados para compartilhar em redes sociais |

---

## 3. Problemas Identificados

### 3.1 Feed atual não engaja nenhuma das personas

| Problema | Dona Maria | Julia |
|----------|-----------|-------|
| Linguagem de diário oficial nos cards | **Crítico** — não entende | Indiferente — entende |
| Categorias cívicas invisíveis no feed | **Crítico** — não filtra por tema | Útil |
| Sem página de deputados | Útil | **Crítico** — não busca o deputado dela |
| Sem dados de gastos parlamentares | Indiferente | **Crítico** — é o que mais quer ver |
| Explicação simplificada enterrada na página de detalhe | **Crítico** | Indiferente |
| Sem cruzamento voto x orientação de bancada | Indiferente | **Crítico** |

### 3.2 Dados existentes vs. dados necessários

| Dado | Existe no ETL | Existe no Frontend | Gap |
|------|--------------|-------------------|-----|
| Votações + Placar | Sim | Sim | — |
| Votos individuais | Sim | Sim (detalhe) | Falta destaque no feed |
| Orientações de bancada | Sim | Sim (detalhe) | Falta cruzamento com votos |
| Proposições + ementa | Sim | Sim | Falta tradução para linguagem simples |
| Categorias cívicas | Sim | Sim (detalhe) | Falta exibição no feed + filtro |
| Gastos parlamentares (CEAP) | **Não** | **Não** | **Gap completo** |
| Resumo em linguagem simples | **Não** | **Não** | **Gap completo** |

---

## 4. Funcionalidades Propostas

### 4.1 Linguagem Acessível (LLM Enrichment)

**Objetivo:** Toda proposição ganha uma versão em linguagem simples, gerada por LLM no ETL.

| Feature | Descrição | Persona principal |
|---------|-----------|-------------------|
| **Headline no card do feed** | Frase declarativa de até 120 chars em voz ativa: "Câmara aprova isenção de IR para quem ganha até 2 salários mínimos" | Dona Maria |
| **Resumo simples** | 2-3 parágrafos sem juridiquês, nível ensino médio | Dona Maria |
| **Impacto cidadão** | Lista de 2-4 mudanças concretas: "Seu IRPF na faixa de R$2.824 passa a ser isento" | Dona Maria |
| **Categorias no card do feed** | Tags coloridas visíveis: `Saúde` `Educação` `Seu bolso` | Dona Maria + Julia |
| **Filtro por categoria** | "Me mostra só o que mexe na saúde" | Dona Maria |

### 4.2 Transparência de Gastos Parlamentares

**Objetivo:** Expor dados da Cota Parlamentar (CEAP) de forma acessível e navegável.

| Feature | Descrição | Persona principal |
|---------|-----------|-------------------|
| **Página do deputado** (`/deputados/:id`) | Foto, partido, UF, histórico de votações, gastos | Julia |
| **Resumo de gastos mensal** | Total gasto, top categorias, comparação com média | Julia |
| **Detalhamento por categoria** | "Passagens aéreas: R$ X.XXX", "Combustível: R$ X.XXX" | Julia |
| **Ranking de gastos** | Top 10 deputados que mais gastaram no mês/ano | Julia |
| **Busca por deputado** | Por nome, partido ou UF — "meu deputado" | Julia + Dona Maria |
| **Link para nota fiscal** | URL do PDF original da Câmara | Julia |

---

## 5. Arquitetura de Informação (Proposta)

```
Memória Cívica
├── / (Feed)
│   ├── Card com headline em linguagem simples
│   ├── Tags de categoria cívica
│   ├── Filtro por categoria
│   └── Placar visual (sim/não/outros)
│
├── /votacoes/:id (Detalhe da Votação)
│   ├── Resumo simples + impacto cidadão     ← NOVO
│   ├── Placar detalhado
│   ├── Lista de votos por deputado
│   ├── Orientações de bancada
│   └── Categorias cívicas
│
├── /deputados (Lista de Deputados)           ← NOVO
│   ├── Busca por nome/partido/UF
│   └── Cards com foto + partido + UF + total gastos
│
└── /deputados/:id (Perfil do Deputado)       ← NOVO
    ├── Dados pessoais (foto, partido, UF, email)
    ├── Histórico de votações recentes
    ├── Resumo de gastos (CEAP)
    │   ├── Total mensal/anual
    │   ├── Breakdown por categoria
    │   └── Link para notas fiscais
    └── Comparação com média da casa
```

---

## 6. Requisitos Técnicos

### 6.1 Backend (ETL)

| Requisito | Detalhe |
|-----------|---------|
| ETL de gastos (CEAP) | Novo domínio `src/gastos/` seguindo padrão existente |
| Fonte de dados | CSV bulk: `dadosabertos.camara.leg.br/arquivos/deputadosDespesas/csv/` |
| Pipeline LLM | Nova fase no ETL batch, pós-classificação |
| Modelo LLM | GPT-4o-mini (custo ~R$ 0,15/mês para 100 proposições) |
| Tabela de enriquecimentos | `enriquecimentos_llm` com headline, resumo, impacto, confiança |

### 6.2 Frontend

| Requisito | Detalhe |
|-----------|---------|
| Card do feed reformulado | Headline LLM + tags de categoria + placar |
| Página de deputados | Componentes já existem (`DeputadoCard`, `DeputadoSearch`) |
| Página de perfil do deputado | Nova, com gastos + votações |
| Filtro por categoria no feed | Novo componente |

### 6.3 API

| Endpoint | Descrição |
|----------|-----------|
| `GET /api/v1/deputados/:id/gastos` | Gastos paginados com filtro por ano/mês/categoria |
| `GET /api/v1/deputados/:id/gastos/resumo` | Totais agregados por categoria e período |
| `GET /api/v1/proposicoes/:id/enriquecimento` | Headline + resumo + impacto gerados por LLM |
| `GET /api/v1/votacoes?categoria=saude` | Filtro de votações por categoria cívica |

---

## 7. Métricas de Sucesso

### 7.1 Engajamento

| Métrica | Estado atual (estimado) | Meta |
|---------|------------------------|------|
| Tempo médio na página | < 15s (feed incompreensível) | > 60s |
| Taxa de clique feed → detalhe | < 10% | > 30% |
| Páginas por sessão | 1-2 | > 4 |
| Retorno em 7 dias | < 5% | > 15% |

### 7.2 Acessibilidade

| Métrica | Como medir |
|---------|-----------|
| Legibilidade do headline | Índice de Flesch-Kincaid adaptado para PT-BR (meta: nível ensino médio) |
| Confiança LLM | % de proposições com `confianca >= 0.7` (meta: > 80%) |
| Cobertura de categorias | % de proposições com pelo menos 1 categoria (meta: > 90% com regex + LLM) |

### 7.3 Accountability

| Métrica | Como medir |
|---------|-----------|
| Cobertura de gastos | % de deputados com dados de CEAP carregados (meta: 100%) |
| Atualização | Defasagem máxima dos dados de gastos (meta: < 30 dias) |

---

## 8. Riscos e Mitigações

| Risco | Severidade | Mitigação |
|-------|-----------|-----------|
| LLM gera resumo incorreto ou tendencioso | Alta | Campo `confianca` + threshold de exibição (< 0.5 = não exibe); versionamento de prompt para auditoria |
| Custos de LLM escalam inesperadamente | Baixa | Volume previsível (~100 props/mês); custo < R$ 1/mês com GPT-4o-mini |
| Dados de CEAP atrasados na Câmara | Média | Exibir data da última atualização; alerta visual quando dados > 30 dias |
| Interpretação errônea de gastos (gasto legítimo vs. abuso) | Alta | Exibir dados brutos sem juízo de valor; link para nota fiscal original; comparação com média (não ranking de "piores") |
| Dependência de API externa da Câmara | Média | Cache ETag já implementado; fallback para último CSV baixado |

---

## 9. Fora de Escopo (MVP)

- Notificações push sobre votações
- Comparação entre legislaturas
- Dados do Senado Federal
- Integração com redes sociais (compartilhamento)
- Chat com IA sobre proposições
- Dados de emendas parlamentares (RP6-RP9)
- Salários individuais de assessores (indisponível via API)
- Análise de sentimento de discursos

---

## 10. Roadmap de Implementação

### Fase 1 — Dados de Gastos (ETL)

- [ ] Tech Spec 003 — ETL de Gastos Parlamentares
- [ ] Implementar domínio `src/gastos/`
- [ ] Migration + testes
- [ ] Integrar no `run_full_etl.py`

### Fase 2 — Enriquecimento LLM (ETL)

- [ ] Tech Spec 004 — Pipeline LLM
- [ ] Implementar tabela `enriquecimentos_llm`
- [ ] Prompt v1.0 + integração com GPT-4o-mini
- [ ] Testes + threshold de confiança

### Fase 3 — Frontend: Feed Acessível

- [ ] Reformular `VotacaoCard` com headline + tags
- [ ] Adicionar filtro por categoria cívica
- [ ] Exibir resumo simples + impacto na página de detalhe

### Fase 4 — Frontend: Deputados e Gastos

- [ ] Criar rota `/deputados` com busca
- [ ] Criar rota `/deputados/:id` com perfil + gastos
- [ ] Componente de resumo de gastos por categoria
- [ ] Ranking/comparação com média

---

## 11. Referências e Inspirações

| Projeto | Relevância |
|---------|-----------|
| **Operação Serenata de Amor** (OKFN Brasil) | Auditoria de gastos parlamentares com ML; mesma fonte de dados (CEAP) |
| **Plural Policy** (EUA) | LLM para simplificar legislação; modelo comercial de referência |
| **DW EU Parliament LLM** | Jornalistas usando LLM batch em dados parlamentares europeus |
| **Dados Abertos da Câmara** | Fonte oficial de todos os dados: `dadosabertos.camara.leg.br` |

---

_Última atualização: Fevereiro 2026_
_Autor: Cezar Zaleski — Status: Draft_
