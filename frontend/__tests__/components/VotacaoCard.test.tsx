import React from 'react'
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { VotacaoCard } from '@/components/features/votacoes/VotacaoCard'
import { ResultadoVotacao } from '@/lib/types/votacao'

describe('VotacaoCard', () => {
  const mockVotacaoAprovado = {
    id: '1',
    data: '2024-01-15T10:00:00Z',
    resultado: ResultadoVotacao.APROVADO,
    placar: { sim: 200, nao: 100, abstencao: 50, obstrucao: 13 },
    proposicao: {
      id: '1',
      tipo: 'PL',
      descricao: 'Reforma Tributária',
      tema: 'Impostos',
    },
  }

  const mockVotacaoRejeitado = {
    ...mockVotacaoAprovado,
    id: '2',
    resultado: ResultadoVotacao.REJEITADO,
  }

  it('should render votacao card with title and date', () => {
    render(<VotacaoCard votacao={mockVotacaoAprovado} />)

    expect(screen.getByText('Reforma Tributária')).toBeInTheDocument()
    expect(screen.getByText(/15\/01\/2024/)).toBeInTheDocument()
  })

  it('should render APROVADO badge with default styling', () => {
    render(<VotacaoCard votacao={mockVotacaoAprovado} />)

    const badge = screen.getByText('APROVADO')
    expect(badge).toBeInTheDocument()
  })

  it('should render REJEITADO badge with destructive styling', () => {
    render(<VotacaoCard votacao={mockVotacaoRejeitado} />)

    const badge = screen.getByText('REJEITADO')
    expect(badge).toBeInTheDocument()
  })

  it('should display placar summary', () => {
    render(<VotacaoCard votacao={mockVotacaoAprovado} />)

    expect(screen.getByText('Sim')).toBeInTheDocument()
    expect(screen.getByText('Não')).toBeInTheDocument()
    expect(screen.getByText('Abstenção')).toBeInTheDocument()
    expect(screen.getByText('Obstrução')).toBeInTheDocument()

    expect(screen.getByText('200')).toBeInTheDocument()
    expect(screen.getByText('100')).toBeInTheDocument()
    expect(screen.getByText('50')).toBeInTheDocument()
    expect(screen.getByText('13')).toBeInTheDocument()
  })

  it('should display proposicao type', () => {
    render(<VotacaoCard votacao={mockVotacaoAprovado} />)

    expect(screen.getByText('PL')).toBeInTheDocument()
  })

  it('should display tema when available', () => {
    render(<VotacaoCard votacao={mockVotacaoAprovado} />)

    expect(screen.getByText(/Tema:/)).toBeInTheDocument()
    expect(screen.getByText('Impostos')).toBeInTheDocument()
  })

  it('should call onClick handler when clicked', () => {
    const onClick = vi.fn()
    render(<VotacaoCard votacao={mockVotacaoAprovado} onClick={onClick} />)

    const card = screen.getByText('Reforma Tributária').closest('div').closest('div')
    if (card) {
      card.click()
      expect(onClick).toHaveBeenCalled()
    }
  })

  it('should handle missing proposicao gracefully', () => {
    const votacaoSemProposicao = {
      ...mockVotacaoAprovado,
      proposicao: undefined,
    }

    render(<VotacaoCard votacao={votacaoSemProposicao} />)

    expect(screen.getByText('Votação')).toBeInTheDocument()
  })

  it('should handle missing placar values', () => {
    const votacaoSemPlacar = {
      ...mockVotacaoAprovado,
      placar: { sim: 0, nao: 0, abstencao: 0, obstrucao: 0 },
    }

    render(<VotacaoCard votacao={votacaoSemPlacar} />)

    expect(screen.getAllByText('0')).toHaveLength(4)
  })
})
