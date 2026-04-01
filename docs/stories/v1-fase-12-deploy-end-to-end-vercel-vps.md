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
- [ ] existe configuracao documentada de variaveis de ambiente para front e back
- [ ] existe processo de execucao do backend documentado para a VPS
- [ ] existe smoke test ponta a ponta em ambiente deployado cobrindo `health`, consulta valida e caso ambiguo
- [ ] existe estrategia minima de observacao operacional via logs basicos no backend
- [ ] a documentacao deixa claro o que ainda nao existe nesta primeira versao publica
- [ ] `npm run lint` passa
- [ ] `npm run typecheck` passa
- [ ] `npm test` passa

## Checklist

- [ ] configurar build e runtime do frontend para Vercel
- [ ] configurar build e runtime do backend para VPS
- [ ] documentar `envs`, URLs e fluxo de deploy
- [ ] validar conectividade Vercel -> VPS
- [ ] executar smoke tests do ambiente deployado
- [ ] registrar limitacoes conhecidas da primeira versao publica
- [ ] validar quality gates

## File List

- [ ] `docs/deploy-v1-vercel-vps.md`
- [ ] `apps/web/vercel.json`
- [ ] `apps/api/ecosystem.config.cjs`
- [ ] `package.json`

## Validation Evidence

- [ ] `2026-04-01`: `npm run lint`
- [ ] `2026-04-01`: `npm run typecheck`
- [ ] `2026-04-01`: `npm test`
- [ ] `2026-04-01`: smoke test ponta a ponta em ambiente deployado

## Notes

- Esta fase e de publicacao, nao de ampliacao de escopo do produto.
- O objetivo nao e deixar a infra definitiva. O objetivo e chegar a uma primeira URL real, com configuracao suficientemente clara para iterar.
- O frontend permanece publico e sem autenticacao nesta primeira rodada.
