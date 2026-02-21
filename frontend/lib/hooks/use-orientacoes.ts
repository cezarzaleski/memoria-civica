import { useState, useEffect, useCallback } from 'react'
import type { Orientacao, PaginationMeta } from '@/lib/types'
import { buildEndpoint, parsePaginatedPayload, readErrorMessage } from './shared'

export interface UseOrientacoesParams {
  page?: number
  per_page?: number
}

export interface UseOrientacoesReturn {
  data: Orientacao[]
  pagination: PaginationMeta | null
  loading: boolean
  error: string | null
  refetch: () => void
}

/**
 * Fetches orientacoes for a specific votacao with optional pagination.
 */
export function useOrientacoes(
  votacaoId: number | string | null,
  params: UseOrientacoesParams = {}
): UseOrientacoesReturn {
  const [data, setData] = useState<Orientacao[]>([])
  const [pagination, setPagination] = useState<PaginationMeta | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const { page, per_page: perPage } = params

  const fetchOrientacoes = useCallback(async () => {
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

      const endpoint = buildEndpoint(`/api/v1/votacoes/${votacaoId}/orientacoes`, {
        page,
        per_page: perPage,
      })

      const response = await fetch(endpoint)

      if (!response.ok) {
        throw new Error(await readErrorMessage(response, 'Failed to fetch orientacoes'))
      }

      const payload = (await response.json()) as unknown
      const parsedResponse = parsePaginatedPayload<Orientacao>(payload)
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
    void fetchOrientacoes()
  }, [fetchOrientacoes])

  return {
    data,
    pagination,
    loading,
    error,
    refetch: fetchOrientacoes,
  }
}
