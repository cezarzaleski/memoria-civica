'use client'

import React from 'react'
import { Votacao, ResultadoVotacao } from '@/lib/types/votacao'
import { Badge } from '@/components/ui/badge'
import { CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { cn } from '@/lib/utils'

interface VotacaoCardProps {
  votacao: Votacao
}

/**
 * Displays a votacao summary card for use in a feed/list
 * Shows title, date, resultado badge, and placar summary
 */
export function VotacaoCard({ votacao }: VotacaoCardProps) {
  const isAprovado =
    votacao.resultado === ResultadoVotacao.APROVADO ||
    votacao.resultado === ResultadoVotacao.APROVADO_COM_SUBSTITUTIVO

  const formatDate = (date: string) => {
    return new Date(date).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    })
  }

  const formatProposicao = () => {
    const { proposicao } = votacao
    if (!proposicao) return 'Votação'
    return `${proposicao.tipo} ${proposicao.numero}/${proposicao.ano}`
  }

  const ementaTruncated = votacao.proposicao?.ementa
    ? votacao.proposicao.ementa.length > 80
      ? votacao.proposicao.ementa.substring(0, 80) + '...'
      : votacao.proposicao.ementa
    : 'Sem descrição'

  return (
    <article
      className={cn(
        'rounded-lg border border-border bg-card p-6',
        'min-h-[200px] flex flex-col',
        'focus-within:ring-2 focus-within:ring-primary focus-within:ring-offset-2'
      )}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <div className="text-sm font-medium text-muted-foreground mb-1">
            {formatProposicao()}
          </div>
          <CardTitle className="text-lg line-clamp-2">
            {ementaTruncated}
          </CardTitle>
          </div>
          <Badge
            variant={isAprovado ? 'default' : 'destructive'}
            className="whitespace-nowrap flex-shrink-0"
          >
            {votacao.resultado}
          </Badge>
        </div>
        <div className="text-sm text-muted-foreground mt-2">
          {formatDate(votacao.data_hora)}
          {votacao.sigla_orgao ? ` • ${votacao.sigla_orgao}` : ''}
        </div>
      </CardHeader>

      <CardContent className="flex-1 flex flex-col justify-between">
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600 dark:text-green-400">
              {votacao.placar.votos_sim}
            </div>
            <div className="text-xs text-muted-foreground">Sim</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600 dark:text-red-400">
              {votacao.placar.votos_nao}
            </div>
            <div className="text-xs text-muted-foreground">Não</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-slate-600 dark:text-slate-300">
              {votacao.placar.votos_outros}
            </div>
            <div className="text-xs text-muted-foreground">Outros</div>
          </div>
        </div>
      </CardContent>
    </article>
  )
}
