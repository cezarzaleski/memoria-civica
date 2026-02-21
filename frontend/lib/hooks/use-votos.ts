import { useState, useEffect, useCallback } from 'react'
import type { PaginationMeta, Voto } from '@/lib/types'
import { buildEndpoint, parsePaginatedPayload, readErrorMessage } from './shared'

export interface UseVotosParams {
  page?: number
  per_page?: number
}

export interface UseVotosReturn {
  data: Voto[]
  pagination: PaginationMeta | null
  loading: boolean
  error: string | null
  refetch: () => void
}

/**
 * Fetches votos for a specific votacao with optional pagination
 */
export function useVotos(votacaoId: number | string | null, params: UseVotosParams = {}): UseVotosReturn {
  const [data, setData] = useState<Voto[]>([])
  const [pagination, setPagination] = useState<PaginationMeta | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const { page, per_page: perPage } = params

  const fetchVotos = useCallback(async () => {
    if (!votacaoId) {
      setData([])
      setPagination(null)
      setError(null)
      setLoading(false)
      return
    }

    try {
      setLoading(true)
      setError(null)

      const endpoint = buildEndpoint(`/api/v1/votacoes/${votacaoId}/votos`, {
        page,
        per_page: perPage,
      })

      const response = await fetch(endpoint)

      if (!response.ok) {
        throw new Error(await readErrorMessage(response, 'Failed to fetch votos'))
      }

      const payload = (await response.json()) as unknown
      const parsedResponse = parsePaginatedPayload<Voto>(payload)
      setData(parsedResponse.data)
      setPagination(parsedResponse.pagination)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error'
      setError(message)
      setData([])
      setPagination(null)
    } finally {
      setLoading(false)
    }
  }, [votacaoId, page, perPage])

  useEffect(() => {
    void fetchVotos()
  }, [fetchVotos])

  return {
    data,
    pagination,
    loading,
    error,
    refetch: fetchVotos,
  }
}
