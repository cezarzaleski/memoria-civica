import { useState, useEffect, useCallback } from 'react'
import type { CategoriaCivica, PaginationMeta } from '@/lib/types'
import { buildEndpoint, parsePaginatedPayload, readErrorMessage } from './shared'

export interface UseCategoriasCivicasParams {
  page?: number
  per_page?: number
}

export interface UseCategoriasCivicasReturn {
  data: CategoriaCivica[]
  pagination: PaginationMeta | null
  loading: boolean
  error: string | null
  refetch: () => void
}

/**
 * Fetches categorias cívicas list with pagination.
 */
export function useCategoriasCivicas(
  params: UseCategoriasCivicasParams = {}
): UseCategoriasCivicasReturn {
  const [data, setData] = useState<CategoriaCivica[]>([])
  const [pagination, setPagination] = useState<PaginationMeta | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const { page, per_page: perPage } = params

  const fetchCategoriasCivicas = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      const endpoint = buildEndpoint('/api/v1/categorias-civicas', {
        page,
        per_page: perPage,
      })

      const response = await fetch(endpoint)

      if (!response.ok) {
        throw new Error(await readErrorMessage(response, 'Failed to fetch categorias civicas'))
      }

      const payload = (await response.json()) as unknown
      const parsedResponse = parsePaginatedPayload<CategoriaCivica>(payload)
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
  }, [page, perPage])

  useEffect(() => {
    void fetchCategoriasCivicas()
  }, [fetchCategoriasCivicas])

  return {
    data,
    pagination,
    loading,
    error,
    refetch: fetchCategoriasCivicas,
  }
}
