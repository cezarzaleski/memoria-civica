# Review Queue Casos Sensiveis Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Registrar `review_queue` como metadado operacional para consultas ambiguas ou sensiveis sem alterar o payload funcional da resposta.

**Architecture:** O `QueryOrchestrator` passa a detectar gatilhos de revisao e anexar entradas estruturadas ao `QueryExecutionRecord`. O contrato publico `ConsultationResponse` permanece intacto; apenas a camada de observabilidade/execucao recebe o novo bloco.

**Tech Stack:** TypeScript, Vitest, arquitetura atual de `QueryOrchestrator` + `QueryExecutionRecord`

---

### Task 1: Travar os gatilhos em testes

**Files:**
- Modify: `tests/query-orchestrator.test.ts`
- Modify: `tests/consulta-entrypoint.test.ts`

- [ ] **Step 1: Write the failing tests**
- [ ] **Step 2: Run the targeted tests to verify they fail**
- [ ] **Step 3: Confirm the expected failures are missing `review_queue` metadata**

### Task 2: Implementar o contrato operacional minimo

**Files:**
- Modify: `packages/memoria-civica/src/domain/models.ts`
- Modify: `packages/memoria-civica/src/observability/query-execution.ts`
- Modify: `packages/memoria-civica/src/services/query-orchestrator.ts`

- [ ] **Step 1: Add review queue types to `QueryExecutionRecord` observability**
- [ ] **Step 2: Add helper to append review queue entries**
- [ ] **Step 3: Register ambiguity, integrity sensitivity and complementary journalism triggers in `QueryOrchestrator`**
- [ ] **Step 4: Run the targeted tests to verify they pass**

### Task 3: Validar e atualizar a story

**Files:**
- Modify: `docs/stories/v1-fase-6-review-queue-casos-sensiveis.md`

- [ ] **Step 1: Run `npm run lint`**
- [ ] **Step 2: Run `npm run typecheck`**
- [ ] **Step 3: Run `npm test`**
- [ ] **Step 4: Update checklist, file list and validation evidence in the story**
