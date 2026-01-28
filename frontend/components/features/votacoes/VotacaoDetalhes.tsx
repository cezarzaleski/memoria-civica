'use client'

import React from 'react'
import { Votacao } from '@/lib/types/votacao'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'

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

  const getProposicaoTitle = () => {
    if (!votacao.proposicao) return 'Votação'
    const { tipo, numero, ano } = votacao.proposicao
    return `${tipo} ${numero}/${ano}`
  }

  const buildDocumentLink = () => {
    if (!votacao.proposicao) return null
    const { tipo, numero, ano } = votacao.proposicao
    // Link para Câmara dos Deputados com tipo/numero/ano
    return `https://www.camara.leg.br/internet/sitaqweb/resultadoPesquisa.asp?tipo=${tipo}&numero=${numero}&ano=${ano}`
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

  const documentLink = buildDocumentLink()

  return (
    <div className="space-y-4">
      {onBack && (
        <Button variant="outline" onClick={onBack} className="mb-4">
          ← Voltar
        </Button>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">
            {getProposicaoTitle()}
          </CardTitle>
          <CardDescription className="mt-4">
            {votacao.data && formatDate(votacao.data)}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {votacao.proposicao?.ementa && (
            <div>
              <label className="font-medium text-sm">Ementa</label>
              <p className="text-sm text-muted-foreground mt-1">
                {votacao.proposicao.ementa}
              </p>
            </div>
          )}

          {votacao.proposicao?.tipo && (
            <div>
              <label className="font-medium text-sm">Tipo de Proposição</label>
              <p className="text-sm text-muted-foreground mt-1">
                {votacao.proposicao.tipo}
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

          {documentLink && (
            <div>
              <label className="font-medium text-sm">Documento Oficial</label>
              <div className="mt-2">
                <a
                  href={documentLink}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 underline text-sm"
                >
                  Ver na Câmara dos Deputados →
                </a>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {(llmExplanation || llmLoading) && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Explicação Simplificada</CardTitle>
            <CardDescription>
              Resumo em linguagem acessível
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
    </div>
  )
}
