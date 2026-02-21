import { describe, it, expect } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { server } from '@/mocks/server'
import { useProposicoes, useProposicaoCategorias } from '@/lib/hooks/use-proposicoes'

describe('useProposicoes', () => {
  it('deve carregar proposições com envelope paginado', async () => {
    const { result } = renderHook(() => useProposicoes())

    expect(result.current.loading).toBe(true)
    expect(result.current.pagination).toBeNull()

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.error).toBeNull()
    expect(result.current.data).toHaveLength(20)
    expect(result.current.pagination).toEqual({
      page: 1,
      per_page: 20,
      total: 80,
    })
    expect(result.current.data[0]).toMatchObject({
      id: expect.any(Number),
      tipo: expect.any(String),
      numero: expect.any(Number),
      ano: expect.any(Number),
    })
  })

  it('deve enviar filtros e paginação na query string', async () => {
    let capturedUrl: URL | null = null

    server.use(
      http.get('*/api/v1/proposicoes', ({ request }) => {
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
      useProposicoes({ tipo: 'PL', ano: 2024, page: 3, per_page: 4 })
    )

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(capturedUrl?.searchParams.get('tipo')).toBe('PL')
    expect(capturedUrl?.searchParams.get('ano')).toBe('2024')
    expect(capturedUrl?.searchParams.get('page')).toBe('3')
    expect(capturedUrl?.searchParams.get('per_page')).toBe('4')
    expect(result.current.pagination).toEqual({
      page: 3,
      per_page: 4,
      total: 0,
    })
  })

  it('deve propagar erro em falha de rede', async () => {
    server.use(
      http.get('*/api/v1/proposicoes', () => {
        return HttpResponse.error()
      })
    )

    const { result } = renderHook(() => useProposicoes())

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.error).toBeTruthy()
    expect(result.current.data).toEqual([])
    expect(result.current.pagination).toBeNull()
  })
})

describe('useProposicaoCategorias', () => {
  it('deve retornar estado vazio quando proposicaoId não é informado', () => {
    const { result } = renderHook(() => useProposicaoCategorias(null))

    expect(result.current.loading).toBe(false)
    expect(result.current.error).toBeNull()
    expect(result.current.data).toEqual([])
    expect(result.current.pagination).toBeNull()
  })

  it('deve carregar categorias associadas à proposição', async () => {
    const { result } = renderHook(() => useProposicaoCategorias(1))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.error).toBeNull()
    expect(result.current.pagination).toEqual({
      page: 1,
      per_page: 20,
      total: 1,
    })
    expect(result.current.data[0]).toMatchObject({
      id: expect.any(Number),
      proposicao_id: 1,
      categoria_id: expect.any(Number),
      origem: expect.any(String),
    })
  })

  it('deve propagar erro quando proposição não existe', async () => {
    const { result } = renderHook(() => useProposicaoCategorias(999999))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.error).toContain('Proposição não encontrada')
    expect(result.current.data).toEqual([])
    expect(result.current.pagination).toBeNull()
  })
})
