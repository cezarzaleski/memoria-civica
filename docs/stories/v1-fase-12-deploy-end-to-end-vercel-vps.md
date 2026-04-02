---
title: V1 Fase 12 - Deploy ponta a ponta Vercel mais VPS
status: Ready
date: 2026-04-01
owner: sm
---

# Story

Publicar a primeira versao navegavel do Memoria Civica com frontend na Vercel e backend na VPS, garantindo um caminho simples de configuracao, smoke test e operacao basica para validar o produto em ambiente real.

## Acceptance Criteria

- [ ] o frontend `Next.js` publica com sucesso na Vercel
- [ ] o backend HTTP publica com sucesso na VPS e responde externamente
- [ ] a Vercel consegue encaminhar consultas para a API da VPS pelo proxy configurado
- [x] existe configuracao documentada de variaveis de ambiente para front e back
- [x] existe processo de execucao do backend documentado para a VPS
- [x] existe smoke test ponta a ponta automatizavel para ambiente deployado cobrindo `health`, consulta valida e caso ambiguo
- [x] existe estrategia minima de observacao operacional via logs basicos no backend
- [x] a documentacao deixa claro o que ainda nao existe nesta primeira versao publica
- [x] `npm run lint` passa
- [x] `npm run typecheck` passa
- [x] `npm test` passa

## Checklist

- [x] configurar build e runtime do frontend para Vercel
- [x] configurar build e runtime do backend para VPS
- [x] documentar `envs`, URLs e fluxo de deploy
- [x] preparar validacao de conectividade Vercel -> VPS
- [x] preparar smoke tests do ambiente deployado
- [x] registrar limitacoes conhecidas da primeira versao publica
- [x] validar quality gates

## File List

- [x] `docs/deploy-v1-vercel-vps.md`
- [x] `apps/web/vercel.json`
- [x] `apps/api/ecosystem.config.cjs`
- [x] `.github/workflows/ci.yml`
- [x] `.github/workflows/deploy-vps-reusable.yml`
- [x] `.github/workflows/deploy-staging.yml`
- [x] `.github/workflows/deploy-branch.yml`
- [x] `apps/api/Dockerfile`
- [x] `docker-compose.backend.yml`
- [x] `.dockerignore`
- [x] `package.json`
- [x] `eslint.config.js`

## Validation Evidence

- [x] `2026-04-01`: `npm run lint`
- [x] `2026-04-01`: `npm run typecheck`
- [x] `2026-04-01`: `npm test`
- [ ] `2026-04-01`: smoke test ponta a ponta em ambiente deployado via workflows de deploy

## Notes

- Esta fase e de publicacao, nao de ampliacao de escopo do produto.
- O objetivo nao e deixar a infra definitiva. O objetivo e chegar a uma primeira URL real, com configuracao suficientemente clara para iterar.
- O frontend permanece publico e sem autenticacao nesta primeira rodada.
