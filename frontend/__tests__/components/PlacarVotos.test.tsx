import { render, screen } from '@testing-library/react'
import { PlacarVotos } from '@/components/features/votacoes/PlacarVotos'
import { Placar } from '@/lib/types/votacao'

describe('PlacarVotos', () => {
  const mockPlacar: Placar = {
    sim: 300,
    nao: 150,
    abstencao: 50,
    obstrucao: 13,
  }

  it('should render scoreboard with title', () => {
    render(<PlacarVotos placar={mockPlacar} title="Resultado da Votação" />)

    expect(screen.getByText('Resultado da Votação')).toBeInTheDocument()
    expect(screen.getByText(/Total: 513 votos/)).toBeInTheDocument()
  })

  it('should display correct vote counts', () => {
    render(<PlacarVotos placar={mockPlacar} title="Test" />)

    // Math.round is used: 300/513=58%, 150/513=29%, 50/513=10%, 13/513=3%
    expect(screen.getByText(/300 \(58%\)/)).toBeInTheDocument()
    expect(screen.getByText(/150 \(29%\)/)).toBeInTheDocument()
    expect(screen.getByText(/50 \(10%\)/)).toBeInTheDocument()
    expect(screen.getByText(/13 \(3%\)/)).toBeInTheDocument()
  })

  it('should display all vote types', () => {
    render(<PlacarVotos placar={mockPlacar} />)

    expect(screen.getByText('Sim')).toBeInTheDocument()
    expect(screen.getByText('Não')).toBeInTheDocument()
    expect(screen.getByText('Abstenção')).toBeInTheDocument()
    expect(screen.getByText('Obstrução')).toBeInTheDocument()
  })

  it('should handle zero votes gracefully', () => {
    const zeroPlacar: Placar = {
      sim: 0,
      nao: 0,
      abstencao: 0,
      obstrucao: 0,
    }

    render(<PlacarVotos placar={zeroPlacar} />)

    // All 4 vote types show "0 (0%)"
    const zeroTexts = screen.getAllByText(/0 \(0%\)/)
    expect(zeroTexts.length).toBe(4)
    expect(screen.getByText(/Total: 0 votos/)).toBeInTheDocument()
  })

  it('should handle partial votes', () => {
    const partialPlacar: Placar = {
      sim: 100,
      nao: 0,
      abstencao: 0,
      obstrucao: 0,
    }

    render(<PlacarVotos placar={partialPlacar} />)

    expect(screen.getByText(/100 \(100%\)/)).toBeInTheDocument()
    // 3 vote types show "0 (0%)"
    const zeroTexts = screen.getAllByText(/0 \(0%\)/)
    expect(zeroTexts.length).toBe(3)
  })

  it('should use default title when not provided', () => {
    render(<PlacarVotos placar={mockPlacar} />)

    expect(screen.getByText('Resultado da Votação')).toBeInTheDocument()
  })

  it('should render progress bars for all vote types', () => {
    const { container } = render(<PlacarVotos placar={mockPlacar} />)

    const progressBars = container.querySelectorAll('.h-full')
    expect(progressBars.length).toBeGreaterThanOrEqual(4)
  })
})
