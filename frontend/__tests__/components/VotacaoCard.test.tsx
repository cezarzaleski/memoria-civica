import React from 'react'
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { VotacaoCard } from '@/components/features/votacoes/VotacaoCard'
import { ResultadoVotacao, Votacao } from '@/lib/types/votacao'

describe('VotacaoCard', () => {
  const mockVotacaoAprovado: Votacao = {
    id: 1,
    proposicao_id: 1,
    data_hora: '2024-01-15T10:00:00Z',
    resultado: ResultadoVotacao.APROVADO,
    placar: { votos_sim: 200, votos_nao: 100, votos_outros: 63 },
    proposicao: {
      id: 1,
      tipo: 'PL',
      numero: 1234,
      ano: 2024,
      ementa: 'Reforma Tributária: Implementação de novo sistema de impostos',
      data_apresentacao: '2024-01-01T00:00:00Z',
    },
  }

  const mockVotacaoRejeitado: Votacao = {
    ...mockVotacaoAprovado,
    id: 2,
    resultado: ResultadoVotacao.REJEITADO,
  }

  it('deve renderizar identificador da proposição e data_hora formatada', () => {
    render(<VotacaoCard votacao={mockVotacaoAprovado} />)

    expect(screen.getByText('PL 1234/2024')).toBeInTheDocument()
    expect(screen.getByText(/15\/01\/2024/)).toBeInTheDocument()
  })

  it('deve renderizar badge de aprovado para resultado aprovado', () => {
    render(<VotacaoCard votacao={mockVotacaoAprovado} />)

    expect(screen.getByText('Aprovado')).toBeInTheDocument()
  })

  it('deve renderizar badge de rejeitado para resultado rejeitado', () => {
    render(<VotacaoCard votacao={mockVotacaoRejeitado} />)

    expect(screen.getByText('Rejeitado')).toBeInTheDocument()
  })

  it('deve exibir resumo do placar canônico', () => {
    render(<VotacaoCard votacao={mockVotacaoAprovado} />)

    expect(screen.getByText('Sim')).toBeInTheDocument()
    expect(screen.getByText('Não')).toBeInTheDocument()
    expect(screen.getByText('Outros')).toBeInTheDocument()

    expect(screen.getByText('200')).toBeInTheDocument()
    expect(screen.getByText('100')).toBeInTheDocument()
    expect(screen.getByText('63')).toBeInTheDocument()
  })

  it('deve exibir ementa truncada quando necessário', () => {
    render(<VotacaoCard votacao={mockVotacaoAprovado} />)

    expect(screen.getByText(/Reforma Tributária/)).toBeInTheDocument()
  })

  it('deve tratar ausência de proposição sem quebrar renderização', () => {
    const votacaoSemProposicao: Votacao = {
      ...mockVotacaoAprovado,
      proposicao: undefined,
    }

    render(<VotacaoCard votacao={votacaoSemProposicao} />)

    expect(screen.getByText('Votação')).toBeInTheDocument()
  })

  it('deve tratar placar zerado', () => {
    const votacaoSemPlacar: Votacao = {
      ...mockVotacaoAprovado,
      placar: { votos_sim: 0, votos_nao: 0, votos_outros: 0 },
    }

    render(<VotacaoCard votacao={votacaoSemPlacar} />)

    expect(screen.getAllByText('0')).toHaveLength(3)
  })
})
