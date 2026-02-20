import { useState, useEffect } from 'react'
import { Deputado } from '@/lib/types/deputado'

interface UseDeputadosParams {
  nome?: string
  partido?: string
  uf?: string
}

interface UseDeputadosReturn {
  data: Deputado[]
  loading: boolean
  error: string | null
  refetch: () => void
}

/**
 * Fetches deputados from /api/v1/deputados endpoint with optional filters
 * @param params - Filter parameters (nome, partido, uf)
 * @returns Object with data, loading, error states
 */
export function useDeputados(params?: UseDeputadosParams): UseDeputadosReturn {
  const [data, setData] = useState<Deputado[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchDeputados = async () => {
    try {
      setLoading(true)
      setError(null)

      const queryParams = new URLSearchParams()
      if (params?.nome) {
        queryParams.append('nome', params.nome)
      }
      if (params?.partido) {
        queryParams.append('partido', params.partido)
      }
      if (params?.uf) {
        queryParams.append('uf', params.uf)
      }

      const queryString = queryParams.toString()
      const endpoint = queryString ? `/api/v1/deputados?${queryString}` : '/api/v1/deputados'

      const response = await fetch(endpoint)

      if (!response.ok) {
        throw new Error(`Failed to fetch deputados: ${response.status}`)
      }

      const deputados = await response.json()
      setData(Array.isArray(deputados) ? deputados : [])
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error'
      setError(message)
      setData([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDeputados()
  }, [params?.nome, params?.partido, params?.uf])

  return {
    data,
    loading,
    error,
    refetch: fetchDeputados,
  }
}
