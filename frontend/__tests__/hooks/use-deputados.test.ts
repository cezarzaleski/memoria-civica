import { describe, it, expect, beforeEach, vi } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { useDeputados } from '@/lib/hooks/use-deputados'

describe('useDeputados', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should return empty data and loading true initially', () => {
    const { result } = renderHook(() => useDeputados())

    expect(result.current.data).toEqual([])
    expect(result.current.loading).toBe(true)
    expect(result.current.error).toBeNull()
  })

  it('should fetch all deputados without filters', async () => {
    const mockDeputados = [
      {
        id: '1',
        nome: 'João Silva',
        partido: 'PT',
        uf: 'SP',
        foto_url: 'http://example.com/foto1.jpg',
      },
      {
        id: '2',
        nome: 'Maria Santos',
        partido: 'PSD',
        uf: 'RJ',
        foto_url: 'http://example.com/foto2.jpg',
      },
    ]

    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockDeputados),
      })
    ) as any

    const { result } = renderHook(() => useDeputados())

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.data).toEqual(mockDeputados)
    expect(result.current.error).toBeNull()
  })

  it('should filter by nome', async () => {
    const mockDeputados = [
      {
        id: '1',
        nome: 'João Silva',
        partido: 'PT',
        uf: 'SP',
        foto_url: 'http://example.com/foto1.jpg',
      },
    ]

    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockDeputados),
      })
    ) as any

    const { result } = renderHook(() => useDeputados({ nome: 'João' }))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('nome=Jo')
    )
    expect(result.current.data).toEqual(mockDeputados)
  })

  it('should filter by partido', async () => {
    const mockDeputados = [
      {
        id: '1',
        nome: 'João Silva',
        partido: 'PT',
        uf: 'SP',
        foto_url: 'http://example.com/foto1.jpg',
      },
    ]

    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockDeputados),
      })
    ) as any

    const { result } = renderHook(() => useDeputados({ partido: 'PT' }))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('partido=PT')
    )
  })

  it('should filter by uf', async () => {
    const mockDeputados = [
      {
        id: '1',
        nome: 'João Silva',
        partido: 'PT',
        uf: 'SP',
        foto_url: 'http://example.com/foto1.jpg',
      },
    ]

    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockDeputados),
      })
    ) as any

    const { result } = renderHook(() => useDeputados({ uf: 'SP' }))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('uf=SP')
    )
  })

  it('should apply multiple filters', async () => {
    const mockDeputados = []

    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockDeputados),
      })
    ) as any

    const { result } = renderHook(() =>
      useDeputados({ nome: 'João', partido: 'PT', uf: 'SP' })
    )

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    const callUrl = (global.fetch as any).mock.calls[0][0]
    expect(callUrl).toContain('nome=Jo')
    expect(callUrl).toContain('partido=PT')
    expect(callUrl).toContain('uf=SP')
  })

  it('should handle fetch errors', async () => {
    global.fetch = vi.fn(() =>
      Promise.reject(new Error('Network error'))
    ) as any

    const { result } = renderHook(() => useDeputados())

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.error).toBeTruthy()
    expect(result.current.data).toEqual([])
  })
})
