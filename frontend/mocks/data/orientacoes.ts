import type { Orientacao } from '@/lib/types';

const BANCADAS = ['GOV', 'OPOS', 'PT', 'PL', 'MDB', 'PSD', 'PP', 'PSB', 'UNIÃO', 'REPUBLICANOS'] as const;
const ORIENTACOES = ['Sim', 'Não', 'Liberado', 'Obstrução'] as const;
const TOTAL_VOTACOES_FIXTURE = 50;

function buildCreatedAt(votacaoId: number, bancadaIndex: number): string {
  return new Date(Date.UTC(2025, 0, 1 + votacaoId, 12 + (bancadaIndex % 4), bancadaIndex, 0)).toISOString();
}

function buildOrientacoes(): Orientacao[] {
  const lista: Orientacao[] = [];
  let orientacaoId = 1;

  for (let votacaoId = 1; votacaoId <= TOTAL_VOTACOES_FIXTURE; votacaoId += 1) {
    BANCADAS.forEach((siglaBancada, bancadaIndex) => {
      const orientacao = ORIENTACOES[(votacaoId + bancadaIndex) % ORIENTACOES.length] ?? ORIENTACOES[0];

      lista.push({
        id: orientacaoId,
        votacao_id: votacaoId,
        sigla_bancada: siglaBancada,
        orientacao,
        created_at: buildCreatedAt(votacaoId, bancadaIndex),
      });

      orientacaoId += 1;
    });
  }

  return lista;
}

export const ORIENTACOES_FIXTURES: Orientacao[] = buildOrientacoes();

export function getOrientacoesByVotacaoId(votacaoId: number): Orientacao[] {
  return ORIENTACOES_FIXTURES.filter((orientacao) => orientacao.votacao_id === votacaoId);
}
