---
title: V1 Fase 11 - Web app minimo com Next.js na Vercel
status: Ready for Review
date: 2026-04-01
owner: architect
---

# Story

Construir a primeira interface web do Memoria Civica com Next.js, mobile-first e em uma unica tela, para que um usuario leigo consiga consultar um candidato e ver o resultado na mesma experiencia, incluindo o estado de desambiguacao quando faltar `UF` e/ou `partido`.

## Acceptance Criteria

- [x] existe uma aplicacao `Next.js` em `apps/web` preparada para deploy na Vercel
- [x] a home entrega uma unica tela com foco em consulta nominal simples
- [x] o fluxo inicial exige apenas o nome do candidato; `UF` e `partido` podem ser preenchidos quando necessario
- [x] o resultado aparece na mesma tela, sem navegacao para outra rota
- [x] quando a API responder ambiguidade forte, a tela mostra um estado simples e acionavel pedindo `UF` e/ou `partido`
- [x] a interface prioriza linguagem simples, pouco ruído visual e leitura confortavel em celular
- [x] existe `manifest` minimo e configuracao inicial de PWA sem compromisso de uso offline
- [x] a app usa uma rota server-side/proxy na propria Vercel para falar com a API da VPS
- [x] testes cobrem ao menos o fluxo feliz, o estado de ambiguidade e um erro de resposta da API
- [x] `npm run lint` passa
- [x] `npm run typecheck` passa
- [x] `npm test` passa

## Checklist

- [x] criar `apps/web` com Next.js e App Router
- [x] montar tela unica de consulta e resultado
- [x] modelar estado de loading, erro, ambiguidade e resultado final
- [x] implementar rota proxy da Vercel para a API da VPS
- [x] configurar `manifest` e metadados minimos de app instalavel
- [x] alinhar copy e hierarquia visual com a persona da Dona Maria
- [x] cobrir os fluxos principais com testes
- [x] validar quality gates

## File List

- [x] `apps/web/package.json`
- [x] `apps/web/next-env.d.ts`
- [x] `apps/web/app/page.tsx`
- [x] `apps/web/app/api/consultas/route.ts`
- [x] `apps/web/app/layout.tsx`
- [x] `apps/web/app/globals.css`
- [x] `apps/web/app/manifest.ts`
- [x] `apps/web/components/consulta-form.tsx`
- [x] `apps/web/components/consulta-result.tsx`
- [x] `tests/web-consulta-page.test.tsx`
- [x] `tests/web-consulta-proxy.test.ts`
- [x] `package.json`
- [x] `tsconfig.json`
- [x] `eslint.config.js`

## Validation Evidence

- [x] `2026-04-01`: `npm run lint`
- [x] `2026-04-01`: `npm run typecheck`
- [x] `2026-04-01`: `npm test`

## Notes

- Esta fase nao tenta resolver autenticacao, dashboard, analytics ou comparacao multipla.
- O objetivo e colocar a consulta validada do CLI dentro de uma experiencia web minima e usavel.
- A desambiguacao permanece na mesma tela porque isso reduz atrito e serve melhor a persona definida para a V1.
