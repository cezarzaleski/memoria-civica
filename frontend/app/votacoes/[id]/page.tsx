'use client'

import React from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { useVotacao } from '@/lib/hooks/use-votacao'
import { useVotos } from '@/lib/hooks/use-votos'
import { useOrientacoes } from '@/lib/hooks/use-orientacoes'
import { useProposicaoCategorias } from '@/lib/hooks/use-proposicoes'
import { VotacaoDetalhes } from '@/components/features/votacoes/VotacaoDetalhes'
import { PlacarVotos } from '@/components/features/votacoes/PlacarVotos'
import { ListaVotos } from '@/components/features/votacoes/ListaVotos'
import { OrientacoesBancadas } from '@/components/features/votacoes/OrientacoesBancadas'
import { CategoriasCivicas } from '@/components/features/votacoes/CategoriasCivicas'

/**
 * Mock LLM explanation for voting details
 * In production, this would come from an API endpoint
 */
function getMockLLMExplanation(votacao_id: string): string {
  const explanations: Record<string, string> = {
    '1': 'Esta votação aprovou um projeto de lei que simplifica o processo de registro de pequenas empresas, permitindo que microempreendedores façam isso totalmente online em menos de 24 horas.',
    '2': 'A votação rejeitou uma proposta de emenda constitucional que aumentaria os impostos sobre a classe média. A maioria dos deputados entendeu que isso prejudicaria a economia.',
    '3': 'Este projeto de lei obriga as escolas públicas a oferecer refeições sem alergênios para crianças com alergias alimentares.',
    '4': 'A votação aprovou medidas de proteção à mata atlântica, proibindo desmatamento em áreas críticas sem autorização prévia.',
    '5': 'Este projeto facilita o acesso de pessoas com deficiência a espaços públicos, exigindo acessibilidade em novos prédios governamentais.',
  }

  return (
    explanations[votacao_id] ||
    'Este projeto de lei trata de um tema importante para o país. A votação reflete as posições dos deputados sobre esta matéria.'
  )
}

/**
 * Página de detalhes da votação
 * Exibe informações completas sobre uma votação específica
 */
export default function VotacaoPage() {
  const params = useParams()
  const votacaoId = params.id as string

  const { data: votacao, loading: votacaoLoading, error: votacaoError } = useVotacao(votacaoId)
  const { data: votos, loading: votosLoading, error: votosError } = useVotos(votacaoId)
  const { data: orientacoes, loading: orientacoesLoading, error: orientacoesError } = useOrientacoes(votacaoId)
  const {
    data: categorias,
    loading: categoriasLoading,
    error: categoriasError,
  } = useProposicaoCategorias(votacao?.proposicao_id ?? null)

  // Estados de carregamento
  if (votacaoLoading) {
    return (
      <div className="container mx-auto px-4 py-6 md:py-8">
        <div className="h-12 w-24 bg-gray-200 dark:bg-gray-700 rounded animate-pulse mb-6" />
        <div className="space-y-6">
          <div className="h-40 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
          <div className="h-64 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
          <div className="h-96 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
        </div>
      </div>
    )
  }

  // Estado de erro - votação não encontrada
  if (votacaoError || !votacao) {
    return (
      <div className="container mx-auto px-4 py-6 md:py-8">
        <Link href="/">
          <Button variant="outline" className="mb-6">
            ← Voltar para o Feed
          </Button>
        </Link>

        <div className="text-center py-12">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
            Votação não encontrada
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            A votação que você procura não existe ou foi removida.
          </p>
          <Link href="/">
            <Button>Ir para o Feed</Button>
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-6 md:py-8 space-y-6">
      {/* Botão voltar */}
      <Link href="/">
        <Button variant="outline">
          ← Voltar para o Feed
        </Button>
      </Link>

      {/* Detalhes da Votação */}
      <VotacaoDetalhes
        votacao={votacao}
        loading={false}
        llmExplanation={getMockLLMExplanation(votacaoId)}
        llmLoading={false}
      />

      {/* Placar de Votos */}
      <PlacarVotos placar={votacao.placar} title="Resultado da Votação" />

      {/* Lista de Votos dos Deputados */}
      <ListaVotos votos={votos} loading={votosLoading} error={votosError} />

      {/* Orientações de Bancada */}
      <OrientacoesBancadas
        orientacoes={orientacoes}
        loading={orientacoesLoading}
        error={orientacoesError}
      />

      {/* Categorias cívicas da proposição vinculada */}
      <CategoriasCivicas
        categorias={categorias}
        loading={categoriasLoading}
        error={categoriasError}
        emptyMessage="Nenhuma categoria cívica foi associada à proposição desta votação."
      />

      {/* Informações adicionais no rodapé */}
      <div className="text-center text-xs text-muted-foreground py-4 border-t">
        <p>
          Dados das votações da Câmara dos Deputados - Última atualização:{' '}
          {new Date().toLocaleDateString('pt-BR')}
        </p>
      </div>
    </div>
  )
}
