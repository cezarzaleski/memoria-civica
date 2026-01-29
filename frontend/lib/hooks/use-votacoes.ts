import { useState, useEffect, useCallback } from 'react'
import type { Votacao } from '@/lib/types'

interface UseVotacoesReturn {
  data: Votacao[]
  loading: boolean
  error: string | null
  refetch: () => void
}

export function useVotacoes(): UseVotacoesReturn {
  const [data, setData] = useState<Votacao[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchVotacoes = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      const response = await fetch('/api/v1/votacoes')

      if (!response.ok) {
        throw new Error(`Erro ao buscar votações: ${response.status}`)
      }

      const result = await response.json()
      setData(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido')
      setData([])
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchVotacoes()
  }, [fetchVotacoes])

  const refetch = useCallback(() => {
    fetchVotacoes()
  }, [fetchVotacoes])

  return { data, loading, error, refetch }
}
