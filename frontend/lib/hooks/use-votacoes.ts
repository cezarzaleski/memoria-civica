import { useState, useEffect } from 'react'
import { Votacao } from '@/lib/types/votacao'

interface UseVotacoesReturn {
  data: Votacao[]
  loading: boolean
  error: string | null
  refetch: () => void
}

/**
 * Fetches votacoes from /api/v1/votacoes endpoint
 * @returns Object with data, loading, error states
 */
export function useVotacoes(): UseVotacoesReturn {
  const [data, setData] = useState<Votacao[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchVotacoes = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await fetch('/api/v1/votacoes')

      if (!response.ok) {
        throw new Error(`Failed to fetch votacoes: ${response.status}`)
      }

      const votacoes = await response.json()
      setData(Array.isArray(votacoes) ? votacoes : [])
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error'
      setError(message)
      setData([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchVotacoes()
  }, [])

  return {
    data,
    loading,
    error,
    refetch: fetchVotacoes,
  }
}
