// Este arquivo contém erro de linting intencional para validar Cenário 5
// Deve causar falha no job frontend mas não bloquear job etl

export function testLintFailure() {
  // Variável declarada mas não utilizada (eslint error)
  const unusedVariable = 'isto causará erro de linting';

  console.log('Teste de falha de linting');
}
