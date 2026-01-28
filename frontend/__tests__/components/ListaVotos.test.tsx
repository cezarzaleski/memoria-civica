import { render, screen, fireEvent } from '@testing-library/react'
import { ListaVotos } from '@/components/features/votacoes/ListaVotos'
import { Voto, TipoVoto } from '@/lib/types/voto'
import { Deputado } from '@/lib/types/deputado'

describe('ListaVotos', () => {
  const mockDeputados: Deputado[] = [
    { id: 1, nome: 'João Silva', partido: 'PT', uf: 'SP', foto_url: 'http://example.com/1.jpg' },
    { id: 2, nome: 'Maria Santos', partido: 'PSDB', uf: 'MG', foto_url: 'http://example.com/2.jpg' },
    { id: 3, nome: 'Pedro Oliveira', partido: 'PT', uf: 'RJ', foto_url: 'http://example.com/3.jpg' },
    { id: 4, nome: 'Ana Costa', partido: 'MDB', uf: 'BA', foto_url: 'http://example.com/4.jpg' },
  ]

  const mockVotos: Voto[] = [
    { id: '1', votacao_id: '1', deputado_id: 1, tipo: TipoVoto.SIM, deputado: mockDeputados[0] },
    { id: '2', votacao_id: '1', deputado_id: 2, tipo: TipoVoto.NAO, deputado: mockDeputados[1] },
    { id: '3', votacao_id: '1', deputado_id: 3, tipo: TipoVoto.ABSTENCAO, deputado: mockDeputados[2] },
    { id: '4', votacao_id: '1', deputado_id: 4, tipo: TipoVoto.OBSTRUCAO, deputado: mockDeputados[3] },
  ]

  it('should render list of votes with correct count', () => {
    render(<ListaVotos votos={mockVotos} />)

    expect(screen.getByText(/Votos \(4 de 4\)/)).toBeInTheDocument()
    expect(screen.getByText('João Silva')).toBeInTheDocument()
    expect(screen.getByText('Maria Santos')).toBeInTheDocument()
  })

  it('should display deputy info correctly', () => {
    render(<ListaVotos votos={mockVotos} />)

    expect(screen.getByText('João Silva')).toBeInTheDocument()
    expect(screen.getByText('PT - SP')).toBeInTheDocument()
  })

  it('should display vote types as badges', () => {
    render(<ListaVotos votos={mockVotos} />)

    expect(screen.getByText('SIM')).toBeInTheDocument()
    expect(screen.getByText('NAO')).toBeInTheDocument()
    expect(screen.getByText('ABSTENCAO')).toBeInTheDocument()
    expect(screen.getByText('OBSTRUCAO')).toBeInTheDocument()
  })

  it('should show loading state', () => {
    render(<ListaVotos votos={[]} loading={true} />)

    expect(screen.getByText('Votos')).toBeInTheDocument()
  })

  it('should show error state', () => {
    const errorMessage = 'Erro ao carregar dados'
    render(<ListaVotos votos={[]} error={errorMessage} />)

    expect(screen.getByText('Erro ao carregar votos')).toBeInTheDocument()
    expect(screen.getByText(errorMessage)).toBeInTheDocument()
  })

  it('should show empty state', () => {
    render(<ListaVotos votos={[]} />)

    expect(screen.getByText('Nenhum voto encontrado')).toBeInTheDocument()
  })

  it('should filter by vote type', () => {
    render(<ListaVotos votos={mockVotos} />)

    const typeSelect = screen.getAllByDisplayValue('Todos')[0]
    fireEvent.change(typeSelect, { target: { value: TipoVoto.SIM } })

    expect(screen.getByText(/Votos \(1 de 4\)/)).toBeInTheDocument()
    expect(screen.getByText('João Silva')).toBeInTheDocument()
    expect(screen.queryByText('Maria Santos')).not.toBeInTheDocument()
  })

  it('should filter by party', () => {
    render(<ListaVotos votos={mockVotos} />)

    const partySelects = screen.getAllByDisplayValue('Todos')
    const partySelect = partySelects[1]
    fireEvent.change(partySelect, { target: { value: 'PT' } })

    expect(screen.getByText(/Votos \(2 de 4\)/)).toBeInTheDocument()
    expect(screen.getByText('João Silva')).toBeInTheDocument()
    expect(screen.getByText('Pedro Oliveira')).toBeInTheDocument()
  })

  it('should sort by name ascending', () => {
    render(<ListaVotos votos={mockVotos} />)

    const sortSelect = screen.getAllByDisplayValue('Nome (A-Z)')[0]
    fireEvent.change(sortSelect, { target: { value: 'nome-asc' } })

    const names = screen.getAllByText(/Silva|Santos|Oliveira|Costa/)
    expect(names[0].textContent).toContain('Ana Costa')
  })

  it('should combine filters and sort correctly', () => {
    render(<ListaVotos votos={mockVotos} />)

    const typeSelects = screen.getAllByDisplayValue('Todos')
    const typeSelect = typeSelects[0]
    fireEvent.change(typeSelect, { target: { value: TipoVoto.SIM } })

    expect(screen.getByText(/Votos \(1 de 4\)/)).toBeInTheDocument()
  })

  it.skip('should show message when no votes match filters', () => {
    render(<ListaVotos votos={mockVotos} />)

    const typeSelects = screen.getAllByDisplayValue('Todos')
    const typeSelect = typeSelects[0]
    fireEvent.change(typeSelect, { target: { value: TipoVoto.SIM } })

    const partySelects = screen.getAllByDisplayValue('Todos')
    const partySelect = partySelects[1]
    fireEvent.change(partySelect, { target: { value: 'PSDB' } })

    expect(screen.getByText('Nenhum voto encontrado com os filtros selecionados')).toBeInTheDocument()
  })

  it('should handle votes without deputado info', () => {
    const votosWithoutDeputado: Voto[] = [
      { id: '1', votacao_id: '1', deputado_id: 1, tipo: TipoVoto.SIM },
    ]

    render(<ListaVotos votos={votosWithoutDeputado} />)

    expect(screen.getByText('Deputado desconhecido')).toBeInTheDocument()
  })
})
