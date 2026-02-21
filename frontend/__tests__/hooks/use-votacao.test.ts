import { describe, it, expect, vi } from 'vitest'
import { renderHook, waitFor, act } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { server } from '@/mocks/server'
import { useVotacao } from '@/lib/hooks/use-votacao'

describe('useVotacao', () => {
  it('deve buscar uma votação individual em formato SingleResponse', async () => {
    const { result } = renderHook(() => useVotacao(1))

    expect(result.current.loading).toBe(true)
    expect(result.current.data).toBeNull()

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.error).toBeNull()
    expect(result.current.data).toMatchObject({
      id: 1,
      data_hora: expect.any(String),
      resultado: expect.any(String),
      placar: expect.objectContaining({
        votos_sim: expect.any(Number),
        votos_nao: expect.any(Number),
        votos_outros: expect.any(Number),
      }),
    })
  })

  it('deve lidar com 404 retornando mensagem amigável', async () => {
    const { result } = renderHook(() => useVotacao(999999))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.data).toBeNull()
    expect(result.current.error).toBe('Votação não encontrada')
  })

  it('não deve buscar quando id é nulo', () => {
    const fetchSpy = vi.spyOn(global, 'fetch')

    const { result } = renderHook(() => useVotacao(null))

    expect(result.current.loading).toBe(false)
    expect(result.current.data).toBeNull()
    expect(result.current.error).toBeNull()
    expect(fetchSpy).not.toHaveBeenCalled()

    fetchSpy.mockRestore()
  })

  it('deve expor erro em falha de rede', async () => {
    server.use(
      http.get('*/api/v1/votacoes/:id', () => {
        return HttpResponse.error()
      })
    )

    const { result } = renderHook(() => useVotacao(1))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.data).toBeNull()
    expect(result.current.error).toBeTruthy()
  })

  it('deve permitir refetch manual', async () => {
    const { result } = renderHook(() => useVotacao(1))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    act(() => {
      result.current.refetch()
    })

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
      expect(result.current.data?.id).toBe(1)
    })
  })
})
