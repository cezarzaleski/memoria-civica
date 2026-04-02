---
title: Deploy V1 - Vercel e VPS
date: 2026-04-01
status: draft
---

# Deploy V1 - Vercel e VPS

## 1. Objetivo

Publicar a primeira versao navegavel do Memoria Civica com:

- frontend `Next.js` na Vercel;
- backend HTTP minimo na VPS;
- proxy server-side da Vercel apontando para a API da VPS.

Esta primeira rodada continua:

- sem autenticacao;
- sem banco;
- sem fila;
- sem observabilidade externa dedicada.

## 1.1 Orquestracao por GitHub Actions

O fluxo recomendado passa a ser:

- `ci.yml` para verificacao continua;
- `deploy-staging.yml` para publicar staging em `push` na `main`;
- `deploy-branch.yml` para publicar manualmente uma branch especifica em staging;
- `deploy-vps-reusable.yml` como rotina reaproveitavel de release-based deploy na VPS.

## 2. Variaveis de Ambiente

### 2.1 Backend na VPS

Segredos esperados no GitHub Environment `staging`:

- `VPS_HOST`
- `VPS_USER`
- `VPS_PORT`
- `VPS_SSH_KEY`
- `DEPLOY_PATH`
- `VPS_APP_PORT`
- `MCP_BRASIL_LOCAL_PATH`
- `API_PUBLIC_URL`

Variaveis aplicadas no runtime:

- `HOST=0.0.0.0`
- `PORT=3000` ou valor de `VPS_APP_PORT`
- `NODE_ENV=production`
- `MCP_BRASIL_LOCAL_PATH=/opt/mcp-brasil`

### 2.2 Frontend na Vercel

Segredos esperados no GitHub Environment `staging`:

- `VERCEL_TOKEN`
- `VERCEL_ORG_ID`
- `VERCEL_PROJECT_ID`

Variavel esperada dentro do projeto da Vercel:

- `MEMORIA_CIVICA_API_BASE_URL=https://api.seu-dominio.com`

## 3. Backend na VPS

### 3.1 Preparacao

No servidor:

```bash
git clone <repo> /opt/memoria-civica
cd /opt/memoria-civica
npm install
```

Se o `mcp-brasil` for usado via clone local:

```bash
git clone <repo-mcp-brasil> /opt/mcp-brasil
```

### 3.2 Processo

Usar o arquivo [ecosystem.config.cjs](/Users/cezar.zaleski/workspace/pessoal/memoria_civica/apps/api/ecosystem.config.cjs). O deploy via Action publica releases em `releases/<sha>` e atualiza o symlink `current`.

```bash
pm2 start apps/api/ecosystem.config.cjs
pm2 save
pm2 status
```

### 3.3 Health Check

```bash
curl -s http://127.0.0.1:3000/health
```

Resposta esperada:

```json
{"status":"ok"}
```

## 4. Frontend na Vercel

### 4.1 Configuracao do Projeto

Na Vercel:

1. importar o repositório;
2. definir `Root Directory` como `apps/web`;
3. manter o framework `Next.js`;
4. configurar `MEMORIA_CIVICA_API_BASE_URL`;
5. publicar.

O arquivo [vercel.json](/Users/cezar.zaleski/workspace/pessoal/memoria_civica/apps/web/vercel.json) garante o install e build a partir da raiz do monorepo.

## 4.2 Fluxo por Action

- `deploy-staging.yml`: publica automaticamente o estado da `main` em staging
- `deploy-branch.yml`: publica manualmente qualquer `ref` em staging

Nos dois casos:

- o frontend faz deploy `preview` na Vercel;
- o backend publica release nova na VPS;
- a pipeline executa smoke test da API e da URL web retornada pela Vercel.

## 5. Smoke Test Ponta a Ponta

### 5.1 Health da API

```bash
curl -s https://api.seu-dominio.com/health
```

### 5.2 Consulta Valida

```bash
curl -s https://api.seu-dominio.com/consultas \
  -H 'content-type: application/json' \
  -d '{"candidate_name":"Tabata Amaral","uf":"SP"}'
```

### 5.3 Caso Ambiguo

```bash
curl -s https://api.seu-dominio.com/consultas \
  -H 'content-type: application/json' \
  -d '{"candidate_name":"Joao Silva"}'
```

Resultado esperado:

- `candidate.resolution_kind = "ambiguous"`
- `candidate.requires` com `uf` e/ou `party`
- `traffic_light = "gray"`

### 5.4 Smoke Test na URL Web

Na interface publicada:

1. abrir a home;
2. consultar um nome resolvido;
3. validar render do resultado na mesma tela;
4. consultar um nome ambiguo;
5. validar pedido de `UF` e/ou `partido`.

## 6. Logs Operacionais Minimos

Nesta primeira versao:

- usar logs de processo do PM2 para o backend;
- usar logs nativos da Vercel para o frontend e proxy.

Comandos uteis:

```bash
pm2 logs memoria-civica-api
pm2 status
```

## 7. Limitacoes Conhecidas

- nao existe autenticacao;
- nao existe rate limit dedicado;
- nao existe persistencia de consultas;
- nao existe monitoramento externo estruturado;
- o backend depende da disponibilidade operacional das fontes e do `mcp-brasil`;
- a publicacao real ainda depende de URL da VPS, DNS e credenciais da Vercel.
