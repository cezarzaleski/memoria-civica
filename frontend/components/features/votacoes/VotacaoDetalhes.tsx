'use client'

import React from 'react'
import { Votacao } from '@/lib/types/votacao'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

interface VotacaoDetalhesProps {
  votacao: Votacao
  loading?: boolean
  onBack?: () => void
  llmExplanation?: string
  llmLoading?: boolean
}

/**
 * Displays full votacao details including proposicao and LLM explanation
 */
export function VotacaoDetalhes({
  votacao,
  loading = false,
  onBack,
  llmExplanation,
  llmLoading = false,
}: VotacaoDetalhesProps) {
  const formatDate = (date: string) => {
    return new Date(date).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="h-40 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
        <div className="h-32 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
        <div className="h-40 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {onBack && (
        <Button variant="outline" onClick={onBack} className="mb-4">
          ← Voltar
        </Button>
      )}

      <Card>
        <CardHeader>
          {onBack && <div className="flex items-start justify-between gap-4 mb-4" />}
          <CardTitle className="text-2xl">
            {votacao.proposicao?.descricao || 'Votação'}
          </CardTitle>
          <CardDescription className="mt-4">
            {votacao.data && formatDate(votacao.data)}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {votacao.proposicao?.tipo && (
            <div>
              <label className="font-medium text-sm">Tipo de Proposição</label>
              <p className="text-sm text-muted-foreground mt-1">
                {votacao.proposicao.tipo}
              </p>
            </div>
          )}

          {votacao.proposicao?.tema && (
            <div>
              <label className="font-medium text-sm">Tema</label>
              <p className="text-sm text-muted-foreground mt-1">
                {votacao.proposicao.tema}
              </p>
            </div>
          )}

          {votacao.resultado && (
            <div>
              <label className="font-medium text-sm">Resultado</label>
              <div className="mt-2">
                <Badge
                  variant={votacao.resultado === 'APROVADO' ? 'default' : 'destructive'}
                >
                  {votacao.resultado}
                </Badge>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {(llmExplanation || llmLoading) && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Explicação (IA)</CardTitle>
            <CardDescription>
              Resumo gerado por inteligência artificial
            </CardDescription>
          </CardHeader>
          <CardContent>
            {llmLoading ? (
              <div className="space-y-2">
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse w-5/6" />
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse w-4/6" />
              </div>
            ) : (
              <p className="text-sm leading-relaxed text-muted-foreground">
                {llmExplanation || 'Explicação não disponível'}
              </p>
            )}
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Resultado da Votação</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            <div className="text-center p-3 rounded-lg bg-green-50 dark:bg-green-900/20">
              <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                {votacao.placar?.sim || 0}
              </div>
              <div className="text-xs text-muted-foreground mt-1">Sim</div>
            </div>
            <div className="text-center p-3 rounded-lg bg-red-50 dark:bg-red-900/20">
              <div className="text-2xl font-bold text-red-600 dark:text-red-400">
                {votacao.placar?.nao || 0}
              </div>
              <div className="text-xs text-muted-foreground mt-1">Não</div>
            </div>
            <div className="text-center p-3 rounded-lg bg-yellow-50 dark:bg-yellow-900/20">
              <div className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">
                {votacao.placar?.abstencao || 0}
              </div>
              <div className="text-xs text-muted-foreground mt-1">Abstenção</div>
            </div>
            <div className="text-center p-3 rounded-lg bg-blue-50 dark:bg-blue-900/20">
              <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                {votacao.placar?.obstrucao || 0}
              </div>
              <div className="text-xs text-muted-foreground mt-1">Obstrução</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
