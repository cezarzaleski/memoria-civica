import { useState, useEffect } from 'react'
import { Voto } from '@/lib/types/voto'

interface UseVotosReturn {
  data: Voto[]
  loading: boolean
  error: string | null
  refetch: () => void
}

/**
 * Fetches votos for a specific votacao
 * @param votacaoId - ID of the votacao to fetch votes for
 * @returns Object with data, loading, error states
 */
export function useVotos(votacaoId: string | null): UseVotosReturn {
  const [data, setData] = useState<Voto[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchVotos = async () => {
    if (!votacaoId) {
      setData([])
      setLoading(false)
      return
    }

    try {
      setLoading(true)
      setError(null)

      const response = await fetch(`/api/v1/votacoes/${votacaoId}/votos`)

      if (!response.ok) {
        throw new Error(`Failed to fetch votos: ${response.status}`)
      }

      const votos = await response.json()
      setData(Array.isArray(votos) ? votos : [])
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error'
      setError(message)
      setData([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchVotos()
  }, [votacaoId])

  return {
    data,
    loading,
    error,
    refetch: fetchVotos,
  }
}
