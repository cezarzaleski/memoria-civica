# Configuração de Branch Protection Rules

Este documento descreve como configurar as regras de proteção de branch para o repositório Memória Cívica, garantindo que todo código seja testado antes de ser mergeado na branch `main`.

## Visão Geral

Branch protection rules garantem que:
- Código não pode ser mergeado diretamente na branch `main` sem passar pelos testes
- Pull Requests devem ter status checks passando antes do merge
- Código é revisado e validado através do workflow de CI/CD

## Configuração via GitHub UI

### Passo a Passo

1. **Acessar configurações do repositório**
   - Vá para: https://github.com/cezarzaleski/memoria-civica/settings/branches
   - Ou: Settings → Branches (menu lateral)

2. **Adicionar regra de proteção**
   - Clique em "Add branch protection rule" ou "Add rule"
   - No campo "Branch name pattern", digite: `main`

3. **Configurar regras obrigatórias**

   Marque as seguintes opções:

   ✅ **Require a pull request before merging**
   - Garante que código não seja commitado diretamente na main
   - Opcionalmente: "Require approvals" (1 aprovação recomendada para projetos com múltiplos contribuidores)

   ✅ **Require status checks to pass before merging**
   - Marque: "Require branches to be up to date before merging"
   - Na busca "Search for status checks", selecione os seguintes checks:
     - `changes` - Job de detecção de mudanças
     - `frontend` - Testes do frontend (se houver mudanças)
     - `etl` - Testes do ETL (se houver mudanças)

   ✅ **Require conversation resolution before merging** (opcional mas recomendado)
   - Garante que todos os comentários de revisão sejam resolvidos

   ✅ **Include administrators** (recomendado)
   - Aplica as regras também para administradores do repositório
   - Evita bypass acidental das regras

4. **Configurações adicionais (opcionais)**

   Considere habilitar:
   - **Require deployments to succeed before merging**: Se houver ambiente de staging
   - **Require signed commits**: Para maior segurança (requer configuração de GPG)
   - **Lock branch**: Para branches que não devem receber commits (ex: releases antigas)

5. **Salvar regras**
   - Clique em "Create" ou "Save changes" no final da página

## Configuração via GitHub CLI

Se você tiver o GitHub CLI (`gh`) instalado, pode configurar via linha de comando:

```bash
# Habilitar branch protection com status checks
gh api repos/cezarzaleski/memoria-civica/branches/main/protection \
  --method PUT \
  -f required_status_checks[strict]=true \
  -f required_status_checks[contexts][]=changes \
  -f required_status_checks[contexts][]=frontend \
  -f required_status_checks[contexts][]=etl \
  -f required_pull_request_reviews[required_approving_review_count]=1 \
  -f required_pull_request_reviews[dismiss_stale_reviews]=true \
  -f enforce_admins=true \
  -f required_conversation_resolution=true \
  -f allow_force_pushes=false \
  -f allow_deletions=false
```

## Configuração via Terraform (opcional)

Para repositórios gerenciados como infraestrutura como código:

```hcl
resource "github_branch_protection" "main" {
  repository_id = "memoria-civica"
  pattern       = "main"

  required_status_checks {
    strict   = true
    contexts = ["changes", "frontend", "etl"]
  }

  required_pull_request_reviews {
    dismiss_stale_reviews           = true
    require_code_owner_reviews      = true
    required_approving_review_count = 1
  }

  enforce_admins                  = true
  require_conversation_resolution = true
  allows_force_pushes             = false
  allows_deletions                = false
}
```

## Verificação da Configuração

### Verificar se as regras estão ativas

1. Vá para: https://github.com/cezarzaleski/memoria-civica/settings/branches
2. Deve aparecer a branch `main` com um ícone de proteção ✓
3. Clique em "Edit" para ver as regras configuradas

### Testar as regras

1. **Criar uma branch de teste**
   ```bash
   git checkout -b test/branch-protection
   echo "test" >> README.md
   git add README.md
   git commit -m "test: verificar branch protection"
   git push origin test/branch-protection
   ```

2. **Abrir Pull Request**
   - Vá para: https://github.com/cezarzaleski/memoria-civica/pulls
   - Clique em "New pull request"
   - Selecione sua branch de teste

3. **Verificar status checks**
   - O PR deve mostrar os status checks pendentes/em execução
   - Aguarde os testes completarem
   - Se os testes passarem, botão "Merge" ficará verde
   - Se os testes falharem, botão "Merge" ficará desabilitado com mensagem de erro

4. **Tentar merge direto na main (deve falhar)**
   ```bash
   git checkout main
   echo "test" >> README.md
   git add README.md
   git commit -m "test: tentar commit direto"
   git push origin main
   ```

   Deve retornar erro:
   ```
   remote: error: GH006: Protected branch update failed
   remote: error: Changes must be made through a pull request.
   ```

## Status Checks do Workflow

O workflow `test.yml` define os seguintes status checks:

### 1. `changes`
- **Obrigatório**: Sim (sempre executa)
- **Função**: Detecta quais módulos (frontend/etl) foram modificados
- **Duração**: ~5-10 segundos
- **Falha se**: Erro no checkout ou na detecção de mudanças

### 2. `frontend`
- **Obrigatório**: Condicional (só se houver mudanças no frontend/)
- **Função**: Executa linting e testes do frontend
- **Duração**: ~1-3 minutos (com cache npm)
- **Falha se**:
  - Erros de linting (ESLint)
  - Testes falhando (Vitest)
  - Erros de TypeScript

### 3. `etl`
- **Obrigatório**: Condicional (só se houver mudanças no etl/)
- **Função**: Executa linting e testes do ETL
- **Duração**: ~30-60 segundos (com cache Poetry)
- **Falha se**:
  - Erros de linting (Ruff)
  - Testes falhando (Pytest)
  - Coverage abaixo do target (80%)

## Troubleshooting

### Status check não aparece na lista

**Problema**: Ao configurar branch protection, o status check não aparece na busca.

**Causa**: O status check precisa ser executado pelo menos uma vez para aparecer na lista.

**Solução**:
1. Crie um PR temporário para executar o workflow
2. Aguarde o workflow completar
3. Volte às configurações de branch protection
4. O status check agora deve aparecer na busca

### Merge bloqueado mesmo com testes passando

**Problema**: Testes estão verdes mas merge continua bloqueado.

**Possíveis causas**:
1. **Branch desatualizada**: Habilite "Require branches to be up to date" e faça merge da main
2. **Conversas não resolvidas**: Se "Require conversation resolution" está habilitado, resolva todos os comentários
3. **Aprovação faltando**: Se require approvals está habilitado, obtenha aprovação de um revisor

### Status check "Expected" mas nunca executa

**Problema**: PR mostra status check como "Expected" mas nunca inicia.

**Causa**: O job é condicional e não foi acionado (ex: mudanças no frontend não acionam job etl).

**Solução**: Isso é comportamento esperado para jobs condicionais. Se não houver mudanças no módulo, o job não executa e não bloqueia o merge.

### Como remover branch protection temporariamente

**Não recomendado**, mas se necessário:
1. Vá para: https://github.com/cezarzaleski/memoria-civica/settings/branches
2. Clique em "Edit" na regra da branch main
3. Role até o final e clique "Delete rule"
4. **Importante**: Reconfigure as regras assim que possível

## Referências

- [GitHub Docs: Branch Protection Rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [GitHub Docs: Required Status Checks](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches#require-status-checks-before-merging)
- [GitHub CLI: Branch Protection](https://cli.github.com/manual/gh_api)
- [Workflow de testes](./workflows/test.yml)

---

**Última atualização**: Janeiro 2025

**Mantenedor**: Time Memória Cívica

**Status**: ✅ Configuração recomendada para produção
