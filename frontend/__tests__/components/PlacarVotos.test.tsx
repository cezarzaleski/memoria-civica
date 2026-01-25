import React from 'react'
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { PlacarVotos } from '@/components/features/votacoes/PlacarVotos'

describe('PlacarVotos', () => {
  const mockPlacar = {
    sim: 200,
    nao: 100,
    abstencao: 50,
    obstrucao: 13,
  }

  it('should render placar with title', () => {
    render(<PlacarVotos placar={mockPlacar} />)

    expect(screen.getByText('Resultado da Votação')).toBeInTheDocument()
  })

  it('should render custom title when provided', () => {
    render(<PlacarVotos placar={mockPlacar} title="Meu Placar" />)

    expect(screen.getByText('Meu Placar')).toBeInTheDocument()
  })

  it('should display total votes', () => {
    render(<PlacarVotos placar={mockPlacar} />)

    expect(screen.getByText(/Total: 363 votos/)).toBeInTheDocument()
  })

  it('should display all vote labels', () => {
    render(<PlacarVotos placar={mockPlacar} />)

    expect(screen.getByText('Sim')).toBeInTheDocument()
    expect(screen.getByText('Não')).toBeInTheDocument()
    expect(screen.getByText('Abstenção')).toBeInTheDocument()
    expect(screen.getByText('Obstrução')).toBeInTheDocument()
  })

  it('should display vote counts and percentages', () => {
    render(<PlacarVotos placar={mockPlacar} />)

    // Percentages should be approximately:
    // SIM: 200/363 = ~55%
    // NÃO: 100/363 = ~28%
    // ABSTENÇÃO: 50/363 = ~14%
    // OBSTRUÇÃO: 13/363 = ~4%
    expect(screen.getByText(/200 \(55%\)/)).toBeInTheDocument()
    expect(screen.getByText(/100 \(28%\)/)).toBeInTheDocument()
    expect(screen.getByText(/50 \(14%\)/)).toBeInTheDocument()
    expect(screen.getByText(/13 \(4%\)/)).toBeInTheDocument()
  })

  it('should calculate percentages correctly', () => {
    const placarSimples = {
      sim: 50,
      nao: 50,
      abstencao: 0,
      obstrucao: 0,
    }

    render(<PlacarVotos placar={placarSimples} />)

    // Each should be exactly 50%
    const percentages = screen.getAllByText(/50%/)
    expect(percentages.length).toBeGreaterThan(0)
  })

  it('should handle zero total votes', () => {
    const placarZero = {
      sim: 0,
      nao: 0,
      abstencao: 0,
      obstrucao: 0,
    }

    render(<PlacarVotos placar={placarZero} />)

    expect(screen.getByText(/Total: 0 votos/)).toBeInTheDocument()
    expect(screen.getAllByText(/\(0%\)/)).toHaveLength(4)
  })

  it('should handle missing vote counts', () => {
    const placarIncompleto = {
      sim: 100,
      nao: undefined,
      abstencao: undefined,
      obstrucao: undefined,
    }

    render(<PlacarVotos placar={placarIncompleto} />)

    expect(screen.getByText(/Total: 100 votos/)).toBeInTheDocument()
    expect(screen.getByText(/100 \(100%\)/)).toBeInTheDocument()
  })

  it('should render visual bars for each vote type', () => {
    render(<PlacarVotos placar={mockPlacar} />)

    // Check that visual bars are rendered (they have specific classes)
    const bars = screen.getByText('Sim').closest('div').parentElement.querySelectorAll('[style*="width"]')
    expect(bars.length).toBeGreaterThan(0)
  })

  it('should display labels in correct order', () => {
    render(<PlacarVotos placar={mockPlacar} />)

    const labels = screen.getAllByText(/Sim|Não|Abstenção|Obstrução/)
    expect(labels[0]).toHaveTextContent('Sim')
    expect(labels[1]).toHaveTextContent('Não')
    expect(labels[2]).toHaveTextContent('Abstenção')
    expect(labels[3]).toHaveTextContent('Obstrução')
  })
})
