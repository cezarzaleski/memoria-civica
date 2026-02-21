'use client'

import React from 'react'
import { Placar } from '@/lib/types/votacao'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { cn } from '@/lib/utils'

interface PlacarVotosProps {
  placar: Placar
  title?: string
}

/**
 * Displays voting results as visual bars with percentages
 * Shows SIM, NÃO e OUTROS vote counts and percentages
 */
export function PlacarVotos({ placar, title = 'Resultado da Votação' }: PlacarVotosProps) {
  const total = placar.votos_sim + placar.votos_nao + placar.votos_outros

  const calculatePercentage = (value: number) => {
    if (total === 0) return 0
    return Math.round((value / total) * 100)
  }

  const votos = [
    {
      label: 'Sim',
      value: placar.votos_sim,
      color: 'bg-green-600 dark:bg-green-500',
      textColor: 'text-green-700 dark:text-green-300',
    },
    {
      label: 'Não',
      value: placar.votos_nao,
      color: 'bg-red-600 dark:bg-red-500',
      textColor: 'text-red-700 dark:text-red-300',
    },
    {
      label: 'Outros',
      value: placar.votos_outros,
      color: 'bg-slate-600 dark:bg-slate-500',
      textColor: 'text-slate-700 dark:text-slate-300',
    },
  ]

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="text-lg">{title}</CardTitle>
        <p className="text-sm text-muted-foreground mt-2">Total: {total} votos</p>
      </CardHeader>
      <CardContent className="space-y-6">
        {votos.map((voto) => {
          const percentage = calculatePercentage(voto.value)
          return (
            <div key={voto.label} className="space-y-2">
              <div className="flex justify-between items-center">
                <label className="font-medium text-sm">{voto.label}</label>
                <span className={cn('font-bold', voto.textColor)}>
                  {voto.value} ({percentage}%)
                </span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 overflow-hidden">
                <div
                  className={`${voto.color} h-full transition-all duration-500`}
                  style={{ width: `${percentage}%` }}
                />
              </div>
            </div>
          )
        })}
      </CardContent>
    </Card>
  )
}
