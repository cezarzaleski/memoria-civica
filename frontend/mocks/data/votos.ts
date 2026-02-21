import { TipoVoto, type Placar, type Voto } from '@/lib/types';
import { DEPUTADOS_FIXTURES } from './deputados';

const PADROES_POR_VOTACAO: readonly TipoVoto[][] = [
  [
    TipoVoto.SIM,
    TipoVoto.SIM,
    TipoVoto.SIM,
    TipoVoto.SIM,
    TipoVoto.NAO,
    TipoVoto.NAO,
    TipoVoto.ABSTENCAO,
    TipoVoto.OBSTRUCAO,
    TipoVoto.ART_17,
    TipoVoto.SIM,
  ],
  [
    TipoVoto.NAO,
    TipoVoto.NAO,
    TipoVoto.NAO,
    TipoVoto.NAO,
    TipoVoto.SIM,
    TipoVoto.SIM,
    TipoVoto.ABSTENCAO,
    TipoVoto.OBSTRUCAO,
    TipoVoto.ART_17,
    TipoVoto.NAO,
  ],
  [
    TipoVoto.SIM,
    TipoVoto.SIM,
    TipoVoto.SIM,
    TipoVoto.NAO,
    TipoVoto.NAO,
    TipoVoto.SIM,
    TipoVoto.ABSTENCAO,
    TipoVoto.OBSTRUCAO,
    TipoVoto.ART_17,
    TipoVoto.NAO,
  ],
];

function resolveTipoVoto(votacaoId: number, deputadoId: number): TipoVoto {
  const padrao = PADROES_POR_VOTACAO[(votacaoId - 1) % PADROES_POR_VOTACAO.length] ?? PADROES_POR_VOTACAO[0];
  return padrao[(deputadoId - 1) % padrao.length] ?? TipoVoto.SIM;
}

export function generateVotos(votacao_id: number): Voto[] {
  return DEPUTADOS_FIXTURES.map((deputado) => ({
    id: votacao_id * 1000 + deputado.id,
    votacao_id,
    deputado_id: deputado.id,
    deputado,
    voto: resolveTipoVoto(votacao_id, deputado.id),
  }));
}

export function getVotoById(votos: Voto[], id: number): Voto | undefined {
  return votos.find((voto) => voto.id === id);
}

export function filterVotosByVotacaoId(votos: Voto[], votacao_id: number): Voto[] {
  return votos.filter((voto) => voto.votacao_id === votacao_id);
}

export function countVotosByTipo(votos: Voto[], votacao_id: number) {
  const votosDaVotacao = filterVotosByVotacaoId(votos, votacao_id);

  return {
    sim: votosDaVotacao.filter((voto) => voto.voto === TipoVoto.SIM).length,
    nao: votosDaVotacao.filter((voto) => voto.voto === TipoVoto.NAO).length,
    outros: votosDaVotacao.filter((voto) => ![TipoVoto.SIM, TipoVoto.NAO].includes(voto.voto)).length,
  };
}

export function buildPlacarFromVotacao(votacaoId: number): Placar {
  const votos = generateVotos(votacaoId);
  const { sim, nao, outros } = countVotosByTipo(votos, votacaoId);

  return {
    votos_sim: sim,
    votos_nao: nao,
    votos_outros: outros,
  };
}
