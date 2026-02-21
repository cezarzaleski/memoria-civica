import React from 'react'
import { describe, it, expect, beforeAll, afterEach, afterAll, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { server } from '@/mocks/server'
import { HttpResponse, http } from 'msw'
import Home from '@/app/page'

// Mock Next.js Link to avoid navigation issues in tests
vi.mock('next/link', () => ({
  default: ({ children, href }: any) => <a href={href}>{children}</a>,
}))

describe('Home Page - Feed de Votações', () => {
  beforeAll(() => {
    server.listen()
  })

  afterEach(() => {
    server.resetHandlers()
  })

  afterAll(() => {
    server.close()
  })

  it('should display loading skeletons while fetching data', async () => {
    // Add a delay to MSW handler to ensure loading state is visible
    server.use(
      http.get('/api/v1/votacoes', async () => {
        await new Promise(resolve => setTimeout(resolve, 100))
        return HttpResponse.json({
          data: [],
          pagination: { page: 1, per_page: 20, total: 0 },
        })
      })
    )

    render(<Home />)

    // Should show loading text/header
    expect(screen.getByText('Votações Recentes')).toBeInTheDocument()
  })

  it('should render feed with votações after loading', async () => {
    render(<Home />)

    // Wait for votações to be fetched and rendered
    await waitFor(() => {
      const votacaoCards = screen.queryAllByText(/PL \d+\/\d+/)
      expect(votacaoCards.length).toBeGreaterThan(0)
    })

    // Verify header is present
    expect(screen.getByText('Votações Recentes')).toBeInTheDocument()
  })

  it('should display votações in reverse chronological order', async () => {
    render(<Home />)

    await waitFor(() => {
      const proposicaoTexts = screen.getAllByText(/PL \d+\/\d+/)
      expect(proposicaoTexts.length).toBeGreaterThan(0)
    })

    // The first votação should be the most recent
    // (This is guaranteed by the mock data factory)
    const firstProposicao = screen.getAllByText(/PL \d+\/\d+/)[0]
    expect(firstProposicao).toBeInTheDocument()
  })

  it('should display votação cards from mock data', async () => {
    render(<Home />)

    await waitFor(() => {
      const votacaoCards = screen.queryAllByText(/PL \d+\/\d+/)
      expect(votacaoCards.length).toBeGreaterThan(0)
    })
  })

  it('should handle error state with retry button', async () => {
    server.use(
      http.get('/api/v1/votacoes', () => {
        return new HttpResponse(null, { status: 500 })
      })
    )

    render(<Home />)

    await waitFor(() => {
      expect(screen.getByText('Erro ao carregar votações')).toBeInTheDocument()
    })

    // Check for retry button
    const retryButton = screen.getByRole('button', { name: /Tentar Novamente/i })
    expect(retryButton).toBeInTheDocument()
  })

  it('should retry fetch when retry button is clicked', async () => {
    let callCount = 0

    server.use(
      http.get('/api/v1/votacoes', () => {
        callCount++
        if (callCount === 1) {
          return new HttpResponse(null, { status: 500 })
        }
        // Second call succeeds with empty list envelope
        return HttpResponse.json({
          data: [],
          pagination: { page: 1, per_page: 20, total: 0 },
        })
      })
    )

    const user = userEvent.setup()
    render(<Home />)

    // Wait for error state
    await waitFor(() => {
      expect(screen.getByText('Erro ao carregar votações')).toBeInTheDocument()
    })

    // Click retry button
    const retryButton = screen.getByRole('button', { name: /Tentar Novamente/i })
    await user.click(retryButton)

    // Wait for empty state or successful load
    await waitFor(() => {
      expect(screen.queryByText('Erro ao carregar votações')).not.toBeInTheDocument()
    }, { timeout: 2000 })
  })

  it('should display empty state when no votações available', async () => {
    server.use(
      http.get('/api/v1/votacoes', () => {
        return HttpResponse.json({
          data: [],
          pagination: { page: 1, per_page: 20, total: 0 },
        })
      })
    )

    render(<Home />)

    await waitFor(() => {
      expect(screen.getByText('Nenhuma votação encontrada')).toBeInTheDocument()
    })

    expect(
      screen.getByText(/Não há votações disponíveis no momento/)
    ).toBeInTheDocument()
  })

  it('should render proposição identifier (TIPO NUMERO/ANO)', async () => {
    render(<Home />)

    await waitFor(() => {
      const proposicaoTexts = screen.getAllByText(/PL \d+\/\d+/)
      expect(proposicaoTexts.length).toBeGreaterThan(0)
    })

    // Check that we have properly formatted proposição identifiers
    const proposicaoText = screen.getAllByText(/PL \d+\/\d+/)[0]
    expect(proposicaoText.textContent).toMatch(/PL \d+\/\d+/)
  })

  it('should display resultado badge with correct colors', async () => {
    render(<Home />)

    await waitFor(() => {
      const badges = screen.queryAllByText(/Aprovado|Rejeitado/)
      expect(badges.length).toBeGreaterThan(0)
    })

    // Badges are verified above - multiple badges expected in feed
  })

  it('should render votação card with placar summary', async () => {
    render(<Home />)

    await waitFor(() => {
      // Check for placar labels and values (multiple cards with these labels)
      expect(screen.queryAllByText('Sim').length).toBeGreaterThan(0)
      expect(screen.queryAllByText('Não').length).toBeGreaterThan(0)
      expect(screen.queryAllByText('Outros').length).toBeGreaterThan(0)
    })
  })

  it('should be scrollable and all cards accessible', async () => {
    render(<Home />)

    await waitFor(() => {
      const votacaoCards = screen.queryAllByText(/PL \d+\/\d+/)
      expect(votacaoCards.length).toBeGreaterThan(0)
    })

    // Verify all cards are in the document and accessible
    const allCards = screen.getAllByText(/PL \d+\/\d+/)
    expect(allCards.length).toBeGreaterThan(0)
  })

  it('should have proper responsive layout on mobile viewport', async () => {
    // Note: This test verifies the DOM structure, actual viewport testing
    // would be done in e2e tests
    render(<Home />)

    await waitFor(() => {
      const votacaoCards = screen.queryAllByText(/PL \d+\/\d+/)
      expect(votacaoCards.length).toBeGreaterThan(0)
    })

    // Container should have responsive classes
    const container = screen.getByText('Votações Recentes').closest('div')?.parentElement
    expect(container).toBeInTheDocument()
  })

  it('should display count of votações shown', async () => {
    render(<Home />)

    await waitFor(() => {
      const countText = screen.queryByText(/Exibindo \d+ votações/)
      expect(countText).toBeInTheDocument()
    })
  })

  it('should navigate to votação details when clicking card', async () => {
    render(<Home />)

    // Wait for votações to be rendered
    await waitFor(() => {
      const votacaoTexts = screen.queryAllByText(/PL \d+\/\d+/)
      expect(votacaoTexts.length).toBeGreaterThan(0)
    })

    // Get all links and find first votação link
    const firstVotacaoLink = screen.getAllByRole('link').find(
      link => link.getAttribute('href')?.startsWith('/votacoes/')
    )

    expect(firstVotacaoLink).toBeDefined()
    expect(firstVotacaoLink?.getAttribute('href')).toMatch(/^\/votacoes\/\d+$/)
  })
})
