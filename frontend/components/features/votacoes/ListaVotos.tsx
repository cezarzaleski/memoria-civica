'use client'

import React, { useMemo, useState } from 'react'
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

type SortOrder = 'nome-asc' | 'nome-desc' | 'partido-asc'
type FilterType = 'todos' | TipoVoto

/**
 * Displays a list of votes from a votacao with filtering and sorting
 * Shows each deputado and their vote type
 */
export function ListaVotos({
  votos,
  loading = false,
  error = null,
  emptyMessage = 'Nenhum voto encontrado',
}: ListaVotosProps) {
  const [filterType, setFilterType] = useState<FilterType>('todos')
  const [sortOrder, setSortOrder] = useState<SortOrder>('nome-asc')

  const partidos = useMemo(() => {
    return [...new Set(votos.map((v) => v.deputado?.partido).filter(Boolean))]
      .sort() as string[]
  }, [votos])

  const [filterPartido, setFilterPartido] = useState<string>('todos')

  const filteredAndSortedVotos = useMemo(() => {
    let result = votos

    // Aplicar filtro por tipo de voto
    if (filterType !== 'todos') {
      result = result.filter((v) => v.tipo === filterType)
    }

    // Aplicar filtro por partido
    if (filterPartido !== 'todos') {
      result = result.filter((v) => v.deputado?.partido === filterPartido)
    }

    // Aplicar ordenação
    result = [...result].sort((a, b) => {
      const nomeA = a.deputado?.nome || ''
      const nomeB = b.deputado?.nome || ''
      const partidoA = a.deputado?.partido || ''
      const partidoB = b.deputado?.partido || ''

      switch (sortOrder) {
        case 'nome-asc':
          return nomeA.localeCompare(nomeB, 'pt-BR')
        case 'nome-desc':
          return nomeB.localeCompare(nomeA, 'pt-BR')
        case 'partido-asc':
          return (
            partidoA.localeCompare(partidoB, 'pt-BR') ||
            nomeA.localeCompare(nomeB, 'pt-BR')
          )
        default:
          return 0
      }
    })

    return result
  }, [votos, filterType, filterPartido, sortOrder])

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
        <CardTitle className="text-lg">
          Votos ({filteredAndSortedVotos.length} de {votos.length})
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Filtros e Ordenação */}
        <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 md:grid-cols-4">
          {/* Filtro por Tipo de Voto */}
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-muted-foreground">Tipo</label>
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value as FilterType)}
              className="text-xs px-2 py-1 border rounded bg-background"
            >
              <option value="todos">Todos</option>
              <option value={TipoVoto.SIM}>Sim</option>
              <option value={TipoVoto.NAO}>Não</option>
              <option value={TipoVoto.ABSTENCAO}>Abstenção</option>
              <option value={TipoVoto.OBSTRUCAO}>Obstrução</option>
            </select>
          </div>

          {/* Filtro por Partido */}
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-muted-foreground">Partido</label>
            <select
              value={filterPartido}
              onChange={(e) => setFilterPartido(e.target.value)}
              className="text-xs px-2 py-1 border rounded bg-background"
            >
              <option value="todos">Todos</option>
              {partidos.map((partido) => (
                <option key={partido} value={partido}>
                  {partido}
                </option>
              ))}
            </select>
          </div>

          {/* Ordenação */}
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-muted-foreground">Ordenar</label>
            <select
              value={sortOrder}
              onChange={(e) => setSortOrder(e.target.value as SortOrder)}
              className="text-xs px-2 py-1 border rounded bg-background"
            >
              <option value="nome-asc">Nome (A-Z)</option>
              <option value="nome-desc">Nome (Z-A)</option>
              <option value="partido-asc">Partido</option>
            </select>
          </div>
        </div>

        {/* Lista de Votos */}
        <div className="space-y-2 max-h-[500px] overflow-y-auto">
          {filteredAndSortedVotos.map((voto) => (
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

        {filteredAndSortedVotos.length === 0 && (
          <p className="text-center text-sm text-muted-foreground py-4">
            Nenhum voto encontrado com os filtros selecionados
          </p>
        )}
      </CardContent>
    </Card>
  )
}
