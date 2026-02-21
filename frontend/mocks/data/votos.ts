import { TipoVoto, type Voto } from '@/lib/types';
import { generateDeputados, getDeputadoById } from './deputados';

/**
 * Select a random vote type with realistic weighting
 * Most votes are SIM or NAO, fewer are ABSTENCAO or OBSTRUCAO
 */
function selectRandomVotoTipo(): TipoVoto {
  const random = Math.random();

  // 40% likely to be SIM
  if (random < 0.4) return TipoVoto.SIM;
  // 35% likely to be NAO
  if (random < 0.75) return TipoVoto.NAO;
  // 15% likely to be ABSTENCAO
  if (random < 0.9) return TipoVoto.ABSTENCAO;
  // 10% likely to be OBSTRUCAO
  return TipoVoto.OBSTRUCAO;
}

/**
 * Generate realistic mock votos (individual votes) for a votação
 * Generates exactly 513 votes (one per deputy in Brazilian chamber)
 * Each vote includes a reference to the voting deputado
 *
 * @param votacao_id ID of the votação these votes belong to
 * @returns Array of mock Voto objects
 */
export function generateVotos(votacao_id: number): Voto[] {
  const deputados = generateDeputados(513);
  const votos: Voto[] = [];

  for (let i = 1; i <= 513; i++) {
    const deputado = getDeputadoById(deputados, i);

    const voto: Voto = {
      id: votacao_id * 1000 + i,
      votacao_id,
      deputado_id: i,
      deputado, // Include nested deputado for convenience
      voto: selectRandomVotoTipo(),
    };

    votos.push(voto);
  }

  return votos;
}

/**
 * Get a single voto by ID
 *
 * @param votos Array of votos
 * @param id Voto ID
 * @returns Voto if found, undefined otherwise
 */
export function getVotoById(votos: Voto[], id: number): Voto | undefined {
  return votos.find((v) => v.id === id);
}

/**
 * Filter votos by votação ID
 *
 * @param votos Array of votos
 * @param votacao_id Votação ID to filter by
 * @returns Filtered array of votos
 */
export function filterVotosByVotacaoId(votos: Voto[], votacao_id: number): Voto[] {
  return votos.filter((v) => v.votacao_id === votacao_id);
}

/**
 * Count votos by tipo for a specific votação
 *
 * @param votos Array of votos
 * @param votacao_id Votação ID to count votes for
 * @returns Object with count for each vote type
 */
export function countVotosByTipo(votos: Voto[], votacao_id: number) {
  const votosForVotacao = filterVotosByVotacaoId(votos, votacao_id);

  return {
    sim: votosForVotacao.filter((v) => v.voto === TipoVoto.SIM).length,
    nao: votosForVotacao.filter((v) => v.voto === TipoVoto.NAO).length,
    outros: votosForVotacao.filter((v) => ![TipoVoto.SIM, TipoVoto.NAO].includes(v.voto)).length,
  };
}
