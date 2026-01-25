import React from 'react'
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { VotacaoDetalhes } from '@/components/features/votacoes/VotacaoDetalhes'

describe('VotacaoDetalhes', () => {
  const mockVotacao = {
    id: '1',
    data: '2024-01-15T10:00:00Z',
    resultado: 'APROVADO',
    placar: { sim: 200, nao: 100, abstencao: 50, obstrucao: 13 },
    proposicao: {
      id: '1',
      tipo: 'PL',
      descricao: 'Reforma Tributária',
      tema: 'Impostos',
    },
  }

  it('should render votacao title', () => {
    render(<VotacaoDetalhes votacao={mockVotacao} />)

    expect(screen.getByText('Reforma Tributária')).toBeInTheDocument()
  })

  it('should render votacao date', () => {
    render(<VotacaoDetalhes votacao={mockVotacao} />)

    expect(screen.getByText(/15\/01\/2024/)).toBeInTheDocument()
  })

  it('should render proposicao type', () => {
    render(<VotacaoDetalhes votacao={mockVotacao} />)

    expect(screen.getByText('Tipo de Proposição')).toBeInTheDocument()
    expect(screen.getByText('PL')).toBeInTheDocument()
  })

  it('should render tema', () => {
    render(<VotacaoDetalhes votacao={mockVotacao} />)

    expect(screen.getByText('Tema')).toBeInTheDocument()
    expect(screen.getByText('Impostos')).toBeInTheDocument()
  })

  it('should render resultado badge', () => {
    render(<VotacaoDetalhes votacao={mockVotacao} />)

    expect(screen.getByText('Resultado')).toBeInTheDocument()
    expect(screen.getByText('APROVADO')).toBeInTheDocument()
  })

  it('should display placar summary', () => {
    render(<VotacaoDetalhes votacao={mockVotacao} />)

    expect(screen.getByText(/Resultado da Votação/)).toBeInTheDocument()
    expect(screen.getByText('Sim')).toBeInTheDocument()
    expect(screen.getByText('Não')).toBeInTheDocument()
  })

  it('should show loading skeleton when loading is true', () => {
    const { container } = render(
      <VotacaoDetalhes votacao={mockVotacao} loading={true} />
    )

    const skeletons = container.querySelectorAll('.animate-pulse')
    expect(skeletons.length).toBeGreaterThan(0)
  })

  it('should display back button when onBack is provided', () => {
    const onBack = vi.fn()
    render(<VotacaoDetalhes votacao={mockVotacao} onBack={onBack} />)

    expect(screen.getByText('← Voltar')).toBeInTheDocument()
  })

  it('should call onBack when back button is clicked', () => {
    const onBack = vi.fn()
    render(<VotacaoDetalhes votacao={mockVotacao} onBack={onBack} />)

    const backButton = screen.getByText('← Voltar')
    backButton.click()

    expect(onBack).toHaveBeenCalled()
  })

  it('should not display back button when onBack is not provided', () => {
    render(<VotacaoDetalhes votacao={mockVotacao} />)

    expect(screen.queryByText('← Voltar')).not.toBeInTheDocument()
  })

  it('should display LLM explanation section when provided', () => {
    const explanation = 'Esta é uma votação sobre reforma tributária...'
    render(
      <VotacaoDetalhes
        votacao={mockVotacao}
        llmExplanation={explanation}
      />
    )

    expect(screen.getByText('Explicação (IA)')).toBeInTheDocument()
    expect(screen.getByText(explanation)).toBeInTheDocument()
  })

  it('should show loading skeleton for LLM explanation', () => {
    const { container } = render(
      <VotacaoDetalhes
        votacao={mockVotacao}
        llmExplanation=""
        llmLoading={true}
      />
    )

    expect(screen.getByText('Explicação (IA)')).toBeInTheDocument()

    const skeletons = container.querySelectorAll('.animate-pulse')
    expect(skeletons.length).toBeGreaterThan(0)
  })

  it('should not display LLM explanation section when not provided and not loading', () => {
    render(<VotacaoDetalhes votacao={mockVotacao} />)

    expect(screen.queryByText('Explicação (IA)')).not.toBeInTheDocument()
  })

  it('should handle votacao without proposicao', () => {
    const votacaoSemProposicao = {
      ...mockVotacao,
      proposicao: undefined,
    }

    render(<VotacaoDetalhes votacao={votacaoSemProposicao} />)

    expect(screen.getByText('Votação')).toBeInTheDocument()
  })

  it('should display all placar values', () => {
    render(<VotacaoDetalhes votacao={mockVotacao} />)

    expect(screen.getByText('200')).toBeInTheDocument()
    expect(screen.getByText('100')).toBeInTheDocument()
    expect(screen.getByText('50')).toBeInTheDocument()
    expect(screen.getByText('13')).toBeInTheDocument()
  })
})
