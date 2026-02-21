import { useState, useEffect, useCallback } from 'react'
import type { Votacao } from '@/lib/types'
import { parseSinglePayload, readErrorMessage } from './shared'

interface UseVotacaoReturn {
  data: Votacao | null
  loading: boolean
  error: string | null
  refetch: () => void
}

/**
 * Fetches a single votacao by ID from /api/v1/votacoes/:id endpoint
 */
export function useVotacao(id: number | string | null): UseVotacaoReturn {
  const [data, setData] = useState<Votacao | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchVotacao = useCallback(async () => {
    if (!id) {
      setData(null)
      setError(null)
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
          return
        }

        throw new Error(await readErrorMessage(response, 'Failed to fetch votacao'))
      }

      const payload = (await response.json()) as unknown
      setData(parseSinglePayload<Votacao>(payload))
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error'
      setError(message)
      setData(null)
    } finally {
      setLoading(false)
    }
  }, [id])

  useEffect(() => {
    void fetchVotacao()
  }, [fetchVotacao])

  return {
    data,
    loading,
    error,
    refetch: fetchVotacao,
  }
}
