import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { useVotacoes } from '@/lib/hooks/use-votacoes'

describe('useVotacoes', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should return empty data and loading true initially', () => {
    const { result } = renderHook(() => useVotacoes())

    expect(result.current.data).toEqual([])
    expect(result.current.loading).toBe(true)
    expect(result.current.error).toBeNull()
  })

  it('should fetch votacoes from endpoint', async () => {
    const mockVotacoes = [
      {
        id: '1',
        data: '2024-01-15',
        resultado: 'APROVADO',
        placar: { sim: 200, nao: 100, abstencao: 50, obstrucao: 13 },
        proposicao: { id: '1', tipo: 'PL', descricao: 'Test', tema: 'Test' },
      },
    ]

    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockVotacoes),
      })
    ) as any

    const { result } = renderHook(() => useVotacoes())

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.data).toEqual(mockVotacoes)
    expect(result.current.error).toBeNull()
  })

  it('should handle error when fetch fails', async () => {
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: false,
        status: 500,
      })
    ) as any

    const { result } = renderHook(() => useVotacoes())

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.error).toBeTruthy()
    expect(result.current.data).toEqual([])
  })

  it('should handle network error', async () => {
    global.fetch = vi.fn(() =>
      Promise.reject(new Error('Network error'))
    ) as any

    const { result } = renderHook(() => useVotacoes())

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.error).toContain('Network error')
    expect(result.current.data).toEqual([])
  })

  it('should have refetch function', async () => {
    const mockVotacoes = [
      {
        id: '1',
        data: '2024-01-15',
        resultado: 'APROVADO',
        placar: { sim: 200, nao: 100, abstencao: 50, obstrucao: 13 },
        proposicao: { id: '1', tipo: 'PL', descricao: 'Test', tema: 'Test' },
      },
    ]

    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockVotacoes),
      })
    ) as any

    const { result } = renderHook(() => useVotacoes())

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(typeof result.current.refetch).toBe('function')
  })
})
