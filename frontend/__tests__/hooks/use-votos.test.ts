import { describe, it, expect, beforeEach, vi } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { useVotos } from '@/lib/hooks/use-votos'

describe('useVotos', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should return empty data when votacaoId is null', async () => {
    const { result } = renderHook(() => useVotos(null))

    expect(result.current.data).toEqual([])
    expect(result.current.loading).toBe(false)
    expect(result.current.error).toBeNull()
  })

  it('should fetch votos for given votacaoId', async () => {
    const mockVotos = [
      {
        id: '1',
        tipo: 'SIM',
        deputado: {
          id: '1',
          nome: 'João Silva',
          partido: 'PT',
          uf: 'SP',
        },
      },
      {
        id: '2',
        tipo: 'NAO',
        deputado: {
          id: '2',
          nome: 'Maria Santos',
          partido: 'PSD',
          uf: 'RJ',
        },
      },
    ]

    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockVotos),
      })
    ) as any

    const { result } = renderHook(() => useVotos('votacao-123'))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(global.fetch).toHaveBeenCalledWith(
      '/api/v1/votacoes/votacao-123/votos'
    )
    expect(result.current.data).toEqual(mockVotos)
    expect(result.current.error).toBeNull()
  })

  it('should handle 404 error when votacao not found', async () => {
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: false,
        status: 404,
      })
    ) as any

    const { result } = renderHook(() => useVotos('invalid-id'))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.error).toContain('404')
    expect(result.current.data).toEqual([])
  })

  it('should handle 500 server error', async () => {
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: false,
        status: 500,
      })
    ) as any

    const { result } = renderHook(() => useVotos('votacao-123'))

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

    const { result } = renderHook(() => useVotos('votacao-123'))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.error).toContain('Network error')
    expect(result.current.data).toEqual([])
  })

  it('should refetch when votacaoId changes', async () => {
    const mockVotos1 = [
      {
        id: '1',
        tipo: 'SIM',
        deputado: {
          id: '1',
          nome: 'João',
          partido: 'PT',
          uf: 'SP',
        },
      },
    ]

    const mockVotos2 = [
      {
        id: '2',
        tipo: 'NAO',
        deputado: {
          id: '2',
          nome: 'Maria',
          partido: 'PSD',
          uf: 'RJ',
        },
      },
    ]

    global.fetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockVotos1),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockVotos2),
      })

    const { result, rerender } = renderHook(
      ({ id }) => useVotos(id),
      { initialProps: { id: 'votacao-1' } }
    )

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.data).toEqual(mockVotos1)

    rerender({ id: 'votacao-2' })

    await waitFor(() => {
      expect(result.current.data).toEqual(mockVotos2)
    })

    expect(global.fetch).toHaveBeenCalledTimes(2)
  })

  it('should have refetch function', async () => {
    const mockVotos = [
      {
        id: '1',
        tipo: 'SIM',
        deputado: {
          id: '1',
          nome: 'João',
          partido: 'PT',
          uf: 'SP',
        },
      },
    ]

    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockVotos),
      })
    ) as any

    const { result } = renderHook(() => useVotos('votacao-123'))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(typeof result.current.refetch).toBe('function')
  })
})
