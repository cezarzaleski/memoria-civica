# API HTTP minima da V1

Esta aplicacao expoe a consulta do Memoria Civica por HTTP para rodar na VPS.

## Variaveis de ambiente minimas

- `HOST`: host de bind do servidor HTTP. Padrao: `0.0.0.0`
- `PORT`: porta do servidor HTTP. Padrao: `3000`
- `MCP_BRASIL_LOCAL_PATH`: caminho local do projeto `mcp-brasil` quando a VPS usar checkout local em vez de `uvx`

## Execucao local

```bash
npm run api:start
```

## Endpoints

- `GET /health`
- `POST /consultas`
