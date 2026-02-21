import { render, screen } from '@testing-library/react'
import { CategoriasCivicas } from '@/components/features/votacoes/CategoriasCivicas'
import { ProposicaoCategoria } from '@/lib/types'

describe('CategoriasCivicas', () => {
  const categorias: ProposicaoCategoria[] = [
    {
      id: 1,
      proposicao_id: 1,
      categoria_id: 10,
      origem: 'manual',
      created_at: '2025-01-01T10:00:00Z',
      categoria: {
        id: 10,
        codigo: 'saude-publica',
        nome: 'Saúde Pública',
        descricao: 'Ações legislativas focadas no SUS.',
      },
    },
    {
      id: 2,
      proposicao_id: 1,
      categoria_id: 11,
      origem: 'automatica',
      created_at: '2025-01-01T10:10:00Z',
      categoria: {
        id: 11,
        codigo: 'educacao',
        nome: 'Educação',
        descricao: 'Políticas para acesso e qualidade da educação.',
      },
    },
    {
      id: 3,
      proposicao_id: 1,
      categoria_id: 10,
      origem: 'automatica',
      created_at: '2025-01-01T10:20:00Z',
      categoria: {
        id: 10,
        codigo: 'saude-publica',
        nome: 'Saúde Pública',
        descricao: 'Ações legislativas focadas no SUS.',
      },
    },
  ]

  it('deve renderizar categorias cívicas e origem', () => {
    render(<CategoriasCivicas categorias={categorias} />)

    expect(screen.getByText('Categorias Cívicas (3)')).toBeInTheDocument()
    expect(screen.getAllByText('Saúde Pública').length).toBe(2)
    expect(screen.getByText('Educação')).toBeInTheDocument()
    expect(screen.getAllByText('manual').length).toBe(1)
    expect(screen.getAllByText('automatica').length).toBe(2)
  })

  it('deve exibir estado de loading', () => {
    const { container } = render(
      <CategoriasCivicas categorias={[]} loading={true} />
    )

    expect(screen.getByText('Categorias Cívicas')).toBeInTheDocument()
    expect(container.querySelectorAll('.animate-pulse').length).toBeGreaterThan(0)
  })

  it('deve exibir estado de erro', () => {
    render(
      <CategoriasCivicas
        categorias={[]}
        error="Falha ao carregar categorias"
      />
    )

    expect(screen.getByText('Falha ao carregar categorias')).toBeInTheDocument()
  })

  it('deve exibir estado vazio', () => {
    render(<CategoriasCivicas categorias={[]} />)

    expect(
      screen.getByText('Esta votação não possui categorias cívicas associadas.')
    ).toBeInTheDocument()
  })
})
