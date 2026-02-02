# Guia de Configuração de GitHub Secrets

Este documento fornece instruções detalhadas para configurar os GitHub Secrets necessários para o pipeline de CI/CD do Memória Cívica.

## Índice

- [Visão Geral](#visão-geral)
- [Checklist de Configuração](#checklist-de-configuração)
- [Secrets do Docker Hub](#secrets-do-docker-hub)
- [Secrets de SSH para VPS](#secrets-de-ssh-para-vps)
- [Secrets do Vercel](#secrets-do-vercel)
- [Como Adicionar Secrets no GitHub](#como-adicionar-secrets-no-github)
- [Validação dos Secrets](#validação-dos-secrets)
- [Troubleshooting](#troubleshooting)

---

## Visão Geral

O pipeline de CI/CD requer 8 secrets configurados no GitHub para funcionar corretamente:

| Categoria | Secret | Obrigatório | Usado Por |
|-----------|--------|-------------|-----------|
| Docker Hub | `DOCKERHUB_USERNAME` | ✅ Sim | deploy-backend.yml |
| Docker Hub | `DOCKERHUB_TOKEN` | ✅ Sim | deploy-backend.yml |
| VPS | `VPS_HOST` | ✅ Sim | deploy-backend.yml |
| VPS | `VPS_USER` | ✅ Sim | deploy-backend.yml |
| VPS | `VPS_SSH_KEY` | ✅ Sim | deploy-backend.yml |
| Vercel | `VERCEL_TOKEN` | ✅ Sim | deploy-frontend.yml |
| Vercel | `VERCEL_ORG_ID` | ✅ Sim | deploy-frontend.yml |
| Vercel | `VERCEL_PROJECT_ID` | ✅ Sim | deploy-frontend.yml |

---

## Checklist de Configuração

Use esta checklist para garantir que todos os secrets estão configurados:

### Docker Hub
- [ ] Conta criada em [hub.docker.com](https://hub.docker.com)
- [ ] Repositório `memoria-backend` criado (público ou privado)
- [ ] Access Token gerado com permissões Read/Write
- [ ] `DOCKERHUB_USERNAME` configurado no GitHub
- [ ] `DOCKERHUB_TOKEN` configurado no GitHub

### VPS (Servidor de Produção)
- [ ] VPS provisionada com Docker instalado
- [ ] Par de chaves SSH gerado (ed25519 recomendado)
- [ ] Chave pública adicionada ao `~/.ssh/authorized_keys` na VPS
- [ ] `VPS_HOST` configurado no GitHub
- [ ] `VPS_USER` configurado no GitHub
- [ ] `VPS_SSH_KEY` configurado no GitHub (chave privada completa)

### Vercel
- [ ] Conta criada em [vercel.com](https://vercel.com)
- [ ] Projeto criado e vinculado ao repositório
- [ ] Token de API gerado
- [ ] `VERCEL_TOKEN` configurado no GitHub
- [ ] `VERCEL_ORG_ID` configurado no GitHub
- [ ] `VERCEL_PROJECT_ID` configurado no GitHub

---

## Secrets do Docker Hub

### DOCKERHUB_USERNAME

**Descrição**: Nome de usuário da conta Docker Hub

**Como obter**:
1. Acesse [hub.docker.com](https://hub.docker.com)
2. O username está visível no canto superior direito
3. Também pode ser visto em Account Settings

**Exemplo de valor**: `cezarzaleski`

### DOCKERHUB_TOKEN

**Descrição**: Token de acesso para autenticação (não use sua senha!)

**Como obter**:
1. Acesse [hub.docker.com](https://hub.docker.com) e faça login
2. Clique no seu avatar → **Account Settings**
3. No menu lateral, clique em **Security**
4. Clique em **New Access Token**
5. Preencha:
   - **Access Token Description**: `GitHub Actions - Memoria Civica`
   - **Access Permissions**: `Read, Write, Delete`
6. Clique em **Generate**
7. **IMPORTANTE**: Copie o token imediatamente (não será mostrado novamente)

**Formato do valor**: String alfanumérica (ex: `dckr_pat_xxxxxxxxxxxxxxxxxxxx`)

**Validação local**:
```bash
# Testar autenticação
echo "SEU_TOKEN" | docker login -u SEU_USERNAME --password-stdin

# Resposta esperada: "Login Succeeded"
```

---

## Secrets de SSH para VPS

### VPS_HOST

**Descrição**: Endereço IP ou hostname do servidor VPS

**Como obter**:
1. Acesse o painel do seu provedor de hosting (DigitalOcean, AWS, etc.)
2. Localize o endereço IP público da sua VPS
3. Pode ser IP (ex: `192.168.1.100`) ou hostname (ex: `vps.exemplo.com`)

**Exemplo de valor**: `203.0.113.50` ou `meu-servidor.exemplo.com`

**Validação**:
```bash
# Testar se o host responde
ping -c 3 SEU_VPS_HOST

# Testar se porta SSH está aberta
nc -zv SEU_VPS_HOST 22
```

### VPS_USER

**Descrição**: Nome de usuário SSH para conectar na VPS

**Como obter**:
1. Geralmente é `root` ou um usuário específico criado para deploy
2. Recomendação: criar usuário dedicado (ex: `deploy`)

**Exemplo de valor**: `root` ou `deploy`

**Criar usuário dedicado na VPS (opcional mas recomendado)**:
```bash
# Na VPS como root
adduser deploy
usermod -aG docker deploy
mkdir -p /home/deploy/.ssh
cp ~/.ssh/authorized_keys /home/deploy/.ssh/
chown -R deploy:deploy /home/deploy/.ssh
chmod 700 /home/deploy/.ssh
chmod 600 /home/deploy/.ssh/authorized_keys
```

### VPS_SSH_KEY

**Descrição**: Chave SSH privada completa para autenticação

**Como gerar um novo par de chaves**:
```bash
# Gerar par de chaves ed25519 (recomendado)
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_deploy_key -N ""

# Ou RSA se ed25519 não for suportado
ssh-keygen -t rsa -b 4096 -C "github-actions-deploy" -f ~/.ssh/github_deploy_key -N ""
```

**Adicionar chave pública na VPS**:
```bash
# Copiar chave pública para a VPS
ssh-copy-id -i ~/.ssh/github_deploy_key.pub USUARIO@VPS_HOST

# Ou manualmente
cat ~/.ssh/github_deploy_key.pub | ssh USUARIO@VPS_HOST "cat >> ~/.ssh/authorized_keys"
```

**Obter conteúdo da chave privada**:
```bash
# Exibir chave privada (copie TODO o conteúdo incluindo cabeçalhos)
cat ~/.ssh/github_deploy_key
```

**Formato do valor** (deve incluir tudo):
```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
...conteúdo da chave...
QyMDI1AAAA
-----END OPENSSH PRIVATE KEY-----
```

**IMPORTANTE**:
- Inclua as linhas `-----BEGIN...-----` e `-----END...-----`
- Não adicione espaços extras no início ou fim
- Não modifique quebras de linha

**Validação local**:
```bash
# Testar conexão SSH com a chave
ssh -i ~/.ssh/github_deploy_key USUARIO@VPS_HOST "echo 'Conexão bem-sucedida!'"
```

---

## Secrets do Vercel

### VERCEL_TOKEN

**Descrição**: Token de autenticação da API Vercel

**Como obter**:
1. Acesse [vercel.com](https://vercel.com) e faça login
2. Vá para **Settings** (clique no seu avatar)
3. No menu lateral, clique em **Tokens**
4. Clique em **Create**
5. Preencha:
   - **Token Name**: `GitHub Actions - Memoria Civica`
   - **Scope**: Full Account
   - **Expiration**: No Expiration (ou escolha um período)
6. Clique em **Create Token**
7. Copie o token imediatamente

**Formato do valor**: String alfanumérica longa

**Validação local**:
```bash
# Instalar Vercel CLI se não tiver
npm install -g vercel

# Testar token
vercel whoami --token=SEU_TOKEN
```

### VERCEL_ORG_ID

**Descrição**: ID da organização ou time na Vercel

**Como obter**:
1. Acesse o projeto em [vercel.com](https://vercel.com)
2. Vá para **Project Settings** → **General**
3. Role até a seção **Project ID**
4. O **Org ID** (ou Team ID) está listado junto

**Alternativa - via CLI**:
```bash
# Na pasta do projeto frontend
cd frontend
vercel link
cat .vercel/project.json
# O "orgId" está no arquivo
```

**Formato do valor**: String alfanumérica (ex: `team_xxxxxxxxxxxxxxxxxxxx`)

### VERCEL_PROJECT_ID

**Descrição**: ID do projeto na Vercel

**Como obter**:
1. Acesse o projeto em [vercel.com](https://vercel.com)
2. Vá para **Project Settings** → **General**
3. O **Project ID** está listado

**Alternativa - via CLI**:
```bash
# Na pasta do projeto frontend
cd frontend
vercel link
cat .vercel/project.json
# O "projectId" está no arquivo
```

**Formato do valor**: String alfanumérica (ex: `prj_xxxxxxxxxxxxxxxxxxxx`)

---

## Como Adicionar Secrets no GitHub

### Via Interface Web

1. Acesse seu repositório no GitHub: `https://github.com/cezarzaleski/memoria-civica`
2. Clique em **Settings** (aba superior)
3. No menu lateral, clique em **Secrets and variables** → **Actions**
4. Clique em **New repository secret**
5. Preencha:
   - **Name**: Nome do secret (ex: `DOCKERHUB_USERNAME`)
   - **Secret**: Valor do secret
6. Clique em **Add secret**
7. Repita para cada secret

### Via GitHub CLI (gh)

```bash
# Autenticar no GitHub CLI
gh auth login

# Adicionar secret
gh secret set DOCKERHUB_USERNAME --body "seu_username"
gh secret set DOCKERHUB_TOKEN --body "seu_token"
gh secret set VPS_HOST --body "seu_ip_ou_hostname"
gh secret set VPS_USER --body "seu_usuario_ssh"
gh secret set VPS_SSH_KEY < ~/.ssh/github_deploy_key
gh secret set VERCEL_TOKEN --body "seu_token_vercel"
gh secret set VERCEL_ORG_ID --body "seu_org_id"
gh secret set VERCEL_PROJECT_ID --body "seu_project_id"

# Listar secrets configurados
gh secret list
```

---

## Validação dos Secrets

Após configurar todos os secrets, execute o workflow de validação:

### Via GitHub Actions UI

1. Acesse **Actions** no repositório
2. Selecione **Validate Secrets** na lista de workflows
3. Clique em **Run workflow**
4. Selecione quais categorias validar (Docker, VPS, Vercel)
5. Clique em **Run workflow**
6. Aguarde a execução e verifique os resultados

### Resultados Esperados

- ✅ **Sucesso**: Secret configurado e válido
- ❌ **Falha**: Secret não configurado ou inválido
- ⚠️ **Aviso**: Teste parcial (ex: VPS não acessível do GitHub)

---

## Troubleshooting

### Docker Hub

**Erro**: `denied: requested access to the resource is denied`
- Verifique se o token tem permissão de escrita
- Verifique se o repositório existe no Docker Hub
- Verifique se o username está correto

**Erro**: `unauthorized: authentication required`
- Token pode estar expirado ou inválido
- Gere um novo token

### VPS/SSH

**Erro**: `Permission denied (publickey)`
- Chave pública não está no `authorized_keys` da VPS
- Chave privada no GitHub está incompleta ou mal formatada
- Usuário SSH está incorreto

**Erro**: `Connection timed out`
- VPS pode estar offline
- Firewall bloqueando porta 22
- IP/hostname incorreto

**Erro**: `Host key verification failed`
- O workflow usa `StrictHostKeyChecking=no` para evitar isso
- Se persistir, verifique se o host está acessível

### Vercel

**Erro**: `Invalid token`
- Token expirado ou revogado
- Gere um novo token em vercel.com

**Erro**: `Project not found`
- VERCEL_PROJECT_ID incorreto
- Projeto foi deletado ou renomeado

**Erro**: `Forbidden`
- Token não tem permissão para o projeto/organização
- Verifique o escopo do token

---

## Melhores Práticas de Segurança

1. **Rotação de secrets**: Atualize tokens e chaves periodicamente
2. **Princípio do menor privilégio**: Use tokens com escopo mínimo necessário
3. **Monitoramento**: Verifique logs de acesso nos serviços externos
4. **Backup seguro**: Mantenha backup das credenciais em gerenciador de senhas
5. **Não compartilhe**: Cada ambiente deve ter seus próprios secrets
6. **Auditoria**: Revise periodicamente quais secrets estão configurados

---

_Última atualização: Janeiro 2025_
