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
 * Shows SIM, NÃO, ABSTENÇÃO, OBSTRUÇÃO vote counts and percentages
 */
export function PlacarVotos({ placar, title = 'Resultado da Votação' }: PlacarVotosProps) {
  const total = (placar.sim || 0) + (placar.nao || 0) + (placar.abstencao || 0) + (placar.obstrucao || 0)

  const calculatePercentage = (value: number) => {
    if (total === 0) return 0
    return Math.round((value / total) * 100)
  }

  const votos = [
    {
      label: 'Sim',
      value: placar.sim || 0,
      color: 'bg-green-600 dark:bg-green-500',
      textColor: 'text-green-700 dark:text-green-300',
    },
    {
      label: 'Não',
      value: placar.nao || 0,
      color: 'bg-red-600 dark:bg-red-500',
      textColor: 'text-red-700 dark:text-red-300',
    },
    {
      label: 'Abstenção',
      value: placar.abstencao || 0,
      color: 'bg-yellow-600 dark:bg-yellow-500',
      textColor: 'text-yellow-700 dark:text-yellow-300',
    },
    {
      label: 'Obstrução',
      value: placar.obstrucao || 0,
      color: 'bg-blue-600 dark:bg-blue-500',
      textColor: 'text-blue-700 dark:text-blue-300',
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
