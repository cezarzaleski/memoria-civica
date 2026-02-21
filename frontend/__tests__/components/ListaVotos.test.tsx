import { render, screen, fireEvent } from '@testing-library/react'
import { ListaVotos } from '@/components/features/votacoes/ListaVotos'
import { Voto, TipoVoto } from '@/lib/types/voto'
import { Deputado } from '@/lib/types/deputado'

describe('ListaVotos', () => {
  const mockDeputados: Deputado[] = [
    {
      id: 1,
      nome: 'João Silva',
      sigla_partido: 'PT',
      uf: 'SP',
      foto_url: 'http://example.com/1.jpg',
      email: 'joao@example.com',
    },
    {
      id: 2,
      nome: 'Maria Santos',
      sigla_partido: 'PSDB',
      uf: 'MG',
      foto_url: 'http://example.com/2.jpg',
      email: 'maria@example.com',
    },
    {
      id: 3,
      nome: 'Pedro Oliveira',
      sigla_partido: 'PT',
      uf: 'RJ',
      foto_url: 'http://example.com/3.jpg',
      email: 'pedro@example.com',
    },
    {
      id: 4,
      nome: 'Ana Costa',
      sigla_partido: 'MDB',
      uf: 'BA',
      foto_url: 'http://example.com/4.jpg',
      email: 'ana@example.com',
    },
  ]

  const mockVotos: Voto[] = [
    { id: 1, votacao_id: 1, deputado_id: 1, voto: TipoVoto.SIM, deputado: mockDeputados[0] },
    { id: 2, votacao_id: 1, deputado_id: 2, voto: TipoVoto.NAO, deputado: mockDeputados[1] },
    { id: 3, votacao_id: 1, deputado_id: 3, voto: TipoVoto.ABSTENCAO, deputado: mockDeputados[2] },
    { id: 4, votacao_id: 1, deputado_id: 4, voto: TipoVoto.OBSTRUCAO, deputado: mockDeputados[3] },
  ]

  it('deve renderizar lista de votos com contagem correta', () => {
    render(<ListaVotos votos={mockVotos} />)

    expect(screen.getByText(/Votos \(4 de 4\)/)).toBeInTheDocument()
    expect(screen.getByText('João Silva')).toBeInTheDocument()
    expect(screen.getByText('Maria Santos')).toBeInTheDocument()
  })

  it('deve exibir informações do deputado com sigla_partido', () => {
    render(<ListaVotos votos={mockVotos} />)

    expect(screen.getByText('João Silva')).toBeInTheDocument()
    expect(screen.getByText('PT - SP')).toBeInTheDocument()
  })

  it('deve exibir tipos de voto em badges', () => {
    render(<ListaVotos votos={mockVotos} />)

    expect(screen.getAllByText('Sim').length).toBeGreaterThan(0)
    expect(screen.getAllByText('Não').length).toBeGreaterThan(0)
    expect(screen.getAllByText('Abstenção').length).toBeGreaterThan(0)
    expect(screen.getAllByText('Obstrução').length).toBeGreaterThan(0)
  })

  it('deve exibir estado de loading', () => {
    render(<ListaVotos votos={[]} loading={true} />)

    expect(screen.getByText('Votos')).toBeInTheDocument()
  })

  it('deve exibir estado de erro', () => {
    const errorMessage = 'Erro ao carregar dados'
    render(<ListaVotos votos={[]} error={errorMessage} />)

    expect(screen.getByText('Erro ao carregar votos')).toBeInTheDocument()
    expect(screen.getByText(errorMessage)).toBeInTheDocument()
  })

  it('deve exibir estado vazio', () => {
    render(<ListaVotos votos={[]} />)

    expect(screen.getByText('Nenhum voto encontrado')).toBeInTheDocument()
  })

  it('deve filtrar por tipo de voto canônico', () => {
    render(<ListaVotos votos={mockVotos} />)

    const typeSelect = screen.getAllByDisplayValue('Todos')[0]
    fireEvent.change(typeSelect, { target: { value: TipoVoto.SIM } })

    expect(screen.getByText(/Votos \(1 de 4\)/)).toBeInTheDocument()
    expect(screen.getByText('João Silva')).toBeInTheDocument()
    expect(screen.queryByText('Maria Santos')).not.toBeInTheDocument()
  })

  it('deve filtrar por partido', () => {
    render(<ListaVotos votos={mockVotos} />)

    const partySelects = screen.getAllByDisplayValue('Todos')
    const partySelect = partySelects[1]
    fireEvent.change(partySelect, { target: { value: 'PT' } })

    expect(screen.getByText(/Votos \(2 de 4\)/)).toBeInTheDocument()
    expect(screen.getByText('João Silva')).toBeInTheDocument()
    expect(screen.getByText('Pedro Oliveira')).toBeInTheDocument()
  })

  it('deve ordenar por nome ascendente', () => {
    render(<ListaVotos votos={mockVotos} />)

    const sortSelect = screen.getAllByDisplayValue('Nome (A-Z)')[0]
    fireEvent.change(sortSelect, { target: { value: 'nome-asc' } })

    const names = screen.getAllByText(/Silva|Santos|Oliveira|Costa/)
    expect(names[0].textContent).toContain('Ana Costa')
  })

  it('deve combinar filtros corretamente', () => {
    render(<ListaVotos votos={mockVotos} />)

    const typeSelects = screen.getAllByDisplayValue('Todos')
    const typeSelect = typeSelects[0]
    fireEvent.change(typeSelect, { target: { value: TipoVoto.SIM } })

    expect(screen.getByText(/Votos \(1 de 4\)/)).toBeInTheDocument()
  })

  it('deve exibir mensagem quando não houver votos após filtros', () => {
    render(<ListaVotos votos={mockVotos} />)

    const selects = screen.getAllByRole('combobox')
    fireEvent.change(selects[0], { target: { value: TipoVoto.SIM } })
    fireEvent.change(selects[1], { target: { value: 'PSDB' } })

    expect(screen.getByText('Nenhum voto encontrado com os filtros selecionados')).toBeInTheDocument()
  })

  it('deve lidar com votos sem dados do deputado', () => {
    const votosWithoutDeputado: Voto[] = [
      { id: 1, votacao_id: 1, deputado_id: 1, voto: TipoVoto.SIM },
    ]

    render(<ListaVotos votos={votosWithoutDeputado} />)

    expect(screen.getByText('Deputado desconhecido')).toBeInTheDocument()
  })
})
