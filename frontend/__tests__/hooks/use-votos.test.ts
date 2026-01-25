import { renderHook, waitFor } from '@testing-library/react'
import { server } from '@/mocks/server'
import { http, HttpResponse } from 'msw'
import { useVotos } from '@/lib/hooks/use-votos'
import { generateVotos } from '@/mocks/data/votos'

describe('useVotos', () => {
  it('should return empty data when votacaoId is null', async () => {
    const { result } = renderHook(() => useVotos(null))

    expect(result.current.data).toEqual([])
    expect(result.current.loading).toBe(false)
    expect(result.current.error).toBeNull()
  })

  it('should fetch votos for given votacaoId', async () => {
    const mockVotos = generateVotos(5, '1')

    const { result } = renderHook(() => useVotos('1'))

    expect(result.current.loading).toBe(true)

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.data).toEqual(mockVotos)
    expect(result.current.error).toBeNull()
  })

  it('should handle error when fetching votos', async () => {
    server.use(
      http.get('/api/v1/votacoes/:id/votos', () => {
        return HttpResponse.error()
      })
    )

    const { result } = renderHook(() => useVotos('1'))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.error).toBeTruthy()
    expect(result.current.data).toEqual([])
  })

  it('should refetch when votacaoId changes', async () => {
    const { result, rerender } = renderHook(
      ({ id }) => useVotos(id),
      { initialProps: { id: '1' } }
    )

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.data.length).toBeGreaterThan(0)

    // Mudar para um ID diferente
    rerender({ id: '2' })

    await waitFor(() => {
      expect(result.current.data.length).toBeGreaterThan(0)
    })
  })

  it('should have refetch function', async () => {
    const { result } = renderHook(() => useVotos('1'))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(typeof result.current.refetch).toBe('function')
  })
})
