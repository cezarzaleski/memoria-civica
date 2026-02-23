# Tech Spec 002 — Analise de Gaps: ETL Models vs Frontend Types/Mocks

**Data**: 2026-02-20
**Status**: Diagnostico

---

## 1. Resumo Executivo

O ETL define **8 tabelas** (`deputados`, `proposicoes`, `votacoes`, `votos`, `votacoes_proposicoes`, `orientacoes`, `categorias_civicas`, `proposicoes_categorias`) enquanto o frontend define **4 tipos** (`Deputado`, `Proposicao`, `Votacao`, `Voto`) e **5 endpoints MSW**. A cobertura estimada do frontend em relacao ao ETL e de aproximadamente **50% das entidades** e **65% dos campos** das entidades cobertas. Foram identificados **2 gaps CRITICOS** (entidades inteiras do ETL sem representacao no frontend), **3 gaps ALTOS** (relacionamentos N:N e campos estruturais ausentes), **8 gaps MEDIOS** (campos individuais ausentes), **6 gaps BAIXOS** (diferencas de tipagem/nomenclatura) e **2 itens INFO** (dados fabricados no frontend sem correspondencia no ETL). Total: **21 gaps**.

---

## 2. Tabela de Gaps (lado a lado)

| # | Severidade | Entidade ETL | Campo/Relacao ETL | Tipo Frontend | Mock Frontend | Descricao do Gap | Referencia ETL | Referencia Frontend |
|---|-----------|-------------|-------------------|--------------|--------------|-----------------|---------------|-------------------|
| 1 | CRITICO | `categorias_civicas` | Tabela inteira (id, codigo, nome, descricao, icone) | Ausente | Ausente | Entidade de categorias civicas nao possui tipo TS, mock, nem endpoint MSW. Sistema de classificacao civica invisivel ao frontend. | `etl/src/classificacao/models.py:24-37` | N/A |
| 2 | CRITICO | `proposicoes_categorias` | Tabela inteira (id, proposicao_id, categoria_id, origem, confianca, created_at) | Ausente | Ausente | Junction table proposicao-categoria nao representada no frontend. Classificacao civica de proposicoes inacessivel. | `etl/src/classificacao/models.py:40-63` | N/A |
| 3 | ALTO | `votacoes_proposicoes` | Tabela inteira (id, votacao_id, proposicao_id, titulo, ementa, sigla_tipo, numero, ano, eh_principal, created_at) | Ausente | Ausente | Relacao N:N votacao-proposicao ausente. Frontend assume relacao 1:1 via `proposicao_id` na Votacao, mas ETL permite multiplas proposicoes por votacao. | `etl/src/votacoes/models.py:120-149` | N/A |
| 4 | ALTO | `orientacoes` | Tabela inteira (id, votacao_id, sigla_bancada, orientacao, created_at) | Ausente | Ausente | Orientacoes de bancada nao representadas no frontend. Informacao politica relevante (como partidos orientaram votos) inexistente na UI. | `etl/src/votacoes/models.py:152-173` | N/A |
| 5 | ALTO | `votacoes` | `proposicao_id` (FK nullable) | `Votacao.proposicao_id: number` (obrigatorio) | Mock sempre gera valor | No ETL, `proposicao_id` e nullable (votacao pode nao ter proposicao direta). No frontend, o campo e obrigatorio (nao tem `?`). Mock sempre gera valor. | `etl/src/votacoes/models.py:48-53` | `frontend/lib/types/votacao.ts:25` |
| 6 | MEDIO | `votacoes` | `eh_nominal` (Boolean) | Ausente | Ausente | Campo que indica se votacao e nominal nao existe no tipo TS Votacao nem no mock. | `etl/src/votacoes/models.py:56` | N/A |
| 7 | MEDIO | `votacoes` | `descricao` (Text) | Ausente | Ausente | Descricao textual da votacao ausente do tipo TS e do mock. | `etl/src/votacoes/models.py:60` | N/A |
| 8 | MEDIO | `votacoes` | `sigla_orgao` (String) | Ausente | Ausente | Sigla do orgao (ex: PLEN, CCJC) ausente do tipo TS e do mock. | `etl/src/votacoes/models.py:61` | N/A |
| 9 | MEDIO | `votacoes` | `votos_sim`, `votos_nao`, `votos_outros` (Integer) | `Placar` (sim, nao, abstencao, obstrucao) | Mock gera placar com 4 campos | ETL armazena 3 contadores (sim/nao/outros), frontend decompoe em 4 (sim/nao/abstencao/obstrucao). `votos_outros` do ETL agrega abstencao+obstrucao que o frontend separa. Mismatch estrutural. | `etl/src/votacoes/models.py:57-59` | `frontend/lib/types/votacao.ts:14-19` |
| 10 | MEDIO | `votos` | `voto` (String, campo unico) | `Voto.tipo` (TipoVoto enum) | Mock usa `tipo` | Campo se chama `voto` no ETL e `tipo` no frontend. Renomeacao semantica. | `etl/src/votacoes/models.py:106` | `frontend/lib/types/voto.ts:16-22` |
| 11 | MEDIO | `votacoes` | `data_hora` (DateTime) | `Votacao.data` (string) | Mock gera ISO string | ETL usa `data_hora` (DateTime nativo), frontend usa `data` (string). Diferenca de nome e tipo. | `etl/src/votacoes/models.py:54` | `frontend/lib/types/votacao.ts:28` |
| 12 | MEDIO | `votacoes` | `resultado` (String(20)) | `Votacao.resultado` (ResultadoVotacao enum) | Mock usa enum | ETL aceita qualquer string ate 20 chars, frontend restringe a APROVADO/REJEITADO. ETL pode ter outros valores nao tratados. | `etl/src/votacoes/models.py:55` | `frontend/lib/types/votacao.ts:6-9` |
| 13 | MEDIO | `proposicoes` | `tipo` (String(20)) | `Proposicao.tipo` (TipoProposicao enum) | Mock usa enum | ETL aceita qualquer string ate 20 chars, frontend restringe a PL/PEC/MP/PLP/PDC. ETL pode ter tipos nao mapeados (ex: REQ, RIC, PFC). | `etl/src/proposicoes/models.py:33` | `frontend/lib/types/proposicao.ts:4-10` |
| 14 | BAIXO | `votacoes` | `id` (Integer PK) | `Votacao.id: string` | Mock gera `"votacao-${i}"` | ETL usa Integer como PK, frontend usa string. Mock gera IDs sinteticos tipo `"votacao-1"`. Incompatibilidade de tipo na chave primaria. | `etl/src/votacoes/models.py:47` | `frontend/lib/types/votacao.ts:25` |
| 15 | BAIXO | `votos` | `id` (Integer PK) | `Voto.id: string` | Mock gera `"voto-votacao-1-1"` | ETL usa Integer como PK, frontend usa string. Mesma incompatibilidade que Votacao. | `etl/src/votacoes/models.py:93` | `frontend/lib/types/voto.ts:16` |
| 16 | BAIXO | `votos` | `votacao_id` (Integer FK) | `Voto.votacao_id: string` | Mock gera string | Consequencia do gap #14: FK tambem muda de Integer para string. | `etl/src/votacoes/models.py:94-98` | `frontend/lib/types/voto.ts:17` |
| 17 | BAIXO | `proposicoes` | relationship `autor` (Deputado) | Ausente | Ausente | ETL tem relationship ORM para carregar autor, frontend nao tem campo `autor` no tipo Proposicao (so `autor_id`). | `etl/src/proposicoes/models.py:40` | `frontend/lib/types/proposicao.ts:15-23` |
| 18 | BAIXO | `votacoes` | relationship `votos` (list) | Ausente | Ausente | ETL tem relationship ORM para carregar votos da votacao, frontend nao inclui array de votos no tipo Votacao (busca via endpoint separado). | `etl/src/votacoes/models.py:67` | `frontend/lib/types/votacao.ts:24-31` |
| 19 | BAIXO | `votacoes` | relationship `proposicao` | `Votacao.proposicao?: Proposicao` | Mock inclui proposicao nested | Alinhado — frontend tem campo opcional `proposicao` que corresponde ao relationship do ETL. Sem gap funcional, mas o nome do FK difere (ver #5). | `etl/src/votacoes/models.py:66` | `frontend/lib/types/votacao.ts:27` |

---

## 3. Mocks Orfaos (Frontend -> ETL)

| # | Tipo Frontend | Campo/Endpoint | Existe no ETL? | Observacao | Referencia Frontend |
|---|--------------|---------------|----------------|-----------|-------------------|
| 1 | `Proposicao` | `ementa_simplificada?: string` | Nao | Campo fabricado no frontend para UI. Nao existe como coluna no ETL. Possivelmente resultado de processamento futuro (LLM simplification) nao implementado ainda. | `frontend/lib/types/proposicao.ts:21`, `frontend/mocks/data/proposicoes.ts:108` |
| 2 | `Placar` | `abstencao` e `obstrucao` (campos separados) | Parcial | ETL agrupa em `votos_outros`. Frontend desagrega. A informacao de detalhamento existe nos votos individuais, mas nao como colunas agregadas na tabela votacoes. | `frontend/lib/types/votacao.ts:17-18`, `frontend/mocks/data/votacoes.ts:9-31` |
| 3 | `Voto` | `deputado?: Deputado` (nested object) | Relationship | ETL tem o relationship mas API precisaria fazer join/eager load. Mock injeta o objeto completo. Nao e orfao, mas exige transformacao na API. | `frontend/lib/types/voto.ts:20`, `frontend/mocks/data/votos.ts:40` |
| 4 | `Votacao` | `proposicao?: Proposicao` (nested object) | Relationship | Similar ao anterior. ETL tem relationship, mock injeta objeto. API precisara serializar. | `frontend/lib/types/votacao.ts:27`, `frontend/mocks/data/votacoes.ts:68` |
| 5 | Handler MSW | `GET /api/v1/deputados?nome=&partido=&uf=` (filtros) | N/A (logica de API) | Filtros de query param sao logica de API, nao do ETL diretamente. Os campos existem nas colunas e indices do ETL. | `frontend/mocks/handlers/deputados.ts:33-55` |

---

## 4. Recomendacoes Priorizadas

1. **[CRITICO] Criar tipos TS, mocks e endpoints MSW para classificacao civica**
   Criar `CategoriaCivica` e `ProposicaoCategoria` como tipos TypeScript, gerar dados mock e endpoints MSW (`GET /api/v1/categorias-civicas`, `GET /api/v1/proposicoes/:id/categorias`). Considerar incluir campo `categorias` na interface `Proposicao`.
   - Arquivos afetados: `frontend/lib/types/` (novos arquivos), `frontend/mocks/data/` (novos arquivos), `frontend/mocks/handlers/` (novos arquivos), `frontend/lib/types/index.ts`
   - Esforco: **Medio**

2. **[CRITICO] Criar tipos TS e mock para `votacoes_proposicoes` (relacao N:N)**
   A relacao N:N entre votacoes e proposicoes e central ao dominio. Criar tipo `VotacaoProposicao`, ajustar interface `Votacao` para suportar lista de proposicoes, e criar endpoint MSW (`GET /api/v1/votacoes/:id/proposicoes`).
   - Arquivos afetados: `frontend/lib/types/votacao.ts`, `frontend/mocks/data/` (novo arquivo), `frontend/mocks/handlers/votacoes.ts`
   - Esforco: **Medio**

3. **[ALTO] Criar tipos TS e mock para orientacoes de bancada**
   Criar interface `Orientacao` com `sigla_bancada` e `orientacao`, mock data e endpoint MSW (`GET /api/v1/votacoes/:id/orientacoes`).
   - Arquivos afetados: `frontend/lib/types/` (novo arquivo), `frontend/mocks/data/` (novo arquivo), `frontend/mocks/handlers/` (novo arquivo ou extensao de `votacoes.ts`)
   - Esforco: **Medio**

4. **[ALTO] Corrigir nullability de `proposicao_id` em `Votacao`**
   Alterar `proposicao_id: number` para `proposicao_id?: number` na interface `Votacao` em `frontend/lib/types/votacao.ts:25`. Ajustar mock para gerar votacoes sem proposicao em alguns casos.
   - Arquivos afetados: `frontend/lib/types/votacao.ts:25`, `frontend/mocks/data/votacoes.ts`
   - Esforco: **Pequeno**

5. **[MEDIO] Adicionar campos ausentes da `Votacao`: `eh_nominal`, `descricao`, `sigla_orgao`**
   Extender interface `Votacao` com `eh_nominal?: boolean`, `descricao?: string`, `sigla_orgao?: string`. Atualizar mock para gerar esses campos.
   - Arquivos afetados: `frontend/lib/types/votacao.ts:24-31`, `frontend/mocks/data/votacoes.ts`
   - Esforco: **Pequeno**

6. **[MEDIO] Alinhar estrutura do Placar com ETL**
   Duas opcoes: (a) ETL passa a armazenar `votos_abstencao` e `votos_obstrucao` separadamente em vez de `votos_outros`, ou (b) API calcula a decomposicao a partir dos votos individuais. Recomenda-se opcao (a) para consistencia.
   - Arquivos afetados: `etl/src/votacoes/models.py:57-59` (se opcao a), ou camada de API (se opcao b)
   - Esforco: **Medio**

7. **[MEDIO] Renomear campo `tipo` para `voto` no tipo `Voto` (ou vice-versa)**
   Alinhar nomenclatura entre ETL (`voto`) e frontend (`tipo`). Recomenda-se que a API use o nome do ETL e o frontend faca a adaptacao, ou padronizar ambos.
   - Arquivos afetados: `frontend/lib/types/voto.ts:21`, `frontend/mocks/data/votos.ts:41`, `frontend/mocks/handlers/votos.ts`
   - Esforco: **Pequeno**

8. **[MEDIO] Alinhar nome `data_hora` (ETL) com `data` (frontend)**
   Padronizar o nome do campo de data/hora da votacao. Recomenda-se `data_hora` em ambos para manter a semantica (inclui hora).
   - Arquivos afetados: `frontend/lib/types/votacao.ts:28`, `frontend/mocks/data/votacoes.ts:69`
   - Esforco: **Pequeno**

9. **[MEDIO] Expandir enums `ResultadoVotacao` e `TipoProposicao`**
   O ETL aceita strings livres, logo pode haver valores nao cobertos pelos enums. Revisar dados reais e adicionar valores faltantes (ex: `ResultadoVotacao` pode precisar de "Aprovado com substitutivo"; `TipoProposicao` pode precisar de REQ, RIC, PFC, etc.).
   - Arquivos afetados: `frontend/lib/types/votacao.ts:6-9`, `frontend/lib/types/proposicao.ts:4-10`
   - Esforco: **Pequeno**

10. **[BAIXO] Alinhar tipo de `id` e `votacao_id` em Votacao/Voto de `string` para `number`**
    ETL usa Integer para PKs de votacoes e votos. Frontend usa string. Alinhar para number, a menos que a API intermediaria converta intencionalmente para string (nesse caso, documentar).
    - Arquivos afetados: `frontend/lib/types/votacao.ts:25`, `frontend/lib/types/voto.ts:16-17`, todos os mocks de votacoes e votos
    - Esforco: **Medio** (impacto em cadeia nos mocks e possivelmente componentes)

11. **[BAIXO] Definir estrategia para `ementa_simplificada`**
    Campo existe no frontend mas nao no ETL. Se for planejado como feature futura (resumo via LLM), adicionar coluna ao modelo `Proposicao` no ETL. Se nao for planejado, remover do tipo TS.
    - Arquivos afetados: `etl/src/proposicoes/models.py` (se adicionar) ou `frontend/lib/types/proposicao.ts:21` (se remover)
    - Esforco: **Pequeno**

---

## Arquivos Referenciados

**ETL Models:**
- `etl/src/deputados/models.py`
- `etl/src/proposicoes/models.py`
- `etl/src/votacoes/models.py`
- `etl/src/classificacao/models.py`

**Frontend Types:**
- `frontend/lib/types/deputado.ts`
- `frontend/lib/types/proposicao.ts`
- `frontend/lib/types/votacao.ts`
- `frontend/lib/types/voto.ts`
- `frontend/lib/types/index.ts`

**Frontend Mocks:**
- `frontend/mocks/data/deputados.ts`
- `frontend/mocks/data/proposicoes.ts`
- `frontend/mocks/data/votacoes.ts`
- `frontend/mocks/data/votos.ts`
- `frontend/mocks/handlers/deputados.ts`
- `frontend/mocks/handlers/votacoes.ts`
- `frontend/mocks/handlers/votos.ts`
- `frontend/mocks/handlers/index.ts`
