import { describe, it, expect } from 'vitest';

/**
 * Este teste falha intencionalmente para validar Cenário 6
 * Objetivo: Verificar que teste falhando causa falha no job com mensagem clara
 */
describe('Validation Scenario 6 - Test Failure', () => {
  it('should intentionally fail to validate test failure handling', () => {
    // Esta assertion vai falhar propositalmente
    expect(true).toBe(false);
  });
});
