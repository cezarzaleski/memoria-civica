import { render, screen } from '@testing-library/react'
import { OrientacoesBancadas } from '@/components/features/votacoes/OrientacoesBancadas'
import { Orientacao } from '@/lib/types'

describe('OrientacoesBancadas', () => {
  const orientacoes: Orientacao[] = [
    {
      id: 1,
      votacao_id: 1,
      sigla_bancada: 'PT',
      orientacao: 'Sim',
      created_at: '2025-01-01T10:00:00Z',
    },
    {
      id: 2,
      votacao_id: 1,
      sigla_bancada: 'PL',
      orientacao: 'Não',
      created_at: '2025-01-01T10:05:00Z',
    },
  ]

  it('deve renderizar orientações com contagem', () => {
    render(<OrientacoesBancadas orientacoes={orientacoes} />)

    expect(screen.getByText('Orientações de Bancada (2)')).toBeInTheDocument()
    expect(screen.getByText('PT')).toBeInTheDocument()
    expect(screen.getByText('PL')).toBeInTheDocument()
    expect(screen.getByText('Sim')).toBeInTheDocument()
    expect(screen.getByText('Não')).toBeInTheDocument()
  })

  it('deve exibir estado de loading', () => {
    const { container } = render(
      <OrientacoesBancadas orientacoes={[]} loading={true} />
    )

    expect(screen.getByText('Orientações de Bancada')).toBeInTheDocument()
    expect(container.querySelectorAll('.animate-pulse').length).toBeGreaterThan(0)
  })

  it('deve exibir estado de erro', () => {
    render(
      <OrientacoesBancadas
        orientacoes={[]}
        error="Falha ao carregar orientações"
      />
    )

    expect(screen.getByText('Falha ao carregar orientações')).toBeInTheDocument()
  })

  it('deve exibir estado vazio', () => {
    render(<OrientacoesBancadas orientacoes={[]} />)

    expect(
      screen.getByText('Não há orientações de bancada para esta votação.')
    ).toBeInTheDocument()
  })
})
