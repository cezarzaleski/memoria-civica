import { TipoProposicao, type Proposicao } from '@/lib/types';

/**
 * Sample proposição topics relevant to Brazilian Congress
 */
const PROPOSICAO_TOPICS = [
  'Reforma Tributária',
  'Reforma Educacional',
  'Saúde Pública',
  'Previdência Social',
  'Segurança Pública',
  'Meio Ambiente',
  'Direitos Trabalhistas',
  'Reforma Administrativa',
  'Lei de Acesso à Informação',
  'Modernização da Legislação',
  'Combate à Corrupção',
  'Proteção aos Direitos Humanos',
  'Desenvolvimento Sustentável',
  'Energias Renováveis',
  'Infraestrutura',
  'Tecnologia e Inovação',
  'Educação Digital',
  'Inclusão Social',
  'Agricultura Familiar',
  'Defesa do Consumidor',
];

/**
 * Sample bill descriptions/ementas
 */
const EMENTA_TEMPLATES = [
  'Dispõe sobre [TOPIC] e altera a Lei nº {num}.',
  'Institui normas para regulamentação de [TOPIC].',
  'Estabelece diretrizes para [TOPIC] no país.',
  'Cria mecanismo de controle sobre [TOPIC].',
  'Autoriza a implementação de políticas públicas relacionadas a [TOPIC].',
  'Revoga disposições anteriores sobre [TOPIC] e regulamenta nova metodologia.',
  'Define procedimentos para [TOPIC] em âmbito federal.',
  'Determina direitos e deveres relativos a [TOPIC].',
];

/**
 * Select a random proposal type
 */
function selectRandomTipo(): TipoProposicao {
  const tipos = Object.values(TipoProposicao);
  return tipos[Math.floor(Math.random() * tipos.length)];
}

/**
 * Generate random proposition number based on type
 */
function generateProposicaoNumero(tipo: TipoProposicao): number {
  const minNum: Record<string, number> = {
    PL: 1,
    PEC: 1,
    MP: 1,
    PLP: 1,
    PDC: 1,
    REQ: 1,
    RIC: 1,
    PFC: 1,
  };

  const maxNum: Record<string, number> = {
    PL: 5000,
    PEC: 300,
    MP: 1000,
    PLP: 200,
    PDC: 500,
    REQ: 2000,
    RIC: 3000,
    PFC: 1200,
  };

  const min = minNum[tipo] ?? 1;
  const max = maxNum[tipo] ?? 5000;

  return Math.floor(Math.random() * (max - min + 1)) + min;
}

/**
 * Generate a realistic ementa (description) for a proposition
 */
function generateEmenta(): string {
  const topic = PROPOSICAO_TOPICS[Math.floor(Math.random() * PROPOSICAO_TOPICS.length)];
  const template = EMENTA_TEMPLATES[Math.floor(Math.random() * EMENTA_TEMPLATES.length)];
  const num = Math.floor(Math.random() * 15000) + 1000;

  return template.replace('[TOPIC]', topic).replace('{num}', num.toString());
}

/**
 * Generate realistic mock proposition data
 * Called to create propositions for mock votações
 *
 * @param count Number of propositions to generate
 * @returns Array of mock Proposicao objects
 */
export function generateProposicoes(count: number = 50): Proposicao[] {
  const propositions: Proposicao[] = [];
  const currentYear = new Date().getFullYear();

  for (let i = 1; i <= count; i++) {
    const tipo = selectRandomTipo();
    const proposicao: Proposicao = {
      id: i,
      tipo,
      numero: generateProposicaoNumero(tipo),
      ano: currentYear - Math.floor(Math.random() * 3),
      ementa: generateEmenta(),
      // Some propositions may have simplified descriptions
      ementa_simplificada: Math.random() > 0.5 ? `Simplified version of proposition ${i}` : undefined,
      // Some may have an author ID
      autor_id: Math.random() > 0.7 ? Math.floor(Math.random() * 513) + 1 : undefined,
      data_apresentacao: new Date(currentYear - 1, Math.floor(Math.random() * 12), 1).toISOString(),
    };

    propositions.push(proposicao);
  }

  return propositions;
}

/**
 * Get a single proposition by ID
 *
 * @param proposicoes Array of propositions
 * @param id Proposition ID
 * @returns Proposition if found, undefined otherwise
 */
export function getProposicaoById(proposicoes: Proposicao[], id: number): Proposicao | undefined {
  return proposicoes.find((p) => p.id === id);
}
