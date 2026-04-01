---
title: V1 Fase 11 - Web app minimo com Next.js na Vercel
status: Ready
date: 2026-04-01
owner: architect
---

# Story

Construir a primeira interface web do Memoria Civica com Next.js, mobile-first e em uma unica tela, para que um usuario leigo consiga consultar um candidato e ver o resultado na mesma experiencia, incluindo o estado de desambiguacao quando faltar `UF` e/ou `partido`.

## Acceptance Criteria

- [ ] existe uma aplicacao `Next.js` em `apps/web` preparada para deploy na Vercel
- [ ] a home entrega uma unica tela com foco em consulta nominal simples
- [ ] o fluxo inicial exige apenas o nome do candidato; `UF` e `partido` podem ser preenchidos quando necessario
- [ ] o resultado aparece na mesma tela, sem navegacao para outra rota
- [ ] quando a API responder ambiguidade forte, a tela mostra um estado simples e acionavel pedindo `UF` e/ou `partido`
- [ ] a interface prioriza linguagem simples, pouco ruído visual e leitura confortavel em celular
- [ ] existe `manifest` minimo e configuracao inicial de PWA sem compromisso de uso offline
- [ ] a app usa uma rota server-side/proxy na propria Vercel para falar com a API da VPS
- [ ] testes cobrem ao menos o fluxo feliz, o estado de ambiguidade e um erro de resposta da API
- [ ] `npm run lint` passa
- [ ] `npm run typecheck` passa
- [ ] `npm test` passa

## Checklist

- [ ] criar `apps/web` com Next.js e App Router
- [ ] montar tela unica de consulta e resultado
- [ ] modelar estado de loading, erro, ambiguidade e resultado final
- [ ] implementar rota proxy da Vercel para a API da VPS
- [ ] configurar `manifest` e metadados minimos de app instalavel
- [ ] alinhar copy e hierarquia visual com a persona da Dona Maria
- [ ] cobrir os fluxos principais com testes
- [ ] validar quality gates

## File List

- [ ] `apps/web/package.json`
- [ ] `apps/web/app/page.tsx`
- [ ] `apps/web/app/api/consultas/route.ts`
- [ ] `apps/web/app/layout.tsx`
- [ ] `apps/web/app/globals.css`
- [ ] `apps/web/app/manifest.ts`
- [ ] `apps/web/components/consulta-form.tsx`
- [ ] `apps/web/components/consulta-result.tsx`
- [ ] `tests/web-consulta-page.test.tsx`
- [ ] `tests/web-consulta-proxy.test.ts`

## Validation Evidence

- [ ] `2026-04-01`: `npm run lint`
- [ ] `2026-04-01`: `npm run typecheck`
- [ ] `2026-04-01`: `npm test`

## Notes

- Esta fase nao tenta resolver autenticacao, dashboard, analytics ou comparacao multipla.
- O objetivo e colocar a consulta validada do CLI dentro de uma experiencia web minima e usavel.
- A desambiguacao permanece na mesma tela porque isso reduz atrito e serve melhor a persona definida para a V1.
