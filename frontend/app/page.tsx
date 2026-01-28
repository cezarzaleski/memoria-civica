'use client'

import Link from 'next/link'
import { useVotacoes } from '@/lib/hooks/use-votacoes'
import { VotacaoCard } from '@/components/features/votacoes/VotacaoCard'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'

/**
 * Skeleton card component for loading state
 */
function VotacaoCardSkeleton() {
  return (
    <div className="rounded-lg border border-border bg-card p-6 space-y-4">
      <div className="space-y-2">
        <Skeleton className="h-6 w-2/3" />
        <Skeleton className="h-5 w-full" />
      </div>
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="text-center space-y-2">
            <Skeleton className="h-8 w-12 mx-auto" />
            <Skeleton className="h-4 w-16 mx-auto" />
          </div>
        ))}
      </div>
    </div>
  )
}

/**
 * Home page displaying feed of votações
 */
export default function Home() {
  const { data: votacoes, loading, error, refetch } = useVotacoes()

  // Loading state with skeleton cards
  if (loading) {
    return (
      <main className="min-h-screen bg-background">
        <div className="container mx-auto px-4 py-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold tracking-tight mb-2">
              Votações Recentes
            </h1>
            <p className="text-muted-foreground">
              Acompanhe as últimas votações do Plenário da Câmara dos Deputados
            </p>
          </div>

          <div className="grid gap-4">
            {[...Array(3)].map((_, i) => (
              <VotacaoCardSkeleton key={i} />
            ))}
          </div>
        </div>
      </main>
    )
  }

  // Error state with retry functionality
  if (error) {
    return (
      <main className="min-h-screen bg-background">
        <div className="container mx-auto px-4 py-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold tracking-tight mb-2">
              Votações Recentes
            </h1>
          </div>

          <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-6">
            <h2 className="text-lg font-semibold text-destructive mb-2">
              Erro ao carregar votações
            </h2>
            <p className="text-muted-foreground mb-4">
              {error || 'Ocorreu um erro ao buscar as votações. Por favor, tente novamente.'}
            </p>
            <Button onClick={refetch} variant="default">
              Tentar Novamente
            </Button>
          </div>
        </div>
      </main>
    )
  }

  // Empty state when no votações available
  if (!votacoes || votacoes.length === 0) {
    return (
      <main className="min-h-screen bg-background">
        <div className="container mx-auto px-4 py-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold tracking-tight mb-2">
              Votações Recentes
            </h1>
            <p className="text-muted-foreground">
              Acompanhe as últimas votações do Plenário da Câmara dos Deputados
            </p>
          </div>

          <div className="rounded-lg border border-border bg-muted/50 p-12 text-center">
            <h2 className="text-lg font-semibold text-muted-foreground mb-2">
              Nenhuma votação encontrada
            </h2>
            <p className="text-muted-foreground mb-4">
              Não há votações disponíveis no momento. Tente novamente mais tarde.
            </p>
            <Button onClick={refetch} variant="outline">
              Atualizar
            </Button>
          </div>
        </div>
      </main>
    )
  }

  // Main feed with votações
  return (
    <main className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight mb-2">
            Votações Recentes
          </h1>
          <p className="text-muted-foreground">
            Acompanhe as últimas votações do Plenário da Câmara dos Deputados
          </p>
        </div>

        <div className="grid gap-4">
          {votacoes.map((votacao) => (
            <Link
              key={votacao.id}
              href={`/votacoes/${votacao.id}`}
              className="block rounded-lg focus:outline-none"
            >
              <VotacaoCard votacao={votacao} />
            </Link>
          ))}
        </div>

        {votacoes.length > 0 && (
          <div className="mt-8 text-center text-sm text-muted-foreground">
            <p>Exibindo {votacoes.length} votações</p>
          </div>
        )}
      </div>
    </main>
  )
}
