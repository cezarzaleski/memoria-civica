# Pipeline de CI/CD - Memória Cívica

Documentação completa do pipeline de integração contínua e deploy contínuo implementado com GitHub Actions.

## Visão Geral

O pipeline de CI/CD do Memória Cívica utiliza **GitHub Actions** com arquitetura de workflows separados para otimizar o ciclo de desenvolvimento:

- **CI (Integração Contínua)**: Executa lint e testes em Pull Requests para feedback rápido
- **Deploy (Deploy Contínuo)**: Realiza build, push de imagens Docker e deploy automatizado

### Fluxo de Trabalho

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Pull       │────►│  CI         │────►│  Review &   │
│  Request    │     │  (lint+test)│     │  Merge      │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                                               ▼
                    ┌─────────────┐     ┌─────────────┐
                    │  VPS        │◄────│  Deploy     │
                    │  Produção   │     │  (main)     │
                    └─────────────┘     └─────────────┘
```

## Arquitetura dos Workflows

### Estrutura de Arquivos

```
.github/
└── workflows/
    ├── ci-frontend.yml      # CI do frontend (lint + testes)
    ├── deploy-frontend.yml  # Deploy do frontend para Vercel
    └── deploy-backend.yml   # Deploy do backend para VPS

docker/
├── docker-compose.prod.yml  # Orquestração de containers na VPS
└── init-pgvector.sh         # Script de inicialização do PostgreSQL
```

### Visão Geral dos Componentes

| Workflow | Trigger | Responsabilidade |
|----------|---------|------------------|
| `ci-frontend.yml` | Pull Requests para `main` | Lint e testes do frontend |
| `deploy-frontend.yml` | Push para `main` (pasta frontend/) ou manual | Deploy do frontend para Vercel |
| `deploy-backend.yml` | Push para `main` (pastas backend/) ou manual | Build Docker, push para Docker Hub, deploy via SSH |

---

## Workflow de CI do Frontend

**Arquivo**: `.github/workflows/ci-frontend.yml`

**Trigger**: Pull Requests para branch `main`

### Jobs

O workflow executa dois jobs em **paralelo** para maximizar a eficiência:

#### Job: lint-frontend

Executa validação de código com ESLint:

```yaml
lint-frontend:
  runs-on: ubuntu-latest
  defaults:
    run:
      working-directory: frontend
  steps:
    - uses: actions/checkout@v4
    - run: npm ci && npm run lint
```

#### Job: test-frontend

Executa testes unitários com Vitest:

```yaml
test-frontend:
  runs-on: ubuntu-latest
  defaults:
    run:
      working-directory: frontend
  steps:
    - uses: actions/checkout@v4
    - run: npm ci && npm run test
```

### Resultados Esperados

- ✅ **Lint pass**: Código segue padrões ESLint configurados
- ✅ **Tests pass**: Todos os testes unitários passam
- ❌ **Falha**: PR não pode ser mergeado até correção

---

## Workflow de Deploy do Frontend

**Arquivo**: `.github/workflows/deploy-frontend.yml`

**Triggers**:
- Push para branch `main` (apenas arquivos em `frontend/` ou o próprio workflow)
- Execução manual via GitHub Actions UI (`workflow_dispatch`)

### Fluxo de Deploy

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Checkout   │────►│  Setup      │────►│  Build      │────►│  Deploy     │
│  código     │     │  Node.js    │     │  Vercel     │     │  Produção   │
└─────────────┘     └─────────────┘     └─────────────┘     └──────┬──────┘
                                                                   │
                                                                   ▼
                                                            ┌─────────────┐
                                                            │  Verificar  │
                                                            │  Deploy     │
                                                            └─────────────┘
```

### Etapas do Job

1. **Checkout**: Obtém código do repositório
2. **Setup Node.js**: Configura Node.js 20 com cache de npm
3. **Instalar Vercel CLI**: Instala ferramenta de deploy
4. **Pull ambiente Vercel**: Sincroniza configurações do projeto
5. **Build**: Compila o projeto Next.js
6. **Deploy**: Envia para produção Vercel
7. **Verificar**: Valida se o deploy está acessível

### Path Filtering

O workflow só executa quando há mudanças em:
- `frontend/**` - Qualquer arquivo do frontend
- `.github/workflows/deploy-frontend.yml` - O próprio workflow

---

## Workflow de Deploy do Backend

**Arquivo**: `.github/workflows/deploy-backend.yml`

**Triggers**:
- Push para branch `main` (arquivos de backend)
- Execução manual via GitHub Actions UI (`workflow_dispatch`)

### Path Filtering

O workflow monitora mudanças em:
- `src/**` - Código fonte Python
- `etl/**` - Pipeline ETL
- `alembic/**` - Migrations de banco
- `docker/backend.Dockerfile` - Dockerfile do backend
- `docker/docker-compose.prod.yml` - Compose de produção
- `pyproject.toml` e `poetry.lock` - Dependências Python

### Fluxo de Deploy

```
┌─────────────────────────────────────────────────────────────┐
│                    Job: build-push                          │
├─────────────┬─────────────┬─────────────┬─────────────────┬┤
│  Checkout   │  Setup      │  Login      │  Build & Push    │
│  código     │  Buildx     │  Docker Hub │  Imagem Docker   │
└─────────────┴─────────────┴─────────────┴────────┬─────────┘
                                                   │
                                                   ▼
┌─────────────────────────────────────────────────────────────┐
│                    Job: deploy (needs: build-push)          │
├─────────────────────────────────────────────────────────────┤
│                      SSH para VPS                           │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────────┐ │
│  │ Pull    │──►│ Run     │──►│ Rolling │──►│ Health      │ │
│  │ Images  │   │ Migrate │   │ Update  │   │ Check       │ │
│  └─────────┘   └─────────┘   └─────────┘   └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Job: build-push

Constrói e publica a imagem Docker:

1. **Setup Buildx**: Configura Docker Buildx para builds avançados
2. **Login Docker Hub**: Autentica com credenciais
3. **Extract Metadata**: Gera tags (SHA do commit + `latest`)
4. **Build & Push**: Compila e publica imagem com cache

### Estratégia de Tags de Imagem

| Tag | Descrição |
|-----|-----------|
| `sha-abc1234` | Tag baseada no SHA do commit (7 caracteres) |
| `latest` | Tag sempre atualizada para última versão |

Exemplo: `usuario/memoria-backend:sha-abc1234` e `usuario/memoria-backend:latest`

### Job: deploy

Executa deploy na VPS via SSH:

```bash
# 1. Navegar para diretório da aplicação
cd /app

# 2. Baixar imagens atualizadas
docker compose -f docker/docker-compose.prod.yml pull

# 3. Executar migrations do banco
docker compose -f docker/docker-compose.prod.yml run --rm backend alembic upgrade head

# 4. Rolling update dos containers
docker compose -f docker/docker-compose.prod.yml up -d --remove-orphans

# 5. Validar deployment via health check
curl -sf http://localhost:3000/health
```

---

## GitHub Secrets

### Secrets Necessários

Configure os seguintes secrets no GitHub (Settings → Secrets and variables → Actions):

#### Docker Hub

| Secret | Descrição | Como Obter |
|--------|-----------|------------|
| `DOCKERHUB_USERNAME` | Nome de usuário Docker Hub | Sua conta em hub.docker.com |
| `DOCKERHUB_TOKEN` | Token de acesso Docker Hub | Account Settings → Security → Access Tokens |

#### VPS (Deploy Backend)

| Secret | Descrição | Como Obter |
|--------|-----------|------------|
| `VPS_HOST` | IP ou hostname da VPS | Painel do provedor de hosting |
| `VPS_USER` | Usuário SSH para acesso | Geralmente `root` ou usuário criado |
| `VPS_SSH_KEY` | Chave SSH privada completa | Conteúdo de `~/.ssh/id_ed25519` |

#### Vercel (Deploy Frontend)

| Secret | Descrição | Como Obter |
|--------|-----------|------------|
| `VERCEL_TOKEN` | Token de autenticação Vercel | Settings → Tokens no painel Vercel |
| `VERCEL_ORG_ID` | ID da organização/time | Project Settings → General |
| `VERCEL_PROJECT_ID` | ID do projeto | Project Settings → General |

### Como Adicionar Secrets

1. Acesse o repositório no GitHub
2. Vá para **Settings** → **Secrets and variables** → **Actions**
3. Clique em **New repository secret**
4. Adicione nome e valor do secret
5. Clique em **Add secret**

### Segurança de Secrets

- ⚠️ **Nunca** commite secrets no código
- ⚠️ **Nunca** exiba secrets em logs (use `echo` com cuidado)
- ✅ Secrets são automaticamente mascarados nos logs do GitHub Actions
- ✅ Use tokens com escopo mínimo necessário

---

## Integração com Docker Hub

### Configuração do Repositório

1. Crie conta em [hub.docker.com](https://hub.docker.com)
2. Crie repositório público: `seu-usuario/memoria-backend`
3. Gere Access Token:
   - Account Settings → Security → Access Tokens
   - Selecione permissão "Read, Write, Delete"
   - Copie o token e salve como `DOCKERHUB_TOKEN`

### Estrutura da Imagem

> **Nota**: O arquivo `docker/backend.Dockerfile` será criado em uma tarefa separada.
> O exemplo abaixo ilustra a estrutura típica esperada.

```dockerfile
# docker/backend.Dockerfile (exemplo)
FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --no-dev

COPY src/ ./src/
COPY etl/ ./etl/
COPY alembic/ ./alembic/
COPY alembic.ini ./

CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "3000"]
```

### Cache de Build

O workflow utiliza cache do GitHub Actions para acelerar builds:

```yaml
cache-from: type=gha
cache-to: type=gha,mode=max
```

---

## Deploy na VPS

### Pré-requisitos da VPS

Antes do primeiro deploy, a VPS deve ter:

1. **Docker** instalado e funcionando
2. **Docker Compose** v2+ instalado
3. **Diretório `/app`** criado com permissões adequadas
4. **Acesso SSH** configurado com chave

### Script de Setup Inicial da VPS

Execute este script uma única vez na VPS:

```bash
#!/bin/bash
# setup-vps.sh

# Instalar Docker
curl -fsSL https://get.docker.com | sh

# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER

# Instalar Docker Compose plugin
sudo apt-get update
sudo apt-get install -y docker-compose-plugin

# Criar diretório da aplicação
sudo mkdir -p /app
sudo chown $USER:$USER /app

# Clonar repositório (primeira vez)
cd /app
git clone https://github.com/seu-usuario/memoria-civica.git .

# Criar arquivo .env (obrigatório para PostgreSQL)
cat > /app/.env << 'EOF'
POSTGRES_USER=memoria
POSTGRES_PASSWORD=sua_senha_segura
POSTGRES_DB=memoria_civica
EOF

# Iniciar containers
docker compose -f docker/docker-compose.prod.yml up -d
```

### Estrutura de Arquivos na VPS

```
/app/
├── docker/
│   ├── docker-compose.prod.yml
│   └── init-pgvector.sh
├── .env                         # Variáveis de ambiente (criar manualmente)
└── ...
```

### Variáveis de Ambiente na VPS

Crie o arquivo `/app/.env` com:

```env
# PostgreSQL (obrigatório)
POSTGRES_USER=memoria
POSTGRES_PASSWORD=sua_senha_segura_aqui
POSTGRES_DB=memoria_civica

# Outras variáveis conforme necessário
# API_KEY=...
# DATABASE_URL=...
```

---

## Health Check

### Endpoint de Validação

O deploy é validado através do endpoint `/health`:

```bash
curl -sf http://localhost:3000/health
```

**Resposta esperada**: HTTP 200 OK

### Mecanismo de Retry

O workflow implementa retry com 5 tentativas:

```bash
for i in 1 2 3 4 5; do
  if curl -sf http://localhost:3000/health > /dev/null 2>&1; then
    echo "Health check passed on attempt $i"
    break
  fi
  echo "Health check attempt $i failed, retrying in 5s..."
  sleep 5
done
```

### Implementação do Endpoint

O backend deve implementar um endpoint de health check:

```python
# Exemplo Python/FastAPI
@app.get("/health")
def health_check():
    return {"status": "healthy"}
```

---

## Procedimentos de Rollback

### Rollback Manual

Se um deploy falhar ou causar problemas, execute o rollback na VPS:

#### Opção 1: Usar tag anterior

```bash
# Na VPS
cd /app

# Identificar tag anterior
docker images usuario/memoria-backend --format "{{.Tag}}"

# Editar docker-compose.prod.yml para usar tag específica
# image: usuario/memoria-backend:sha-abc1234

# Reiniciar com imagem anterior
docker compose -f docker/docker-compose.prod.yml up -d
```

#### Opção 2: Reverter commit e re-deploy

```bash
# No seu ambiente local
git revert HEAD
git push origin main
# O workflow de deploy será acionado automaticamente
```

#### Opção 3: Deploy manual de versão específica

```bash
# Na VPS
cd /app

# Parar containers atuais
docker compose -f docker/docker-compose.prod.yml down

# Baixar versão específica
docker pull usuario/memoria-backend:sha-abc1234

# Editar compose para usar a tag específica e reiniciar
docker compose -f docker/docker-compose.prod.yml up -d
```

### Rollback de Migration

Se uma migration causou problemas:

```bash
# Na VPS
cd /app

# Reverter última migration
docker compose -f docker/docker-compose.prod.yml run --rm backend alembic downgrade -1

# Verificar status
docker compose -f docker/docker-compose.prod.yml run --rm backend alembic current
```

---

## Troubleshooting

### Falhas no Workflow de CI

#### Problema: Lint falhou

**Sintomas**: Job `lint-frontend` falhou com erros de ESLint

**Solução**:
```bash
cd frontend
npm run lint         # Ver erros
npm run lint -- --fix  # Corrigir automaticamente
```

#### Problema: Testes falharam

**Sintomas**: Job `test-frontend` falhou

**Solução**:
```bash
cd frontend
npm run test         # Executar localmente para ver detalhes
```

### Falhas no Build Docker

#### Problema: Dockerfile não encontrado

**Sintomas**: `unable to prepare context: unable to evaluate symlinks in Dockerfile path`

**Solução**: Verifique que `docker/backend.Dockerfile` existe e está commitado

#### Problema: Falha de autenticação no Docker Hub

**Sintomas**: `Error: denied: requested access to the resource is denied`

**Solução**:
1. Verifique que `DOCKERHUB_USERNAME` e `DOCKERHUB_TOKEN` estão configurados
2. Verifique que o token tem permissão de escrita
3. Verifique que o repositório existe no Docker Hub

### Falhas de SSH

#### Problema: Conexão SSH recusada

**Sintomas**: `ssh: connect to host X port 22: Connection refused`

**Soluções**:
1. Verifique se a VPS está online
2. Verifique se o SSH está habilitado na VPS
3. Verifique se o IP/hostname está correto em `VPS_HOST`
4. Verifique regras de firewall

#### Problema: Autenticação SSH falhou

**Sintomas**: `Permission denied (publickey)`

**Soluções**:
1. Verifique se a chave pública está no `~/.ssh/authorized_keys` da VPS
2. Verifique se `VPS_SSH_KEY` contém a chave privada completa (incluindo headers)
3. Formato correto:
```
-----BEGIN OPENSSH PRIVATE KEY-----
...conteúdo da chave...
-----END OPENSSH PRIVATE KEY-----
```

#### Problema: SSH timeout

**Sintomas**: `ssh: connect to host X port 22: Connection timed out`

**Soluções**:
1. Verifique conectividade de rede da VPS
2. Verifique se a porta 22 está aberta no firewall
3. Aumente timeout se necessário

### Falhas de Migration

#### Problema: Migration falhou

**Sintomas**: `alembic upgrade head` retorna erro

**Soluções**:
```bash
# Na VPS, verificar status atual
docker compose -f docker/docker-compose.prod.yml run --rm backend alembic current

# Ver histórico de migrations
docker compose -f docker/docker-compose.prod.yml run --rm backend alembic history

# Tentar upgrade novamente
docker compose -f docker/docker-compose.prod.yml run --rm backend alembic upgrade head
```

#### Problema: Banco de dados bloqueado

**Sintomas**: `database is locked`

**Solução**: Aguarde conexões finalizarem ou reinicie container do banco

### Falhas de Health Check

#### Problema: Health check falhou após 5 tentativas

**Sintomas**: `WARNING: Health check failed after 5 attempts`

**Soluções**:
1. Verifique se o endpoint `/health` está implementado
2. Verifique se a aplicação está iniciando corretamente:
```bash
docker compose -f docker/docker-compose.prod.yml logs backend
```
3. Verifique se a porta está correta (padrão: 3000)

### Verificação de Logs

#### Logs do GitHub Actions

1. Acesse a aba **Actions** no repositório
2. Clique no workflow que falhou
3. Expanda os steps para ver logs detalhados

#### Logs na VPS

```bash
# Logs de todos os containers
docker compose -f docker/docker-compose.prod.yml logs

# Logs do backend apenas
docker compose -f docker/docker-compose.prod.yml logs backend

# Seguir logs em tempo real
docker compose -f docker/docker-compose.prod.yml logs -f

# Últimas 100 linhas
docker compose -f docker/docker-compose.prod.yml logs --tail=100
```

---

## Monitoramento

### GitHub Actions

- **Aba Actions**: Histórico de todas as execuções
- **Status Checks**: Visíveis em PRs e commits
- **Notificações**: Configure em Settings → Notifications

### VPS

#### Verificar containers ativos

```bash
docker compose -f docker/docker-compose.prod.yml ps
```

#### Verificar uso de recursos

```bash
docker stats
```

#### Verificar logs em tempo real

```bash
docker compose -f docker/docker-compose.prod.yml logs -f
```

### Alertas Recomendados

1. Configure notificações de falha no GitHub Actions
2. Monitore uso de disco na VPS (imagens Docker acumulam)
3. Configure alertas de uptime para o health check endpoint

---

## Referências

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Hub Documentation](https://docs.docker.com/docker-hub/)
- [Vercel CLI Documentation](https://vercel.com/docs/cli)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)

---

_Última atualização: Janeiro 2025_
