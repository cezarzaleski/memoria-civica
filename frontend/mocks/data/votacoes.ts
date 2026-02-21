import { ResultadoVotacao, type Votacao, type Placar } from '@/lib/types';
import { generateProposicoes, getProposicaoById } from './proposicoes';

/**
 * Generate a realistic placar (vote count)
 * Creates plausible vote distributions totaling 513 (Brazilian chamber size)
 * Avoids unrealistic outcomes like 513-0
 */
function generatePlacar(): Placar {
  // Total should sum to 513 (Brazilian Federal Chamber)
  const total = 513;

  // Generate realistic distribution - most votes go to SIM or NAO
  // with smaller number of ABSTENCAO and OBSTRUCAO
  const baseVotes = Math.floor(total * (0.5 + Math.random() * 0.2)); // 50-70% to SIM
  const sim = baseVotes + Math.floor(Math.random() * 20 - 10); // Add variation

  const naoBase = total - sim - Math.floor(Math.random() * 100);
  const nao = Math.max(Math.floor(naoBase * 0.7), 0); // 70% of remainder

  const votosOutros = Math.max(total - sim - nao, 0);

  return {
    votos_sim: Math.max(sim, 0),
    votos_nao: Math.max(nao, 0),
    votos_outros: votosOutros,
  };
}

/**
 * Determine voting result based on placar
 */
function determineResultado(placar: Placar): ResultadoVotacao {
  return placar.votos_sim > placar.votos_nao
    ? ResultadoVotacao.APROVADO
    : ResultadoVotacao.REJEITADO;
}

/**
 * Generate a date within the last 6 months
 */
function generateRecentDate(): Date {
  const today = new Date();
  const sixMonthsAgo = new Date(today.getFullYear(), today.getMonth() - 6, today.getDate());

  const randomTime = Math.random() * (today.getTime() - sixMonthsAgo.getTime()) + sixMonthsAgo.getTime();
  return new Date(randomTime);
}

/**
 * Generate realistic mock votação (voting session) data
 *
 * @param count Number of votações to generate (default: 50)
 * @returns Array of mock Votacao objects sorted by data descending
 */
export function generateVotacoes(count: number = 50): Votacao[] {
  const proposicoes = generateProposicoes(count);
  const votacoes: Votacao[] = [];

  for (let i = 1; i <= count; i++) {
    const proposicao = getProposicaoById(proposicoes, i);
    const placar = generatePlacar();

    const votacao: Votacao = {
      id: i,
      proposicao_id: i,
      proposicao, // Include nested proposicao
      data_hora: generateRecentDate().toISOString(),
      resultado: determineResultado(placar),
      placar,
      eh_nominal: true,
      descricao: `Sessão ${i} de votação`,
      sigla_orgao: 'PLEN',
    };

    votacoes.push(votacao);
  }

  // Sort by date descending (most recent first)
  votacoes.sort((a, b) => new Date(b.data_hora).getTime() - new Date(a.data_hora).getTime());

  return votacoes;
}

/**
 * Get a single votação by ID
 *
 * @param votacoes Array of votações
 * @param id Votação ID
 * @returns Votação if found, undefined otherwise
 */
export function getVotacaoById(votacoes: Votacao[], id: number): Votacao | undefined {
  return votacoes.find((v) => v.id === id);
}
