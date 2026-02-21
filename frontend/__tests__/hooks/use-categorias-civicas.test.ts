import { describe, it, expect } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { server } from '@/mocks/server'
import { useCategoriasCivicas } from '@/lib/hooks/use-categorias-civicas'

describe('useCategoriasCivicas', () => {
  it('deve carregar categorias cívicas em envelope paginado', async () => {
    const { result } = renderHook(() => useCategoriasCivicas())

    expect(result.current.loading).toBe(true)

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.error).toBeNull()
    expect(result.current.data).toHaveLength(8)
    expect(result.current.pagination).toEqual({
      page: 1,
      per_page: 20,
      total: 8,
    })
    expect(result.current.data[0]).toMatchObject({
      id: expect.any(Number),
      codigo: expect.any(String),
      nome: expect.any(String),
    })
  })

  it('deve enviar parâmetros de paginação', async () => {
    let capturedUrl: URL | null = null

    server.use(
      http.get('*/api/v1/categorias-civicas', ({ request }) => {
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

    const { result } = renderHook(() => useCategoriasCivicas({ page: 2, per_page: 3 }))

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

  it('deve lidar com erro de rede', async () => {
    server.use(
      http.get('*/api/v1/categorias-civicas', () => {
        return HttpResponse.error()
      })
    )

    const { result } = renderHook(() => useCategoriasCivicas())

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.error).toBeTruthy()
    expect(result.current.data).toEqual([])
    expect(result.current.pagination).toBeNull()
  })
})
