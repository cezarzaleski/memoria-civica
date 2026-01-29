import { useState, useEffect, useCallback } from 'react'
import type { Voto } from '@/lib/types'

interface UseVotosReturn {
  data: Voto[]
  loading: boolean
  error: string | null
  refetch: () => void
}

export function useVotos(votacaoId: string | null): UseVotosReturn {
  const [data, setData] = useState<Voto[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchVotos = useCallback(async () => {
    if (!votacaoId) {
      setLoading(false)
      setData([])
      setError(null)
      return
    }

    try {
      setLoading(true)
      setError(null)

      const response = await fetch(`/api/v1/votacoes/${votacaoId}/votos`)

      if (!response.ok) {
        throw new Error(`Erro ao buscar votos: ${response.status}`)
      }

      const result = await response.json()
      setData(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido')
      setData([])
    } finally {
      setLoading(false)
    }
  }, [votacaoId])

  useEffect(() => {
    fetchVotos()
  }, [fetchVotos])

  const refetch = useCallback(() => {
    fetchVotos()
  }, [fetchVotos])

  return { data, loading, error, refetch }
}
