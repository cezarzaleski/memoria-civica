import { renderHook, waitFor } from '@testing-library/react'
import { server } from '@/mocks/server'
import { http, HttpResponse } from 'msw'
import { useVotacao } from '@/lib/hooks/use-votacao'

describe('useVotacao', () => {
  // Use a known votacao ID that MSW will generate
  const testVotacaoId = 'votacao-1'

  it('should fetch single votacao successfully', async () => {
    const { result } = renderHook(() => useVotacao(testVotacaoId))

    expect(result.current.loading).toBe(true)
    expect(result.current.data).toBe(null)
    expect(result.current.error).toBe(null)

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    // Verify structure instead of exact equality
    expect(result.current.data).not.toBe(null)
    expect(result.current.data?.id).toBe(testVotacaoId)
    expect(result.current.data?.placar).toBeDefined()
    expect(result.current.data?.resultado).toBeDefined()
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

    const { result } = renderHook(() => useVotacao(testVotacaoId))

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
    const { result } = renderHook(() => useVotacao(testVotacaoId))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.data?.id).toBe(testVotacaoId)

    // Chamar refetch
    result.current.refetch()

    // Deve retornar os mesmos dados após refetch
    await waitFor(() => {
      expect(result.current.data?.id).toBe(testVotacaoId)
    })
  })

  it('should update when id prop changes', async () => {
    const votacaoId1 = 'votacao-1'
    const votacaoId2 = 'votacao-2'

    const { result, rerender } = renderHook(
      ({ id }) => useVotacao(id),
      { initialProps: { id: votacaoId1 } }
    )

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.data?.id).toBe(votacaoId1)

    // Mudar o ID
    rerender({ id: votacaoId2 })

    await waitFor(() => {
      expect(result.current.data?.id).toBe(votacaoId2)
    })
  })
})
