import { useState, useEffect } from 'react'
import { Votacao } from '@/lib/types/votacao'

interface UseVotacaoReturn {
  data: Votacao | null
  loading: boolean
  error: string | null
  refetch: () => void
}

/**
 * Fetches a single votacao by ID from /api/v1/votacoes/:id endpoint
 * @param id - ID of the votacao to fetch
 * @returns Object with data, loading, error states
 */
export function useVotacao(id: string | null): UseVotacaoReturn {
  const [data, setData] = useState<Votacao | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchVotacao = async () => {
    if (!id) {
      setData(null)
      setLoading(false)
      return
    }

    try {
      setLoading(true)
      setError(null)

      const response = await fetch(`/api/v1/votacoes/${id}`)

      if (!response.ok) {
        if (response.status === 404) {
          setError('Votação não encontrada')
          setData(null)
        } else {
          throw new Error(`Failed to fetch votacao: ${response.status}`)
        }
      } else {
        const votacao = await response.json()
        setData(votacao || null)
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error'
      setError(message)
      setData(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchVotacao()
  }, [id])

  return {
    data,
    loading,
    error,
    refetch: fetchVotacao,
  }
}
