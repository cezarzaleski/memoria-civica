# Cenário de Validação 4: Cache Hits

Este arquivo foi criado para testar cache hits no workflow de CI/CD.

**Objetivo:** Validar que após a primeira execução, o cache de dependências é reutilizado (npm para frontend, Poetry para etl).

**O que verificar nos logs:**
- Mensagem "Cache restored from key" para npm (frontend)
- Mensagem "Cache restored from key" para Poetry (etl)
- Tempo de execução reduzido em relação à primeira execução

**Data de criação:** 2026-01-28
