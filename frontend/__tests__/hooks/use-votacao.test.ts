import { renderHook, waitFor } from '@testing-library/react'
import { server } from '@/mocks/server'
import { http, HttpResponse } from 'msw'
import { useVotacao } from '@/lib/hooks/use-votacao'
import { generateVotacoes } from '@/mocks/data/votacoes'

describe('useVotacao', () => {
  const mockVotacoes = generateVotacoes(5)
  const mockVotacao = mockVotacoes[0]

  it('should fetch single votacao successfully', async () => {
    const { result } = renderHook(() => useVotacao(mockVotacao.id))

    expect(result.current.loading).toBe(true)
    expect(result.current.data).toBe(null)
    expect(result.current.error).toBe(null)

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.data).toEqual(mockVotacao)
    expect(result.current.error).toBe(null)
  })

  it('should handle 404 error for non-existent votacao', async () => {
    server.use(
      http.get('/api/v1/votacoes/:id', () => {
        return new HttpResponse(null, { status: 404 })
      })
    )

    const { result } = renderHook(() => useVotacao('non-existent-id'))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.data).toBe(null)
    expect(result.current.error).toBe('Votação não encontrada')
  })

  it('should handle network errors', async () => {
    server.use(
      http.get('/api/v1/votacoes/:id', () => {
        return HttpResponse.error()
      })
    )

    const { result } = renderHook(() => useVotacao(mockVotacao.id))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.data).toBe(null)
    expect(result.current.error).toBeTruthy()
  })

  it('should not fetch when id is null', () => {
    const { result } = renderHook(() => useVotacao(null))

    expect(result.current.loading).toBe(false)
    expect(result.current.data).toBe(null)
    expect(result.current.error).toBe(null)
  })

  it('should refetch when calling refetch()', async () => {
    const { result } = renderHook(() => useVotacao(mockVotacao.id))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.data).toEqual(mockVotacao)

    // Chamar refetch
    result.current.refetch()

    // Deve estar carregando novamente
    await waitFor(() => {
      expect(result.current.data).toEqual(mockVotacao)
    })
  })

  it('should update when id prop changes', async () => {
    const votacao1 = mockVotacoes[0]
    const votacao2 = mockVotacoes[1]

    const { result, rerender } = renderHook(
      ({ id }) => useVotacao(id),
      { initialProps: { id: votacao1.id } }
    )

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.data?.id).toBe(votacao1.id)

    // Mudar o ID
    rerender({ id: votacao2.id })

    await waitFor(() => {
      expect(result.current.data?.id).toBe(votacao2.id)
    })
  })
})
