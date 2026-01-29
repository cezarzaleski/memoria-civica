import { useState, useEffect, useCallback } from 'react'
import type { Deputado } from '@/lib/types'

interface UseDeputadosFilters {
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

export function useDeputados(filters?: UseDeputadosFilters): UseDeputadosReturn {
  const [data, setData] = useState<Deputado[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchDeputados = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      const params = new URLSearchParams()

      if (filters?.nome) {
        params.append('nome', filters.nome)
      }
      if (filters?.partido) {
        params.append('partido', filters.partido)
      }
      if (filters?.uf) {
        params.append('uf', filters.uf)
      }

      const queryString = params.toString()
      const url = `/api/v1/deputados${queryString ? `?${queryString}` : ''}`

      const response = await fetch(url)

      if (!response.ok) {
        throw new Error(`Erro ao buscar deputados: ${response.status}`)
      }

      const result = await response.json()
      setData(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido')
      setData([])
    } finally {
      setLoading(false)
    }
  }, [filters?.nome, filters?.partido, filters?.uf])

  useEffect(() => {
    fetchDeputados()
  }, [fetchDeputados])

  const refetch = useCallback(() => {
    fetchDeputados()
  }, [fetchDeputados])

  return { data, loading, error, refetch }
}
