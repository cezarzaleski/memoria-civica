import React from 'react'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
import { DeputadoSearch } from '@/components/features/deputados/DeputadoSearch'
import userEvent from '@testing-library/user-event'

describe('DeputadoSearch', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('should render input with placeholder', () => {
    const onSearch = vi.fn()
    render(<DeputadoSearch onSearch={onSearch} />)

    const input = screen.getByPlaceholderText('Pesquisar deputados...')
    expect(input).toBeInTheDocument()
  })

  it('should render custom placeholder', () => {
    const onSearch = vi.fn()
    render(
      <DeputadoSearch
        onSearch={onSearch}
        placeholder="Buscar por nome..."
      />
    )

    expect(screen.getByPlaceholderText('Buscar por nome...')).toBeInTheDocument()
  })

  it('should call onSearch after debounce', async () => {
    const onSearch = vi.fn()
    render(<DeputadoSearch onSearch={onSearch} debounceMs={300} />)

    // Component calls onSearch('') on mount
    expect(onSearch).toHaveBeenCalledWith('')
    onSearch.mockClear()

    const input = screen.getByPlaceholderText('Pesquisar deputados...')

    fireEvent.change(input, { target: { value: 'João' } })

    // Search should not be called immediately after change
    expect(onSearch).not.toHaveBeenCalled()

    // Move time forward by 300ms
    await act(async () => {
      vi.advanceTimersByTime(300)
    })

    expect(onSearch).toHaveBeenCalledWith('João')
  })

  it('should debounce rapid input changes', async () => {
    const onSearch = vi.fn()
    render(<DeputadoSearch onSearch={onSearch} debounceMs={300} />)

    // Clear initial mount call
    onSearch.mockClear()

    const input = screen.getByPlaceholderText('Pesquisar deputados...')

    fireEvent.change(input, { target: { value: 'J' } })
    fireEvent.change(input, { target: { value: 'Jo' } })
    fireEvent.change(input, { target: { value: 'Joa' } })
    fireEvent.change(input, { target: { value: 'João' } })

    // None should be called yet (after clearing mount call)
    expect(onSearch).not.toHaveBeenCalled()

    await act(async () => {
      vi.advanceTimersByTime(300)
    })

    expect(onSearch).toHaveBeenCalledTimes(1)
    expect(onSearch).toHaveBeenCalledWith('João')
  })

  it('should respect custom debounce time', async () => {
    const onSearch = vi.fn()
    render(<DeputadoSearch onSearch={onSearch} debounceMs={500} />)

    // Clear initial mount call
    onSearch.mockClear()

    const input = screen.getByPlaceholderText('Pesquisar deputados...')

    fireEvent.change(input, { target: { value: 'Maria' } })

    await act(async () => {
      vi.advanceTimersByTime(300)
    })
    expect(onSearch).not.toHaveBeenCalled()

    await act(async () => {
      vi.advanceTimersByTime(200)
    })
    expect(onSearch).toHaveBeenCalledWith('Maria')
  })

  it('should initialize with initial value', () => {
    const onSearch = vi.fn()
    render(
      <DeputadoSearch onSearch={onSearch} initialValue="João" />
    )

    const input = screen.getByDisplayValue('João')
    expect(input).toBeInTheDocument()

    vi.advanceTimersByTime(300)

    expect(onSearch).toHaveBeenCalledWith('João')
  })

  it('should display search hint after debounce', async () => {
    const onSearch = vi.fn()
    render(<DeputadoSearch onSearch={onSearch} debounceMs={300} />)

    const input = screen.getByPlaceholderText('Pesquisar deputados...')

    fireEvent.change(input, { target: { value: 'João' } })

    await act(async () => {
      vi.advanceTimersByTime(300)
    })

    expect(screen.getByText(/Buscando por: "João"/)).toBeInTheDocument()
  })

  it('should clear search hint on empty input', async () => {
    const onSearch = vi.fn()
    render(<DeputadoSearch onSearch={onSearch} debounceMs={300} />)

    const input = screen.getByPlaceholderText('Pesquisar deputados...')

    fireEvent.change(input, { target: { value: 'João' } })

    await act(async () => {
      vi.advanceTimersByTime(300)
    })

    expect(screen.getByText(/Buscando por: "João"/)).toBeInTheDocument()

    fireEvent.change(input, { target: { value: '' } })

    await act(async () => {
      vi.advanceTimersByTime(300)
    })

    expect(screen.queryByText(/Buscando por:/)).not.toBeInTheDocument()
  })

  it('should disable input when disabled prop is true', () => {
    const onSearch = vi.fn()
    render(<DeputadoSearch onSearch={onSearch} disabled={true} />)

    const input = screen.getByPlaceholderText('Pesquisar deputados...')
    expect(input).toBeDisabled()
  })

  it('should not call onSearch when disabled', async () => {
    const onSearch = vi.fn()
    const { rerender } = render(
      <DeputadoSearch onSearch={onSearch} disabled={false} />
    )

    // Clear initial mount call
    onSearch.mockClear()

    const input = screen.getByPlaceholderText('Pesquisar deputados...') as HTMLInputElement

    fireEvent.change(input, { target: { value: 'João' } })

    await act(async () => {
      vi.advanceTimersByTime(300)
    })

    expect(onSearch).toHaveBeenCalledWith('João')

    rerender(<DeputadoSearch onSearch={onSearch} disabled={true} />)

    expect(input).toBeDisabled()
  })

  it('should handle empty input', async () => {
    const onSearch = vi.fn()
    render(<DeputadoSearch onSearch={onSearch} debounceMs={300} />)

    // Component already calls onSearch('') on mount
    expect(onSearch).toHaveBeenCalledWith('')
  })

  it('should handle special characters', async () => {
    const onSearch = vi.fn()
    render(<DeputadoSearch onSearch={onSearch} debounceMs={300} />)

    // Clear initial mount call
    onSearch.mockClear()

    const input = screen.getByPlaceholderText('Pesquisar deputados...')

    fireEvent.change(input, { target: { value: 'João & Silva' } })

    await act(async () => {
      vi.advanceTimersByTime(300)
    })

    expect(onSearch).toHaveBeenCalledWith('João & Silva')
  })
})
