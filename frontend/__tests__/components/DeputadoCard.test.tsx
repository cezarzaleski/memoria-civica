import React from 'react'
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { DeputadoCard } from '@/components/features/deputados/DeputadoCard'

describe('DeputadoCard', () => {
  const mockDeputado = {
    id: '1',
    nome: 'João Silva Santos',
    partido: 'PT',
    uf: 'SP',
    foto_url: 'http://example.com/foto.jpg',
    email: 'joao@example.com',
  }

  it('should render deputado with name', () => {
    render(<DeputadoCard deputado={mockDeputado} />)

    expect(screen.getByText('João Silva Santos')).toBeInTheDocument()
  })

  it('should render deputado party badge', () => {
    render(<DeputadoCard deputado={mockDeputado} />)

    expect(screen.getByText('PT')).toBeInTheDocument()
  })

  it('should render deputado state badge', () => {
    render(<DeputadoCard deputado={mockDeputado} />)

    const ufs = screen.getAllByText('SP')
    expect(ufs.length).toBeGreaterThan(0)
  })

  it('should display email when available', () => {
    render(<DeputadoCard deputado={mockDeputado} />)

    expect(screen.getByText('joao@example.com')).toBeInTheDocument()
  })

  it('should render photo when foto_url is available', () => {
    const { container } = render(<DeputadoCard deputado={mockDeputado} />)

    const img = container.querySelector('img')
    expect(img).toBeInTheDocument()
    expect(img).toHaveAttribute('src', 'http://example.com/foto.jpg')
    expect(img).toHaveAttribute('alt', 'João Silva Santos')
  })

  it('should render avatar with initials when no foto_url', () => {
    const deputadoSemFoto = {
      ...mockDeputado,
      foto_url: undefined,
    }

    const { container } = render(<DeputadoCard deputado={deputadoSemFoto} />)

    // Should not have image
    const img = container.querySelector('img')
    expect(img).not.toBeInTheDocument()

    // Should display initials JS
    expect(screen.getByText('JS')).toBeInTheDocument()
  })

  it('should handle single name correctly', () => {
    const deputadoUmNome = {
      ...mockDeputado,
      nome: 'João',
    }

    const { container } = render(<DeputadoCard deputado={deputadoUmNome} />)

    // Should create initials from first letter
    expect(screen.getByText('J')).toBeInTheDocument()
  })

  it('should handle null nome gracefully', () => {
    const deputadoSemNome = {
      ...mockDeputado,
      nome: null as any,
    }

    const { container } = render(<DeputadoCard deputado={deputadoSemNome} />)

    expect(screen.getByText('?')).toBeInTheDocument()
  })

  it('should call onClick handler when clicked', () => {
    const onClick = vi.fn()
    render(<DeputadoCard deputado={mockDeputado} onClick={onClick} />)

    const card = screen.getByText('João Silva Santos').closest('div').closest('div')
    if (card) {
      card.click()
      expect(onClick).toHaveBeenCalled()
    }
  })

  it('should handle deputado without email', () => {
    const deputadoSemEmail = {
      ...mockDeputado,
      email: undefined,
    }

    render(<DeputadoCard deputado={deputadoSemEmail} />)

    expect(screen.queryByText('joao@example.com')).not.toBeInTheDocument()
  })

  it('should handle deputado without partido', () => {
    const deputadoSemPartido = {
      ...mockDeputado,
      partido: undefined,
    }

    render(<DeputadoCard deputado={deputadoSemPartido} />)

    // Should still render name and state
    expect(screen.getByText('João Silva Santos')).toBeInTheDocument()
  })

  it('should handle deputado without uf', () => {
    const deputadoSemUf = {
      ...mockDeputado,
      uf: undefined,
    }

    render(<DeputadoCard deputado={deputadoSemUf} />)

    expect(screen.getByText('João Silva Santos')).toBeInTheDocument()
    expect(screen.getByText('PT')).toBeInTheDocument()
  })

  it('should display multiple word names correctly', () => {
    const deputadoNomeLongo = {
      ...mockDeputado,
      nome: 'João da Silva Santos Oliveira',
    }

    const { container } = render(<DeputadoCard deputado={deputadoNomeLongo} />)

    expect(screen.getByText('João da Silva Santos Oliveira')).toBeInTheDocument()
  })
})
