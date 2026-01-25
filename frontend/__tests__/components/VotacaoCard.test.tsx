import React from 'react'
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { VotacaoCard } from '@/components/features/votacoes/VotacaoCard'
import { ResultadoVotacao } from '@/lib/types/votacao'

describe('VotacaoCard', () => {
  const mockVotacaoAprovado = {
    id: '1',
    proposicao_id: 1,
    data: '2024-01-15T10:00:00Z',
    resultado: ResultadoVotacao.APROVADO,
    placar: { sim: 200, nao: 100, abstencao: 50, obstrucao: 13 },
    proposicao: {
      id: 1,
      tipo: 'PL',
      numero: 1234,
      ano: 2024,
      ementa: 'Reforma Tributária: Implementação de novo sistema de impostos',
    },
  }

  const mockVotacaoRejeitado = {
    ...mockVotacaoAprovado,
    id: '2',
    resultado: ResultadoVotacao.REJEITADO,
  }

  it('should render votacao card with proposicao identifier and date', () => {
    render(<VotacaoCard votacao={mockVotacaoAprovado} />)

    expect(screen.getByText('PL 1234/2024')).toBeInTheDocument()
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

  it('should display ementa (proposicao title) truncated if too long', () => {
    render(<VotacaoCard votacao={mockVotacaoAprovado} />)

    expect(screen.getByText(/Reforma Tributária/)).toBeInTheDocument()
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
