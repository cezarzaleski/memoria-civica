# 📜 PRD — Memória Cívica

> "Democracia não é só votar. É lembrar, cobrar e participar."

---

## 1. Visão do Produto

### 1.1 Problema

O cidadão brasileiro:

- Não lembra o que seus deputados votaram

- Não entende o que significa cada votação na prática

- Não tem tempo de acompanhar o Congresso no dia a dia

- Não sabe como cobrar seus representantes

- Vota no escuro a cada 4 anos, baseado em promessas e não em fatos

Resultado: políticos sem accountability, reeleição de corruptos, e um ciclo vicioso de reclamação sem ação.

### 1.2 Solução

Memória Cívica é uma ferramenta que dá ao cidadão o poder de:

1. Lembrar — O que foi votado, quando, e como seu deputado votou

2. Entender — Em linguagem simples, o que cada decisão significa para sua vida

3. Cobrar — Contato direto com o parlamentar para questionar ou elogiar

4. Decidir — Na hora de votar, ter histórico completo, não promessas

### 1.3 North Star Metric

> "Quantos cidadãos consultaram o histórico de um deputado antes de votar?"

Métrica secundária: engajamento com funcionalidade de contato/cobrança.

---

## 2. Público-Alvo

### 2.1 Persona Principal: "O Cidadão Cansado"

Maria, 38 anos, professora

- Trabalha o dia todo, não tem tempo de acompanhar política

- Sabe que "tá tudo errado" mas não sabe exatamente o quê

- Quer fazer a coisa certa na hora de votar

- Se sente impotente: "meu voto não muda nada"

- Usa WhatsApp e Instagram, não lê jornal

Necessidades:

- Informação mastigada, sem juridiquês

- Acesso rápido, no celular

- Não quer virar "especialista em política", só quer o essencial

### 2.2 Persona Secundária: "O Engajado"

Pedro, 25 anos, universitário

- Já acompanha política, mas de forma fragmentada

- Quer dados concretos para argumentar

- Compartilha informações em redes sociais

- Potencial multiplicador

### 2.3 Antiusuário

- Jornalistas políticos (já têm ferramentas profissionais)

- Pesquisadores acadêmicos (precisam de dados brutos)

- Militantes partidários (buscam viés, não fatos)

---

## 3. Princípios de Design

### 3.1 Linguagem

- Sem juridiquês: "PL" vira "Projeto de Lei", com explicação

- Sem partidarismo: Fatos, não opiniões

- Consequência primeiro: "Isso significa que..." antes dos detalhes técnicos

### 3.2 Experiência

- Mobile-first: 80% do uso será no celular

- 3 toques até a informação: Máximo de fricção aceitável

- Compartilhável: Cada informação deve ser fácil de enviar no WhatsApp

### 3.3 Confiança

- Fonte sempre visível: Link para dados oficiais da Câmara

- Sem editorialização: O produto não diz se votação foi "boa" ou "ruim"

- Transparência: Explicar como os dados são obtidos

---

## 4. Roadmap de Funcionalidades

### 4.1 MVP (v1.0) — "Memória"

Objetivo: Cidadão consegue ver o histórico de votações de qualquer deputado.

|Funcionalidade|Descrição|Prioridade|

|---|---|---|

|Feed de Votações|Lista cronológica das votações do Plenário|P0|

|Página da Votação|Detalhes: o que foi votado, placar, quem votou o quê|P0|

|Página do Deputado|Histórico de votos do parlamentar específico|P0|

|Busca por Deputado|Encontrar por nome, partido ou estado|P0|

|Explicação em Linguagem Simples|LLM traduz ementa para português claro|P0|

|"Por que isso importa"|LLM explica impacto prático da decisão|P1|

|Compartilhar Votação|Gerar card para WhatsApp/redes sociais|P1|

Escopo:

- Apenas Câmara dos Deputados

- Apenas Plenário (não comissões)

- Apenas votações nominais

- Dados de 2023 em diante

---

### 4.2 v1.5 — "Entendimento"

Objetivo: Cidadão entende o contexto e consegue comparar deputados.

|Funcionalidade|Descrição|Prioridade|

|---|---|---|

|Comparar Deputados|Side-by-side de dois parlamentares|P1|

|Filtro por Tema|Ver votações sobre saúde, educação, segurança, etc.|P1|

|Alinhamento com Governo|% de vezes que votou com/contra orientação do governo|P1|

|Alinhamento com Partido|% de vezes que seguiu orientação do líder|P1|

|Timeline Visual|Gráfico de votações ao longo do tempo|P2|

---

### 4.3 v2.0 — "Fiscalização"

Objetivo: Cidadão vê o dinheiro público sendo usado pelo deputado.

|Funcionalidade|Descrição|Prioridade|

|---|---|---|

|Gastos Parlamentares|Cota parlamentar: quanto gastou, com o quê|P0|

|Emendas Parlamentares|Para onde o deputado direcionou dinheiro público|P0|

|Ranking de Gastos|Comparativo entre deputados do mesmo estado|P1|

|Alertas de Gasto Atípico|Notificação quando gasto foge do padrão|P2|

|Cruzamento Voto × Emenda|Votou X e direcionou emenda para Y (conflito?)|P2|

---

### 4.4 v2.5 — "Contexto"

Objetivo: Cidadão tem visão 360° do parlamentar.

|Funcionalidade|Descrição|Prioridade|

|---|---|---|

|Notícias do Deputado|Agregador de menções na mídia (via busca)|P1|

|Presença em Plenário|Quantas sessões compareceu vs. faltou|P1|

|Projetos de Autoria|PLs que o deputado propôs|P2|

|Histórico de Mandatos|Cargos anteriores, processos, etc.|P2|

---

### 4.5 v3.0 — "Cobrança"

Objetivo: Cidadão consegue agir, não só observar.

|Funcionalidade|Descrição|Prioridade|

|---|---|---|

|Contato Direto|Botão para email/telefone do gabinete|P0|

|Template de Cobrança|Mensagem pré-escrita questionando voto específico|P1|

|Template de Elogio|Mensagem pré-escrita agradecendo posicionamento|P1|

|Campanha Coletiva|Juntar cidadãos para cobrar em massa|P2|

|Resposta do Gabinete|Registrar se houve resposta (crowdsourced)|P2|

|Lembrete Pré-Eleição|"Você pesquisou esse deputado. Ele votou assim..."|P1|

---

## 5. Arquitetura de Informação

### 5.1 Estrutura de Navegação (MVP)

```

[Home / Feed]

│

├── [Votação]

│ ├── O que foi votado (explicação simples)

│ ├── Por que importa

│ ├── Placar (SIM/NÃO)

│ ├── Lista de votos por deputado

│ └── [Link para deputado]

│

├── [Deputado]

│ ├── Foto, partido, estado

│ ├── Histórico de votos

│ ├── Filtro por tema/período

│ └── [Link para votação]

│

└── [Busca]

├── Por nome do deputado

├── Por estado

└── Por partido

```

### 5.2 Modelo Mental do Usuário

O usuário pensa em 3 perguntas:

1. "O que aconteceu?" → Feed de votações

2. "Quem votou o quê?" → Página da votação

3. "Como meu deputado votou?" → Página do deputado

O fluxo principal é:

```

Descoberta → Entendimento → Ação

"Vi que votaram algo" → "Entendi o impacto" → "Vou cobrar/lembrar"

```

---

## 6. Requisitos Técnicos (MVP)

### 6.1 Fontes de Dados

|Dado|Fonte|Frequência|

|---|---|---|

|Votações|API Dados Abertos Câmara|Diária|

|Votos individuais|API Dados Abertos Câmara|Diária|

|Proposições|API Dados Abertos Câmara|Diária|

|Deputados|API Dados Abertos Câmara|Semanal|

|Orientações de bancada|API Dados Abertos Câmara|Diária|

### 6.2 Pipeline de Dados

```

[Bronze] [Silver] [Gold]

Dados brutos da API → Dados normalizados → Watch Items

(JSON/CSV) (Postgres/SQLite) (JSON para frontend)

│

▼

[LLM Processing]

- Tradução da ementa

- "Por que importa"

- Tags de tema

```

### 6.3 Stack Sugerida (MVP simples)

|Componente|Tecnologia|Justificativa|

|---|---|---|

|Backend|Python + FastAPI|Simplicidade, bom para dados|

|Database|SQLite → Postgres|Começar simples, escalar depois|

|Frontend|Next.js ou HTML estático|Mobile-first, SEO|

|LLM|Claude API|Qualidade de texto|

|Hosting|Vercel + Railway|Free tier generoso|

|Cache|Redis (futuro)|Quando escalar|

### 6.4 Estimativa de Custos (MVP)

|Item|Custo Mensal|

|---|---|

|Hosting (Vercel free)|$0|

|Database (Railway free)|$0|

|Claude API (~1000 votações/mês)|~$10-20|

|Domínio|~$12/ano|

|**Total MVP**|**~$15-25/mês**|

---

## 7. Métricas de Sucesso

### 7.1 MVP (primeiros 3 meses)

|Métrica|Meta|Como medir|

|---|---|---|

|Usuários únicos/mês|1.000|Analytics|

|Páginas de deputado visualizadas|5.000|Analytics|

|Compartilhamentos|500|Tracking de botão|

|Tempo médio na página|> 2 min|Analytics|

### 7.2 v2.0 (6-12 meses)

|Métrica|Meta|Como medir|

|---|---|---|

|Usuários únicos/mês|10.000|Analytics|

|Contatos enviados a gabinetes|1.000|Tracking|

|Menções em redes sociais|100|Social listening|

|Matérias na imprensa|5|Clipping|

### 7.3 North Star (longo prazo)

> "Em 2026, X% dos eleitores brasileiros consultaram o Memória Cívica antes de votar."

---

## 8. Riscos e Mitigações

|Risco|Probabilidade|Impacto|Mitigação|

|---|---|---|---|

|API da Câmara instável/fora|Média|Alto|Cache agressivo, fallback para arquivos CSV|

|LLM gera informação incorreta|Média|Alto|Sempre mostrar fonte original, revisão humana inicial|

|Acusação de viés político|Alta|Médio|Transparência total, só fatos, sem opinião|

|Baixa adoção|Alta|Alto|Foco em compartilhamento, parcerias com influenciadores|

|Custo de LLM escalar|Média|Médio|Cache de explicações, processar só votações novas|

---

## 9. Fora de Escopo (MVP)

Para manter foco, não faremos no MVP:

- ❌ Senado Federal

- ❌ Comissões (só Plenário)

- ❌ Votações simbólicas (só nominais)

- ❌ App nativo (só web responsiva)

- ❌ Notificações push

- ❌ Contas de usuário / login

- ❌ Gastos parlamentares

- ❌ Emendas

- ❌ Notícias

---

## 10. Cronograma Sugerido

### Fase 1: Fundação (Semanas 1-2)

- [ ] Pipeline de ingestão de dados

- [ ] Modelo de dados (Proposição, Votação, Voto, Deputado)

- [ ] Script de carga inicial (2023-2024)

### Fase 2: Core (Semanas 3-4)

- [ ] API backend (endpoints de votações e deputados)

- [ ] Integração com LLM para explicações

- [ ] Testes de qualidade das explicações

### Fase 3: Frontend (Semanas 5-6)

- [ ] Página de Feed

- [ ] Página de Votação

- [ ] Página de Deputado

- [ ] Busca

### Fase 4: Polish (Semanas 7-8)

- [ ] Mobile responsivo

- [ ] Compartilhamento social

- [ ] SEO básico

- [ ] Analytics

### Fase 5: Lançamento (Semana 9)

- [ ] Deploy produção

- [ ] Soft launch para feedback

- [ ] Ajustes finais

- [ ] Lançamento público

---

## 11. Perguntas em Aberto

1. Nome definitivo: "Memória Cívica" ou outro? (Fiscaliza Brasil? Meu Deputado? Congresso Claro?)



2. Tom das explicações: Mais formal ou mais coloquial? ("O projeto estabelece..." vs. "Basicamente, isso significa que...")



3. Abrangência geográfica inicial: Lançar nacional ou começar por um estado?



4. Parcerias: Buscar apoio de ONGs (Transparência Brasil, Open Knowledge)?



5. Monetização futura: Doações? Grants? Ads? Totalmente gratuito?



---

## 12. Referências e Inspirações

- [Radar do Congresso](https://www.radardocongresso.com.br/) — Bom conteúdo, UX complexa

- [Congresso em Foco](https://congressoemfoco.uol.com.br/) — Jornalismo, não ferramenta

- [Poder360](https://www.poder360.com.br/) — Dados, mas para profissionais

- [Vote Watch Europe](https://www.votewatch.eu/) — Referência internacional

- [GovTrack.us](https://www.govtrack.us/) — Modelo americano

---

_Última atualização: Janeiro 2025_ _Autor: [Seu nome]_ Status: Draft para validação
