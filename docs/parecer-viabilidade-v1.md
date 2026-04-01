---
title: Parecer de Viabilidade da V1
date: 2026-04-01
status: draft
---

# Parecer de Viabilidade da V1

## 1. Pergunta

O Memoria Civica V1 ja tem base suficiente para ser considerado viavel, principalmente quanto a dados, cobertura real de fontes e honestidade metodologica?

## 2. Resposta Curta

Sim, com recorte claro.

Nota argumentada de viabilidade da V1: **8/10**.

Essa nota vale para a V1 como produto focado em consulta explicavel, especialmente para nomes com historico parlamentar observavel.

Ela nao vale para promessa ampla de cobertura uniforme de qualquer candidato.

## 3. O Que Foi Validado

A rodada 2 testou quatro perfis reais:

- incumbente com historico forte;
- incumbente controverso;
- figura publica com vida parlamentar observavel;
- nome com cobertura limitada.

O comportamento observado mostrou:

- identidade, evidencia e coerencia funcionam bem quando ha base oficial densa;
- `integrity` funciona como triagem prudente, nao como juizo automatizado forte;
- `values_fit` minimo ja consegue gerar sinal util em tema coberto, mas ainda nao de forma ampla;
- a V1 acerta ao parar cedo com `evidencia insuficiente` quando a identidade oficial nao fecha.

## 4. Parecer por Eixo

### 4.1 Dados e Fontes

Parecer: **viavel**

Razao:

- Camara e TSE sustentam bem a espinha dorsal para incumbentes;
- ha base suficiente para identidade, atividade legislativa e historico eleitoral;
- houve instabilidade pontual de endpoint, mas com recuperacao automatica;
- a cobertura cai de forma relevante quando a identidade oficial nao e localizada.

### 4.2 Comparabilidade

Parecer: **viavel com cautela**

Razao:

- incumbentes sao comparaveis entre si com base mais justa;
- figuras com vida parlamentar observavel ainda entram com cautela;
- desafiantes e nomes sem identidade resolvida nao podem ser comparados como se tivessem a mesma densidade de historico.

### 4.3 Metodo

Parecer: **viavel com cautela**

Razao:

- `coherence` e `evidence_level` se sustentam melhor;
- `integrity` e util se tratado como alerta e screening, nao como condenacao narrativa;
- `values_fit` minimo e metodologicamente honesto porque ainda responde insuficiencia quando o tema nao esta coberto.

### 4.4 Experiencia Minima Defensavel

Parecer: **viavel**

Razao:

- o produto ja consegue dizer algo util para quem tem historico observavel;
- tambem consegue dizer `nao sei` de forma honesta quando falta base;
- isso reduz o risco de parecer mais inteligente do que realmente e.

## 5. O Que Ja Esta Pavimentado

- consulta explicavel para incumbentes;
- comparacao inicial entre perfis com historico legislativo;
- metacamada de `evidence_level`;
- screening prudente de `integrity`;
- primeira versao operacional de `values_fit` por watchlist minima;
- regra pratica de parada por `evidencia insuficiente`.

## 6. O Que Ainda E Parcial

- cobertura de `values_fit` por tema;
- comparabilidade para nomes novos ou sem mandato;
- resolucao de identidade para casos fora do melhor cenario;
- robustez operacional em fontes auxiliares mais instaveis.

## 7. O Que Nao Deve Ser Vendido Como Resolvido

- avaliacao justa e ampla de qualquer candidato;
- shortlist confiavel entre perfis muito desiguais;
- ranking absoluto;
- inferencia forte de valores em temas ainda nao cobertos pela watchlist minima.

## 8. Regra de Produto a Preservar

O produto deve responder `evidencia insuficiente` quando:

- a identidade oficial nao for resolvida com seguranca;
- faltar fonte auditavel conectada ao sinal;
- o tema de `values_fit` nao tiver base suficiente;
- a comparacao exigir tratar perfis estruturalmente desiguais como equivalentes.

Essa regra nao e fallback cosmetico. Ela e parte da tese de confiabilidade da V1.

## 9. Conclusao

O projeto deixou de ser uma aposta abstrata.

Hoje ele e tecnicamente e metodologicamente **viavel como V1 focada**, desde que o posicionamento continue claro:

- foco principal em nomes com historico parlamentar observavel;
- uso de fontes oficiais como espinha dorsal;
- comparacao com cautela fora desse nucleo;
- expansao de escopo apenas depois de novas rodadas de validacao.

Em resumo:

- **base tecnica:** 9/10
- **viabilidade do MVP util:** 8/10
- **viabilidade da tese completa hoje:** 7/10

O ponto central nao e mais "da para construir?".

O ponto central agora e "como ampliar cobertura sem romper a honestidade metodologica que tornou a V1 defensavel?".
