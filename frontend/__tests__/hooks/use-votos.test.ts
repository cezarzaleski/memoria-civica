import { describe, it, expect } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { server } from '@/mocks/server'
import { useVotos } from '@/lib/hooks/use-votos'

describe('useVotos', () => {
  it('deve retornar estado vazio quando votacaoId não é informado', () => {
    const { result } = renderHook(() => useVotos(null))

    expect(result.current.loading).toBe(false)
    expect(result.current.error).toBeNull()
    expect(result.current.data).toEqual([])
    expect(result.current.pagination).toBeNull()
  })

  it('deve consumir envelope paginado de votos', async () => {
    const { result } = renderHook(() => useVotos(1))

    expect(result.current.loading).toBe(true)

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.error).toBeNull()
    expect(result.current.pagination).toEqual({
      page: 1,
      per_page: 20,
      total: 513,
    })
    expect(result.current.data).toHaveLength(20)
    expect(result.current.data[0]).toMatchObject({
      id: expect.any(Number),
      votacao_id: 1,
      voto: expect.any(String),
    })
    expect((result.current.data[0] as Record<string, unknown>).tipo).toBeUndefined()
  })

  it('deve enviar parâmetros de paginação na query string', async () => {
    let capturedUrl: URL | null = null

    server.use(
      http.get('*/api/v1/votacoes/:votacao_id/votos', ({ request }) => {
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

    const { result } = renderHook(() => useVotos(1, { page: 3, per_page: 7 }))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(capturedUrl?.searchParams.get('page')).toBe('3')
    expect(capturedUrl?.searchParams.get('per_page')).toBe('7')
    expect(result.current.pagination).toEqual({
      page: 3,
      per_page: 7,
      total: 0,
    })
  })

  it('deve expor erro quando votação não existe', async () => {
    const { result } = renderHook(() => useVotos(999999))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.error).toContain('Votação não encontrada')
    expect(result.current.data).toEqual([])
    expect(result.current.pagination).toBeNull()
  })

  it('deve refazer busca ao trocar votacaoId', async () => {
    const { result, rerender } = renderHook(
      ({ id }) => useVotos(id, { per_page: 5 }),
      { initialProps: { id: 1 } }
    )

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
      expect(result.current.data).toHaveLength(5)
    })

    const firstId = result.current.data[0]?.id

    rerender({ id: 2 })

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
      expect(result.current.data).toHaveLength(5)
    })

    expect(result.current.data[0]?.id).not.toBe(firstId)
  })
})
