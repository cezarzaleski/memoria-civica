'use client'

import React from 'react'
import { Voto, TipoVoto } from '@/lib/types/voto'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

interface ListaVotosProps {
  votos: Voto[]
  loading?: boolean
  error?: string | null
  emptyMessage?: string
}

const getTipoBadgeVariant = (tipo: TipoVoto) => {
  switch (tipo) {
    case TipoVoto.SIM:
      return 'default'
    case TipoVoto.NAO:
      return 'destructive'
    case TipoVoto.ABSTENCAO:
      return 'secondary'
    case TipoVoto.OBSTRUCAO:
      return 'outline'
    default:
      return 'secondary'
  }
}

const getTipoColor = (tipo: TipoVoto) => {
  switch (tipo) {
    case TipoVoto.SIM:
      return 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200'
    case TipoVoto.NAO:
      return 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200'
    case TipoVoto.ABSTENCAO:
      return 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200'
    case TipoVoto.OBSTRUCAO:
      return 'bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200'
    default:
      return ''
  }
}

/**
 * Displays a list of votes from a votacao
 * Shows each deputado and their vote type
 */
export function ListaVotos({
  votos,
  loading = false,
  error = null,
  emptyMessage = 'Nenhum voto encontrado',
}: ListaVotosProps) {
  if (error) {
    return (
      <Card className="border-red-200 dark:border-red-800">
        <CardContent className="pt-6">
          <div className="text-center text-red-600 dark:text-red-400">
            <p className="font-medium">Erro ao carregar votos</p>
            <p className="text-sm">{error}</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Votos</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-12 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  if (votos.length === 0) {
    return (
      <Card>
        <CardContent className="pt-6">
          <p className="text-center text-muted-foreground">{emptyMessage}</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Votos ({votos.length})</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2 max-h-[500px] overflow-y-auto">
          {votos.map((voto) => (
            <div
              key={voto.id}
              className={cn(
                'p-3 rounded-lg border flex items-center justify-between gap-2 hover:bg-accent/50 transition-colors',
                'sm:p-4'
              )}
            >
              <div className="min-w-0 flex-1">
                <p className="font-medium text-sm sm:text-base truncate">
                  {voto.deputado?.nome || 'Deputado desconhecido'}
                </p>
                {voto.deputado?.partido && (
                  <p className="text-xs sm:text-sm text-muted-foreground">
                    {voto.deputado.partido} - {voto.deputado.uf}
                  </p>
                )}
              </div>
              <Badge
                className={getTipoColor(voto.tipo)}
                variant={getTipoBadgeVariant(voto.tipo)}
              >
                {voto.tipo}
              </Badge>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
