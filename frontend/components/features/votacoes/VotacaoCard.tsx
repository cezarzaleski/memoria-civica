'use client'

import React from 'react'
import { Votacao, ResultadoVotacao } from '@/lib/types/votacao'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

interface VotacaoCardProps {
  votacao: Votacao
  onClick?: () => void
}

/**
 * Displays a votacao summary card for use in a feed/list
 * Shows title, date, resultado badge, and placar summary
 */
export function VotacaoCard({ votacao, onClick }: VotacaoCardProps) {
  const isAprovado = votacao.resultado === ResultadoVotacao.APROVADO

  const formatDate = (date: string) => {
    return new Date(date).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    })
  }

  return (
    <Card
      className={cn(
        'cursor-pointer transition-all hover:shadow-md active:scale-95 min-h-[200px] flex flex-col',
        'touch-target'
      )}
      onClick={onClick}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-4">
          <CardTitle className="text-lg line-clamp-2 flex-1">
            {votacao.proposicao?.descricao || 'Votação'}
          </CardTitle>
          <Badge
            variant={isAprovado ? 'default' : 'destructive'}
            className="whitespace-nowrap"
          >
            {votacao.resultado}
          </Badge>
        </div>
        <div className="text-sm text-muted-foreground">
          {votacao.proposicao?.tipo && (
            <span className="font-medium">{votacao.proposicao.tipo}</span>
          )}
          {votacao.data && (
            <span className="ml-2">{formatDate(votacao.data)}</span>
          )}
        </div>
      </CardHeader>

      <CardContent className="flex-1 flex flex-col justify-between">
        <div className="grid grid-cols-2 gap-4 mb-4 sm:grid-cols-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600 dark:text-green-400">
              {votacao.placar?.sim || 0}
            </div>
            <div className="text-xs text-muted-foreground">Sim</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600 dark:text-red-400">
              {votacao.placar?.nao || 0}
            </div>
            <div className="text-xs text-muted-foreground">Não</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">
              {votacao.placar?.abstencao || 0}
            </div>
            <div className="text-xs text-muted-foreground">Abstenção</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
              {votacao.placar?.obstrucao || 0}
            </div>
            <div className="text-xs text-muted-foreground">Obstrução</div>
          </div>
        </div>

        {votacao.proposicao?.tema && (
          <div className="text-sm text-muted-foreground border-t pt-3">
            <span className="font-medium">Tema:</span> {votacao.proposicao.tema}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
