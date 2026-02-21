import { useState, useEffect, useCallback } from 'react'
import type { PaginationMeta, Votacao, VotacaoProposicao } from '@/lib/types'
import { buildEndpoint, parsePaginatedPayload, readErrorMessage } from './shared'

export interface UseVotacoesParams {
  sigla_orgao?: string
  eh_nominal?: boolean
  page?: number
  per_page?: number
}

export interface UseVotacoesReturn {
  data: Votacao[]
  pagination: PaginationMeta | null
  loading: boolean
  error: string | null
  refetch: () => void
}

export interface UseVotacaoProposicoesParams {
  page?: number
  per_page?: number
}

export interface UseVotacaoProposicoesReturn {
  data: VotacaoProposicao[]
  pagination: PaginationMeta | null
  loading: boolean
  error: string | null
  refetch: () => void
}

/**
 * Fetches votacoes from /api/v1/votacoes endpoint with optional filters and pagination
 */
export function useVotacoes(params: UseVotacoesParams = {}): UseVotacoesReturn {
  const [data, setData] = useState<Votacao[]>([])
  const [pagination, setPagination] = useState<PaginationMeta | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const { sigla_orgao: siglaOrgao, eh_nominal: ehNominal, page, per_page: perPage } = params

  const fetchVotacoes = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      const endpoint = buildEndpoint('/api/v1/votacoes', {
        sigla_orgao: siglaOrgao,
        eh_nominal: ehNominal,
        page,
        per_page: perPage,
      })

      const response = await fetch(endpoint)

      if (!response.ok) {
        throw new Error(await readErrorMessage(response, 'Failed to fetch votacoes'))
      }

      const payload = (await response.json()) as unknown
      const parsedResponse = parsePaginatedPayload<Votacao>(payload)
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
  }, [siglaOrgao, ehNominal, page, perPage])

  useEffect(() => {
    void fetchVotacoes()
  }, [fetchVotacoes])

  return {
    data,
    pagination,
    loading,
    error,
    refetch: fetchVotacoes,
  }
}

/**
 * Fetches proposicoes related to a specific votacao with optional pagination
 */
export function useVotacaoProposicoes(
  votacaoId: number | string | null,
  params: UseVotacaoProposicoesParams = {}
): UseVotacaoProposicoesReturn {
  const [data, setData] = useState<VotacaoProposicao[]>([])
  const [pagination, setPagination] = useState<PaginationMeta | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const { page, per_page: perPage } = params

  const fetchVotacaoProposicoes = useCallback(async () => {
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

      const endpoint = buildEndpoint(`/api/v1/votacoes/${votacaoId}/proposicoes`, {
        page,
        per_page: perPage,
      })

      const response = await fetch(endpoint)

      if (!response.ok) {
        throw new Error(await readErrorMessage(response, 'Failed to fetch votacao proposicoes'))
      }

      const payload = (await response.json()) as unknown
      const parsedResponse = parsePaginatedPayload<VotacaoProposicao>(payload)
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
    void fetchVotacaoProposicoes()
  }, [fetchVotacaoProposicoes])

  return {
    data,
    pagination,
    loading,
    error,
    refetch: fetchVotacaoProposicoes,
  }
}
