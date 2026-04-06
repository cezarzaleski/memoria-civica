# API HTTP minima da V1

Esta aplicacao expoe a consulta do Memoria Civica por HTTP para rodar na VPS.

## Variaveis de ambiente minimas

- `HOST`: host de bind do servidor HTTP. Padrao: `0.0.0.0`
- `PORT`: porta do servidor HTTP. Padrao: `3000`
- `MCP_BRASIL_RUNTIME`: seleciona como o `mcp-brasil` sera iniciado. Padrao: `uvx`
- `MCP_BRASIL_LOCAL_PATH`: caminho local do projeto `mcp-brasil` quando quiser usar checkout local em vez de `uvx`

## Runtime em Docker

O `Dockerfile` da API instala `mcp-brasil` e `truststore` dentro da imagem e define
`MCP_BRASIL_RUNTIME=python`. Nesse modo, a API sobe o `mcp-brasil` via `stdio`
usando o modulo Python ja empacotado no build, sem depender de clone local na VPS.

## Execucao local

```bash
npm run api:start
```

## Execucao local em container

```bash
docker compose -f docker-compose.backend.yml up -d --build
curl -s http://127.0.0.1:3000/health
```

## Endpoints

- `GET /health`
- `POST /consultas`
