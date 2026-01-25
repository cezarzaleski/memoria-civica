import React from 'react'
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ListaVotos } from '@/components/features/votacoes/ListaVotos'
import { TipoVoto } from '@/lib/types/voto'

describe('ListaVotos', () => {
  const mockVotos = [
    {
      id: '1',
      tipo: TipoVoto.SIM,
      deputado: {
        id: '1',
        nome: 'João Silva',
        partido: 'PT',
        uf: 'SP',
      },
    },
    {
      id: '2',
      tipo: TipoVoto.NAO,
      deputado: {
        id: '2',
        nome: 'Maria Santos',
        partido: 'PSD',
        uf: 'RJ',
      },
    },
    {
      id: '3',
      tipo: TipoVoto.ABSTENCAO,
      deputado: {
        id: '3',
        nome: 'Carlos Oliveira',
        partido: 'MDB',
        uf: 'MG',
      },
    },
  ]

  it('should render lista votos with title', () => {
    render(<ListaVotos votos={mockVotos} />)

    expect(screen.getByText(/Votos \(3\)/)).toBeInTheDocument()
  })

  it('should render all votos', () => {
    render(<ListaVotos votos={mockVotos} />)

    expect(screen.getByText('João Silva')).toBeInTheDocument()
    expect(screen.getByText('Maria Santos')).toBeInTheDocument()
    expect(screen.getByText('Carlos Oliveira')).toBeInTheDocument()
  })

  it('should display deputado party and state', () => {
    render(<ListaVotos votos={mockVotos} />)

    expect(screen.getByText(/PT - SP/)).toBeInTheDocument()
    expect(screen.getByText(/PSD - RJ/)).toBeInTheDocument()
    expect(screen.getByText(/MDB - MG/)).toBeInTheDocument()
  })

  it('should display vote type badges', () => {
    render(<ListaVotos votos={mockVotos} />)

    expect(screen.getByText(TipoVoto.SIM)).toBeInTheDocument()
    expect(screen.getByText(TipoVoto.NAO)).toBeInTheDocument()
    expect(screen.getByText(TipoVoto.ABSTENCAO)).toBeInTheDocument()
  })

  it('should show loading skeleton when loading is true', () => {
    const { container } = render(<ListaVotos votos={[]} loading={true} />)

    const skeletons = container.querySelectorAll('.animate-pulse')
    expect(skeletons.length).toBeGreaterThan(0)
  })

  it('should display empty message when no votos', () => {
    render(<ListaVotos votos={[]} emptyMessage="Nenhum voto encontrado" />)

    expect(screen.getByText('Nenhum voto encontrado')).toBeInTheDocument()
  })

  it('should display custom empty message', () => {
    render(
      <ListaVotos votos={[]} emptyMessage="Nenhum voto disponível" />
    )

    expect(screen.getByText('Nenhum voto disponível')).toBeInTheDocument()
  })

  it('should display error message when error is provided', () => {
    render(
      <ListaVotos votos={[]} error="Erro ao carregar votos" />
    )

    expect(screen.getByText('Erro ao carregar votos')).toBeInTheDocument()
  })

  it('should display "Erro ao carregar votos" header on error', () => {
    render(
      <ListaVotos votos={[]} error="Network error" />
    )

    expect(screen.getByText('Erro ao carregar votos')).toBeInTheDocument()
  })

  it('should handle votos without deputado', () => {
    const votosComVazio = [
      {
        id: '1',
        tipo: TipoVoto.SIM,
        deputado: undefined,
      },
    ]

    render(<ListaVotos votos={votosComVazio} />)

    expect(screen.getByText('Deputado desconhecido')).toBeInTheDocument()
  })

  it('should render all vote types with correct styling', () => {
    const votosCompletos = [
      {
        id: '1',
        tipo: TipoVoto.SIM,
        deputado: { id: '1', nome: 'Test1', partido: 'PT', uf: 'SP' },
      },
      {
        id: '2',
        tipo: TipoVoto.NAO,
        deputado: { id: '2', nome: 'Test2', partido: 'PSD', uf: 'RJ' },
      },
      {
        id: '3',
        tipo: TipoVoto.ABSTENCAO,
        deputado: { id: '3', nome: 'Test3', partido: 'MDB', uf: 'MG' },
      },
      {
        id: '4',
        tipo: TipoVoto.OBSTRUCAO,
        deputado: { id: '4', nome: 'Test4', partido: 'PP', uf: 'BA' },
      },
    ]

    render(<ListaVotos votos={votosCompletos} />)

    expect(screen.getByText(TipoVoto.SIM)).toBeInTheDocument()
    expect(screen.getByText(TipoVoto.NAO)).toBeInTheDocument()
    expect(screen.getByText(TipoVoto.ABSTENCAO)).toBeInTheDocument()
    expect(screen.getByText(TipoVoto.OBSTRUCAO)).toBeInTheDocument()
  })
})
