import { render, screen } from '@testing-library/react'
import { PlacarVotos } from '@/components/features/votacoes/PlacarVotos'
import { Placar } from '@/lib/types/votacao'

describe('PlacarVotos', () => {
  const mockPlacar: Placar = {
    votos_sim: 300,
    votos_nao: 150,
    votos_outros: 63,
  }

  it('deve renderizar placar com título', () => {
    render(<PlacarVotos placar={mockPlacar} title="Resultado da Votação" />)

    expect(screen.getByText('Resultado da Votação')).toBeInTheDocument()
    expect(screen.getByText(/Total: 513 votos/)).toBeInTheDocument()
  })

  it('deve exibir contagens e percentuais corretos', () => {
    render(<PlacarVotos placar={mockPlacar} title="Teste" />)

    // Math.round: 300/513=58%, 150/513=29%, 63/513=12%
    expect(screen.getByText(/300 \(58%\)/)).toBeInTheDocument()
    expect(screen.getByText(/150 \(29%\)/)).toBeInTheDocument()
    expect(screen.getByText(/63 \(12%\)/)).toBeInTheDocument()
  })

  it('deve exibir os tipos de voto canônicos', () => {
    render(<PlacarVotos placar={mockPlacar} />)

    expect(screen.getByText('Sim')).toBeInTheDocument()
    expect(screen.getByText('Não')).toBeInTheDocument()
    expect(screen.getByText('Outros')).toBeInTheDocument()
  })

  it('deve lidar com placar zerado', () => {
    const zeroPlacar: Placar = {
      votos_sim: 0,
      votos_nao: 0,
      votos_outros: 0,
    }

    render(<PlacarVotos placar={zeroPlacar} />)

    const zeroTexts = screen.getAllByText(/0 \(0%\)/)
    expect(zeroTexts.length).toBe(3)
    expect(screen.getByText(/Total: 0 votos/)).toBeInTheDocument()
  })

  it('deve lidar com placar parcial', () => {
    const partialPlacar: Placar = {
      votos_sim: 100,
      votos_nao: 0,
      votos_outros: 0,
    }

    render(<PlacarVotos placar={partialPlacar} />)

    expect(screen.getByText(/100 \(100%\)/)).toBeInTheDocument()
    const zeroTexts = screen.getAllByText(/0 \(0%\)/)
    expect(zeroTexts.length).toBe(2)
  })

  it('deve usar título padrão quando não informado', () => {
    render(<PlacarVotos placar={mockPlacar} />)

    expect(screen.getByText('Resultado da Votação')).toBeInTheDocument()
  })

  it('deve renderizar barras de progresso para todos os tipos', () => {
    const { container } = render(<PlacarVotos placar={mockPlacar} />)

    const progressBars = container.querySelectorAll('.h-full')
    expect(progressBars.length).toBeGreaterThanOrEqual(3)
  })
})
