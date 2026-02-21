import { describe, it, expect } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { server } from '@/mocks/server'
import { useOrientacoes } from '@/lib/hooks/use-orientacoes'

describe('useOrientacoes', () => {
  it('deve retornar estado vazio quando votacaoId não é informado', () => {
    const { result } = renderHook(() => useOrientacoes(null))

    expect(result.current.loading).toBe(false)
    expect(result.current.error).toBeNull()
    expect(result.current.data).toEqual([])
    expect(result.current.pagination).toBeNull()
  })

  it('deve carregar orientações por votação com envelope paginado', async () => {
    const { result } = renderHook(() => useOrientacoes(1))

    expect(result.current.loading).toBe(true)

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.error).toBeNull()
    expect(result.current.data).toHaveLength(10)
    expect(result.current.pagination).toEqual({
      page: 1,
      per_page: 20,
      total: 10,
    })
    expect(result.current.data[0]).toMatchObject({
      id: expect.any(Number),
      votacao_id: 1,
      sigla_bancada: expect.any(String),
      orientacao: expect.any(String),
    })
  })

  it('deve enviar paginação na query string', async () => {
    let capturedUrl: URL | null = null

    server.use(
      http.get('*/api/v1/votacoes/:votacao_id/orientacoes', ({ request }) => {
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

    const { result } = renderHook(() => useOrientacoes(1, { page: 2, per_page: 3 }))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(capturedUrl?.searchParams.get('page')).toBe('2')
    expect(capturedUrl?.searchParams.get('per_page')).toBe('3')
    expect(result.current.pagination).toEqual({
      page: 2,
      per_page: 3,
      total: 0,
    })
  })

  it('deve expor erro quando votação não existe', async () => {
    const { result } = renderHook(() => useOrientacoes(999999))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.error).toContain('Votação não encontrada')
    expect(result.current.data).toEqual([])
    expect(result.current.pagination).toBeNull()
  })
})
