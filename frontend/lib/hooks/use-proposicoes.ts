import { useState, useEffect, useCallback } from 'react'
import type { PaginationMeta, Proposicao, ProposicaoCategoria } from '@/lib/types'
import { buildEndpoint, parsePaginatedPayload, readErrorMessage } from './shared'

export interface UseProposicoesParams {
  tipo?: string
  ano?: number
  page?: number
  per_page?: number
}

export interface UseProposicoesReturn {
  data: Proposicao[]
  pagination: PaginationMeta | null
  loading: boolean
  error: string | null
  refetch: () => void
}

export interface UseProposicaoCategoriasParams {
  page?: number
  per_page?: number
}

export interface UseProposicaoCategoriasReturn {
  data: ProposicaoCategoria[]
  pagination: PaginationMeta | null
  loading: boolean
  error: string | null
  refetch: () => void
}

/**
 * Fetches proposicoes list with optional filters and pagination.
 */
export function useProposicoes(params: UseProposicoesParams = {}): UseProposicoesReturn {
  const [data, setData] = useState<Proposicao[]>([])
  const [pagination, setPagination] = useState<PaginationMeta | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const { tipo, ano, page, per_page: perPage } = params

  const fetchProposicoes = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      const endpoint = buildEndpoint('/api/v1/proposicoes', {
        tipo,
        ano,
        page,
        per_page: perPage,
      })

      const response = await fetch(endpoint)

      if (!response.ok) {
        throw new Error(await readErrorMessage(response, 'Failed to fetch proposicoes'))
      }

      const payload = (await response.json()) as unknown
      const parsedResponse = parsePaginatedPayload<Proposicao>(payload)
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
  }, [tipo, ano, page, perPage])

  useEffect(() => {
    void fetchProposicoes()
  }, [fetchProposicoes])

  return {
    data,
    pagination,
    loading,
    error,
    refetch: fetchProposicoes,
  }
}

/**
 * Fetches categorias cívicas linked to a specific proposicao.
 */
export function useProposicaoCategorias(
  proposicaoId: number | string | null,
  params: UseProposicaoCategoriasParams = {}
): UseProposicaoCategoriasReturn {
  const [data, setData] = useState<ProposicaoCategoria[]>([])
  const [pagination, setPagination] = useState<PaginationMeta | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const { page, per_page: perPage } = params

  const fetchCategorias = useCallback(async () => {
    if (!proposicaoId) {
      setData([])
      setPagination(null)
      setError(null)
      setLoading(false)
      return
    }

    try {
      setLoading(true)
      setError(null)

      const endpoint = buildEndpoint(`/api/v1/proposicoes/${proposicaoId}/categorias`, {
        page,
        per_page: perPage,
      })

      const response = await fetch(endpoint)

      if (!response.ok) {
        throw new Error(await readErrorMessage(response, 'Failed to fetch categorias da proposicao'))
      }

      const payload = (await response.json()) as unknown
      const parsedResponse = parsePaginatedPayload<ProposicaoCategoria>(payload)
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
  }, [proposicaoId, page, perPage])

  useEffect(() => {
    void fetchCategorias()
  }, [fetchCategorias])

  return {
    data,
    pagination,
    loading,
    error,
    refetch: fetchCategorias,
  }
}
