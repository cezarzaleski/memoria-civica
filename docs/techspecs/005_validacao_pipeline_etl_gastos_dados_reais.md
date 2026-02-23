# Tech Spec 005 — Validação do Pipeline ETL de Gastos com Dados Reais (Fonte Cotas)

**Status:** Implementado  
**Data:** 2026-02-23  
**Escopo:** Evidenciar validação E2E do pipeline ETL completo com dados reais CEAP (fonte cotas) e critérios objetivos de aprovação.

## 1. Objetivo

Validar, de forma reprodutível, que o pipeline ETL completo:

1. Executa a ordem orquestrada correta (`deputados` → `proposicoes` → `votacoes` → `gastos` → `votacoes_proposicoes` → `orientacoes` → `classificacao`).
2. Processa dados reais da fonte CEAP/cotas para o ano configurado em `CAMARA_ANO`.
3. Mantém consistência da carga no domínio de gastos (idempotência e integridade referencial com `deputados`).
4. Interrompe com erro (`exit code 1`) quando o step crítico de gastos falha.

## 2. Pré-condições

1. Arquivos reais anuais disponíveis no diretório `etl/data/dados_camara/` (ou, em fallback, `data/dados_camara/`):
   - `deputados.csv`
   - `proposicoes-{ano}.csv`
   - `votacoes-{ano}.csv`
   - `votacoesVotos-{ano}.csv`
   - `gastos-{ano}.csv`
   - `votacoesProposicoes-{ano}.csv`
   - `votacoesOrientacoes-{ano}.csv`
2. Dependências Python instaladas via Poetry.

## 3. Validação Automatizada

Foi adicionada a suíte opcional de integração com dados reais:

- `etl/tests/test_integration/test_gastos_real_data_pipeline.py`

Essa suíte:

1. Usa subconjuntos derivados dos CSVs reais para manter execução previsível e reprodutível.
2. Executa `run_full_etl.run_etl()` com ETLs reais conectados a banco SQLite temporário.
3. Valida happy path, ordem dos steps, idempotência de `gastos` e integridade referencial.
4. Valida cenário de falha crítica no step de `gastos` com abortamento imediato.

## 4. Execução Recomendada

```bash
RUN_REAL_DATA_PIPELINE=1 poetry run pytest -v etl/tests/test_integration/test_gastos_real_data_pipeline.py
```

```bash
make test
make lint
```

## 5. Critérios de Aceite

1. Teste de happy path retorna sucesso (`exit code 0`) com ordem de execução esperada.
2. Reexecução da carga de `gastos` com mesmo arquivo não altera a contagem total de registros.
3. Não existem registros em `gastos` com `deputado_id` não nulo apontando para deputado inexistente.
4. Teste de falha crítica em `gastos` retorna `exit code 1` e interrompe fluxo sem avançar para steps seguintes.
5. `make test` e `make lint` concluem sem falhas.

## 6. Evidências de Execução (2026-02-23)

### 6.1 Download da fonte cotas (real)

Comando:

```bash
poetry run python etl/scripts/download_camara.py --file gastos --data-dir etl/data/dados_camara
```

Resultado observado:

- URL efetiva: `https://www.camara.leg.br/cotas/Ano-2025.csv.zip`
- Arquivo materializado: `etl/data/dados_camara/gastos-2025.csv`
- Tamanho baixado: `6.53 MB`
- Tempo total reportado: `1.28s`
- Falhas: `0`

### 6.2 Integração com dados reais (subconjunto reprodutível)

Comando:

```bash
RUN_REAL_DATA_PIPELINE=1 poetry run pytest -v etl/tests/test_integration/test_gastos_real_data_pipeline.py
```

Resultado observado:

- `2 passed`
- Testes cobertos:
  - happy path completo + idempotência + integridade referencial
  - falha crítica no step de gastos com abortamento do pipeline

### 6.3 Validação global do projeto

Comandos:

```bash
make test
make lint
```

Resultado observado:

- `make test`: `609 passed, 17 skipped`
- `make lint`: `All checks passed`
