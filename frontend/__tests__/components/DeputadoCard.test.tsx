import React from 'react'
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { DeputadoCard } from '@/components/features/deputados/DeputadoCard'

describe('DeputadoCard', () => {
  const mockDeputado = {
    id: 1,
    nome: 'João Silva Santos',
    sigla_partido: 'PT',
    uf: 'SP',
    foto_url: 'http://example.com/foto.jpg',
    email: 'joao@example.com',
  }

  it('deve renderizar nome do deputado', () => {
    render(<DeputadoCard deputado={mockDeputado} />)

    expect(screen.getByText('João Silva Santos')).toBeInTheDocument()
  })

  it('deve renderizar badge de sigla_partido', () => {
    render(<DeputadoCard deputado={mockDeputado} />)

    expect(screen.getByText('PT')).toBeInTheDocument()
  })

  it('deve renderizar badge de UF', () => {
    render(<DeputadoCard deputado={mockDeputado} />)

    const ufs = screen.getAllByText('SP')
    expect(ufs.length).toBeGreaterThan(0)
  })

  it('deve exibir email quando disponível', () => {
    render(<DeputadoCard deputado={mockDeputado} />)

    expect(screen.getByText('joao@example.com')).toBeInTheDocument()
  })

  it('deve renderizar foto quando foto_url estiver disponível', () => {
    const { container } = render(<DeputadoCard deputado={mockDeputado} />)

    const img = container.querySelector('img')
    expect(img).toBeInTheDocument()
    expect(img).toHaveAttribute('src', 'http://example.com/foto.jpg')
    expect(img).toHaveAttribute('alt', 'João Silva Santos')
  })

  it('deve renderizar avatar com iniciais quando não houver foto', () => {
    const deputadoSemFoto = {
      ...mockDeputado,
      foto_url: undefined as unknown as string,
    }

    const { container } = render(<DeputadoCard deputado={deputadoSemFoto} />)

    const img = container.querySelector('img')
    expect(img).not.toBeInTheDocument()
    expect(screen.getByText('JS')).toBeInTheDocument()
  })

  it('deve lidar com nome único ao gerar iniciais', () => {
    const deputadoUmNome = {
      ...mockDeputado,
      nome: 'João',
      foto_url: undefined as unknown as string,
    }

    render(<DeputadoCard deputado={deputadoUmNome} />)

    expect(screen.getByText('J')).toBeInTheDocument()
  })

  it('deve lidar com nome nulo sem quebrar', () => {
    const deputadoSemNome = {
      ...mockDeputado,
      nome: null as unknown as string,
      foto_url: undefined as unknown as string,
    }

    render(<DeputadoCard deputado={deputadoSemNome} />)

    expect(screen.getByText('?')).toBeInTheDocument()
  })

  it('deve chamar onClick quando card for clicado', () => {
    const onClick = vi.fn()
    render(<DeputadoCard deputado={mockDeputado} onClick={onClick} />)

    const card = screen.getByText('João Silva Santos').closest('div')?.closest('div')
    if (card) {
      card.click()
      expect(onClick).toHaveBeenCalled()
    }
  })

  it('deve lidar com deputado sem email', () => {
    const deputadoSemEmail = {
      ...mockDeputado,
      email: undefined as unknown as string,
    }

    render(<DeputadoCard deputado={deputadoSemEmail} />)

    expect(screen.queryByText('joao@example.com')).not.toBeInTheDocument()
  })

  it('deve lidar com deputado sem sigla_partido', () => {
    const deputadoSemPartido = {
      ...mockDeputado,
      sigla_partido: undefined as unknown as string,
    }

    render(<DeputadoCard deputado={deputadoSemPartido} />)

    expect(screen.getByText('João Silva Santos')).toBeInTheDocument()
  })

  it('deve lidar com deputado sem UF', () => {
    const deputadoSemUf = {
      ...mockDeputado,
      uf: undefined as unknown as string,
    }

    render(<DeputadoCard deputado={deputadoSemUf} />)

    expect(screen.getByText('João Silva Santos')).toBeInTheDocument()
    expect(screen.getByText('PT')).toBeInTheDocument()
  })

  it('deve exibir nomes longos corretamente', () => {
    const deputadoNomeLongo = {
      ...mockDeputado,
      nome: 'João da Silva Santos Oliveira',
    }

    render(<DeputadoCard deputado={deputadoNomeLongo} />)

    expect(screen.getByText('João da Silva Santos Oliveira')).toBeInTheDocument()
  })
})
