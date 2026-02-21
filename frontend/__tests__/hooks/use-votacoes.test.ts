import { describe, it, expect } from 'vitest'
import { act, renderHook, waitFor } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { server } from '@/mocks/server'
import { useVotacoes, useVotacaoProposicoes } from '@/lib/hooks/use-votacoes'

describe('useVotacoes', () => {
  it('deve consumir envelope paginado de votações', async () => {
    const { result } = renderHook(() => useVotacoes())

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
      total: 50,
    })
    expect(result.current.data[0]).toMatchObject({
      id: expect.any(Number),
      data_hora: expect.any(String),
      resultado: expect.any(String),
    })
  })

  it('deve enviar filtros e paginação na query string', async () => {
    let capturedUrl: URL | null = null

    server.use(
      http.get('*/api/v1/votacoes', ({ request }) => {
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
      useVotacoes({
        sigla_orgao: 'PLEN',
        eh_nominal: true,
        page: 2,
        per_page: 7,
      })
    )

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(capturedUrl?.searchParams.get('sigla_orgao')).toBe('PLEN')
    expect(capturedUrl?.searchParams.get('eh_nominal')).toBe('true')
    expect(capturedUrl?.searchParams.get('page')).toBe('2')
    expect(capturedUrl?.searchParams.get('per_page')).toBe('7')
    expect(result.current.pagination).toEqual({
      page: 2,
      per_page: 7,
      total: 0,
    })
  })

  it('deve atualizar dados quando parâmetros mudam', async () => {
    const { result, rerender } = renderHook(
      ({ page }) => useVotacoes({ page, per_page: 5 }),
      { initialProps: { page: 1 } }
    )

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
      expect(result.current.pagination?.page).toBe(1)
    })

    const firstPageFirstId = result.current.data[0]?.id

    rerender({ page: 2 })

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
      expect(result.current.pagination?.page).toBe(2)
    })

    expect(result.current.data[0]?.id).not.toBe(firstPageFirstId)
  })

  it('deve propagar erro HTTP com mensagem do payload', async () => {
    server.use(
      http.get('*/api/v1/votacoes', () => {
        return HttpResponse.json(
          {
            error: {
              code: 'INTERNAL',
              message: 'Falha forçada',
            },
          },
          { status: 500 }
        )
      })
    )

    const { result } = renderHook(() => useVotacoes())

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.error).toContain('Falha forçada')
    expect(result.current.data).toEqual([])
    expect(result.current.pagination).toBeNull()
  })
})

describe('useVotacaoProposicoes', () => {
  it('deve retornar estado vazio quando votacaoId não é informado', () => {
    const { result } = renderHook(() => useVotacaoProposicoes(null))

    expect(result.current.loading).toBe(false)
    expect(result.current.error).toBeNull()
    expect(result.current.data).toEqual([])
    expect(result.current.pagination).toBeNull()
  })

  it('deve consumir envelope paginado de proposições por votação', async () => {
    const { result } = renderHook(() => useVotacaoProposicoes(4))

    expect(result.current.loading).toBe(true)

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.error).toBeNull()
    expect(result.current.data).toHaveLength(2)
    expect(result.current.pagination).toEqual({
      page: 1,
      per_page: 20,
      total: 2,
    })
    expect(result.current.data[0]).toMatchObject({
      id: expect.any(Number),
      votacao_id: 4,
      proposicao_id: expect.any(Number),
      eh_principal: expect.any(Boolean),
    })
  })

  it('deve enviar paginação na query string', async () => {
    let capturedUrl: URL | null = null

    server.use(
      http.get('*/api/v1/votacoes/:id/proposicoes', ({ request }) => {
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

    const { result } = renderHook(() => useVotacaoProposicoes(1, { page: 3, per_page: 7 }))

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
    const { result } = renderHook(() => useVotacaoProposicoes(999999))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.error).toContain('Votação não encontrada')
    expect(result.current.data).toEqual([])
    expect(result.current.pagination).toBeNull()
  })

  it('deve permitir refetch manual', async () => {
    let calls = 0

    server.use(
      http.get('*/api/v1/votacoes/:id/proposicoes', () => {
        calls += 1
        return HttpResponse.json({
          data: [],
          pagination: { page: 1, per_page: 20, total: 0 },
        })
      })
    )

    const { result } = renderHook(() => useVotacaoProposicoes(1))

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
