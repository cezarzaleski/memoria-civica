'use client'

import React from 'react'
import { ProposicaoCategoria } from '@/lib/types'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

interface CategoriasCivicasProps {
  categorias: ProposicaoCategoria[]
  loading?: boolean
  error?: string | null
  emptyMessage?: string
}

/**
 * Exibe categorias cívicas associadas à proposição da votação.
 */
export function CategoriasCivicas({
  categorias,
  loading = false,
  error = null,
  emptyMessage = 'Esta votação não possui categorias cívicas associadas.',
}: CategoriasCivicasProps) {
  if (error) {
    return (
      <Card className="border-red-200 dark:border-red-800">
        <CardHeader>
          <CardTitle className="text-lg text-red-700 dark:text-red-300">
            Categorias Cívicas
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
          <CardTitle className="text-lg">Categorias Cívicas</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {[...Array(3)].map((_, index) => (
            <div
              key={index}
              className="h-16 rounded bg-gray-200 dark:bg-gray-700 animate-pulse"
            />
          ))}
        </CardContent>
      </Card>
    )
  }

  if (categorias.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Categorias Cívicas</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">{emptyMessage}</p>
        </CardContent>
      </Card>
    )
  }

  const categoriasOrdenadas = [...categorias].sort((first, second) => {
    const nomePrimeira = first.categoria?.nome ?? `Categoria #${first.categoria_id}`
    const nomeSegunda = second.categoria?.nome ?? `Categoria #${second.categoria_id}`

    return (
      nomePrimeira.localeCompare(nomeSegunda, 'pt-BR') ||
      first.origem.localeCompare(second.origem, 'pt-BR')
    )
  })

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">
          Categorias Cívicas ({categoriasOrdenadas.length})
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ul className="space-y-3">
          {categoriasOrdenadas.map((item) => {
            const nomeCategoria = item.categoria?.nome ?? `Categoria #${item.categoria_id}`
            const descricaoCategoria = item.categoria?.descricao

            return (
              <li key={item.id} className="rounded-lg border p-3">
                <div className="flex items-center justify-between gap-3">
                  <p className="font-medium text-sm">{nomeCategoria}</p>
                  <Badge variant={item.origem === 'manual' ? 'default' : 'secondary'}>
                    {item.origem}
                  </Badge>
                </div>
                {descricaoCategoria && (
                  <p className="text-sm text-muted-foreground mt-2">{descricaoCategoria}</p>
                )}
              </li>
            )
          })}
        </ul>
      </CardContent>
    </Card>
  )
}
