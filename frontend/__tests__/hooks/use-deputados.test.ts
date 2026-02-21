import { describe, it, expect } from 'vitest'
import { renderHook, waitFor, act } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { server } from '@/mocks/server'
import { useDeputados } from '@/lib/hooks/use-deputados'

describe('useDeputados', () => {
  it('deve carregar deputados com paginação padrão do envelope', async () => {
    const { result } = renderHook(() => useDeputados())

    expect(result.current.data).toEqual([])
    expect(result.current.loading).toBe(true)
    expect(result.current.error).toBeNull()
    expect(result.current.pagination).toBeNull()

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.error).toBeNull()
    expect(result.current.data).toHaveLength(20)
    expect(result.current.pagination).toEqual({
      page: 1,
      per_page: 20,
      total: 513,
    })
    expect(result.current.data[0]).toMatchObject({
      id: expect.any(Number),
      nome: expect.any(String),
      sigla_partido: expect.any(String),
      uf: expect.any(String),
    })
  })

  it('deve enviar filtros e parâmetros de paginação na query string', async () => {
    let capturedUrl: URL | null = null

    server.use(
      http.get('*/api/v1/deputados', ({ request }) => {
        capturedUrl = new URL(request.url)
        return HttpResponse.json({
          data: [],
          pagination: {
            page: Number(capturedUrl.searchParams.get('page') ?? '1'),
            per_page: Number(capturedUrl.searchParams.get('per_page') ?? '20'),
            total: 0,
          },
        })
      })
    )

    const { result } = renderHook(() =>
      useDeputados({
        nome: 'Ana',
        partido: 'PT',
        uf: 'SP',
        page: 2,
        per_page: 5,
      })
    )

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(capturedUrl?.searchParams.get('nome')).toBe('Ana')
    expect(capturedUrl?.searchParams.get('partido')).toBe('PT')
    expect(capturedUrl?.searchParams.get('uf')).toBe('SP')
    expect(capturedUrl?.searchParams.get('page')).toBe('2')
    expect(capturedUrl?.searchParams.get('per_page')).toBe('5')
    expect(result.current.pagination).toEqual({
      page: 2,
      per_page: 5,
      total: 0,
    })
  })

  it('deve expor erro e limpar estado em falha de rede', async () => {
    server.use(
      http.get('*/api/v1/deputados', () => {
        return HttpResponse.error()
      })
    )

    const { result } = renderHook(() => useDeputados())

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.error).toBeTruthy()
    expect(result.current.data).toEqual([])
    expect(result.current.pagination).toBeNull()
  })

  it('deve permitir refetch manual', async () => {
    let calls = 0

    server.use(
      http.get('*/api/v1/deputados', () => {
        calls += 1
        return HttpResponse.json({
          data: [],
          pagination: { page: 1, per_page: 20, total: 0 },
        })
      })
    )

    const { result } = renderHook(() => useDeputados())

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    act(() => {
      result.current.refetch()
    })

    await waitFor(() => {
      expect(calls).toBeGreaterThanOrEqual(2)
    })
  })
})
