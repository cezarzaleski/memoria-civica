import { useState, useEffect, useCallback } from 'react'
import type { Votacao } from '@/lib/types'

interface UseVotacaoReturn {
  data: Votacao | null
  loading: boolean
  error: string | null
  refetch: () => void
}

export function useVotacao(votacaoId: string | null): UseVotacaoReturn {
  const [data, setData] = useState<Votacao | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchVotacao = useCallback(async () => {
    if (!votacaoId) {
      setLoading(false)
      setData(null)
      setError(null)
      return
    }

    try {
      setLoading(true)
      setError(null)

      const response = await fetch(`/api/v1/votacoes/${votacaoId}`)

      if (response.status === 404) {
        setError('Votação não encontrada')
        setData(null)
        return
      }

      if (!response.ok) {
        throw new Error(`Erro ao buscar votação: ${response.status}`)
      }

      const result = await response.json()
      setData(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido')
      setData(null)
    } finally {
      setLoading(false)
    }
  }, [votacaoId])

  useEffect(() => {
    fetchVotacao()
  }, [fetchVotacao])

  const refetch = useCallback(() => {
    fetchVotacao()
  }, [fetchVotacao])

  return { data, loading, error, refetch }
}
