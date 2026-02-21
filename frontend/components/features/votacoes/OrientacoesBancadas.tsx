'use client'

import React from 'react'
import { Orientacao } from '@/lib/types'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

interface OrientacoesBancadasProps {
  orientacoes: Orientacao[]
  loading?: boolean
  error?: string | null
  emptyMessage?: string
}

function getOrientacaoVariant(orientacao: string): 'default' | 'destructive' | 'secondary' | 'outline' {
  const normalized = orientacao.toLowerCase()

  if (normalized === 'sim') {
    return 'default'
  }

  if (normalized === 'não' || normalized === 'nao') {
    return 'destructive'
  }

  if (normalized === 'obstrução' || normalized === 'obstrucao') {
    return 'outline'
  }

  return 'secondary'
}

function getOrientacaoClassName(orientacao: string): string {
  const normalized = orientacao.toLowerCase()

  if (normalized === 'sim') {
    return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100'
  }

  if (normalized === 'não' || normalized === 'nao') {
    return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100'
  }

  if (normalized === 'obstrução' || normalized === 'obstrucao') {
    return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-100'
  }

  return 'bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-100'
}

/**
 * Exibe orientações por bancada para uma votação.
 */
export function OrientacoesBancadas({
  orientacoes,
  loading = false,
  error = null,
  emptyMessage = 'Não há orientações de bancada para esta votação.',
}: OrientacoesBancadasProps) {
  if (error) {
    return (
      <Card className="border-red-200 dark:border-red-800">
        <CardHeader>
          <CardTitle className="text-lg text-red-700 dark:text-red-300">
            Orientações de Bancada
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
        </CardContent>
      </Card>
    )
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Orientações de Bancada</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {[...Array(6)].map((_, index) => (
            <div
              key={index}
              className="h-10 rounded bg-gray-200 dark:bg-gray-700 animate-pulse"
            />
          ))}
        </CardContent>
      </Card>
    )
  }

  if (orientacoes.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Orientações de Bancada</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">{emptyMessage}</p>
        </CardContent>
      </Card>
    )
  }

  const orientacoesOrdenadas = [...orientacoes].sort((a, b) =>
    a.sigla_bancada.localeCompare(b.sigla_bancada, 'pt-BR')
  )

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">
          Orientações de Bancada ({orientacoesOrdenadas.length})
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ul className="space-y-2">
          {orientacoesOrdenadas.map((orientacao) => (
            <li
              key={orientacao.id}
              className="rounded-lg border p-3 flex items-center justify-between gap-3"
            >
              <span className="font-medium text-sm">{orientacao.sigla_bancada}</span>
              <Badge
                className={cn(getOrientacaoClassName(orientacao.orientacao))}
                variant={getOrientacaoVariant(orientacao.orientacao)}
              >
                {orientacao.orientacao}
              </Badge>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  )
}
