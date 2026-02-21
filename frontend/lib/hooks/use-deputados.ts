import { useState, useEffect, useCallback } from 'react'
import type { Deputado, PaginationMeta } from '@/lib/types'
import { buildEndpoint, parsePaginatedPayload, readErrorMessage } from './shared'

export interface UseDeputadosParams {
  nome?: string
  partido?: string
  uf?: string
  page?: number
  per_page?: number
}

export interface UseDeputadosReturn {
  data: Deputado[]
  pagination: PaginationMeta | null
  loading: boolean
  error: string | null
  refetch: () => void
}

/**
 * Fetches deputados from /api/v1/deputados endpoint with optional filters and pagination
 */
export function useDeputados(params: UseDeputadosParams = {}): UseDeputadosReturn {
  const [data, setData] = useState<Deputado[]>([])
  const [pagination, setPagination] = useState<PaginationMeta | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const { nome, partido, uf, page, per_page: perPage } = params

  const fetchDeputados = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      const endpoint = buildEndpoint('/api/v1/deputados', {
        nome,
        partido,
        uf,
        page,
        per_page: perPage,
      })

      const response = await fetch(endpoint)

      if (!response.ok) {
        throw new Error(await readErrorMessage(response, 'Failed to fetch deputados'))
      }

      const payload = (await response.json()) as unknown
      const parsedResponse = parsePaginatedPayload<Deputado>(payload)
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
  }, [nome, partido, uf, page, perPage])

  useEffect(() => {
    void fetchDeputados()
  }, [fetchDeputados])

  return {
    data,
    pagination,
    loading,
    error,
    refetch: fetchDeputados,
  }
}
