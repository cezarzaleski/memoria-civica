import React from 'react'
import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { server } from '@/mocks/server'
import VotacaoPage from '@/app/votacoes/[id]/page'

let mockVotacaoId = '1'

vi.mock('next/navigation', () => ({
  useParams: () => ({ id: mockVotacaoId }),
}))

vi.mock('next/link', () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => <a href={href}>{children}</a>,
}))

describe('VotacaoPage - Detalhe da Votação', () => {
  it('deve renderizar detalhes, placar, votos, orientações e categorias cívicas', async () => {
    mockVotacaoId = '1'

    render(<VotacaoPage />)

    await waitFor(() => {
      expect(screen.getByText(/PL \d+\/\d+/)).toBeInTheDocument()
    })

    expect(screen.getByText('Resultado da Votação')).toBeInTheDocument()
    expect(screen.getByText(/Votos \(/)).toBeInTheDocument()
    expect(screen.getByText(/Orientações de Bancada \(/)).toBeInTheDocument()
    expect(screen.getByText(/Categorias Cívicas/)).toBeInTheDocument()
  })

  it('deve exibir estado de erro quando votação não existe', async () => {
    mockVotacaoId = '999999'

    render(<VotacaoPage />)

    await waitFor(() => {
      expect(screen.getByText('Votação não encontrada')).toBeInTheDocument()
    })
  })

  it('deve exibir erro de categorias quando endpoint falha', async () => {
    mockVotacaoId = '1'

    server.use(
      http.get('*/api/v1/proposicoes/:id/categorias', () =>
        HttpResponse.json(
          {
            error: {
              code: 'INTERNAL_SERVER_ERROR',
              message: 'Falha ao carregar categorias da proposição',
            },
          },
          { status: 500 }
        )
      )
    )

    render(<VotacaoPage />)

    await waitFor(() => {
      expect(
        screen.getByText('Falha ao carregar categorias da proposição')
      ).toBeInTheDocument()
    })
  })
})
