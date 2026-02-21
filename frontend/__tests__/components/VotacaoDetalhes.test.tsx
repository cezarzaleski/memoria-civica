import React from 'react'
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { VotacaoDetalhes } from '@/components/features/votacoes/VotacaoDetalhes'
import { ResultadoVotacao, Votacao } from '@/lib/types/votacao'

describe('VotacaoDetalhes', () => {
  const mockVotacao: Votacao = {
    id: 1,
    data_hora: '2024-01-15T10:00:00Z',
    resultado: ResultadoVotacao.APROVADO,
    placar: { votos_sim: 200, votos_nao: 100, votos_outros: 63 },
    proposicao_id: 1,
    sigla_orgao: 'PLEN',
    eh_nominal: true,
    descricao: 'Sessão deliberativa sobre reforma tributária.',
    proposicao: {
      id: 1,
      tipo: 'PL',
      numero: 1234,
      ano: 2024,
      ementa: 'Reforma Tributária',
      data_apresentacao: '2024-01-01T00:00:00Z',
    },
  }

  it('deve renderizar título da proposição', () => {
    render(<VotacaoDetalhes votacao={mockVotacao} />)

    expect(screen.getByText('PL 1234/2024')).toBeInTheDocument()
  })

  it('deve renderizar data_hora formatada', () => {
    render(<VotacaoDetalhes votacao={mockVotacao} />)

    expect(screen.getByText(/15\/01\/2024/)).toBeInTheDocument()
  })

  it('deve renderizar campos adicionais de sessão e metadados', () => {
    render(<VotacaoDetalhes votacao={mockVotacao} />)

    expect(screen.getByText('Descrição da Sessão')).toBeInTheDocument()
    expect(screen.getByText('Sessão deliberativa sobre reforma tributária.')).toBeInTheDocument()
    expect(screen.getByText('Órgão')).toBeInTheDocument()
    expect(screen.getByText('PLEN')).toBeInTheDocument()
    expect(screen.getByText('Votação nominal')).toBeInTheDocument()
    expect(screen.getByText('Sim')).toBeInTheDocument()
  })

  it('deve renderizar badge com resultado canônico', () => {
    render(<VotacaoDetalhes votacao={mockVotacao} />)

    expect(screen.getByText('Resultado')).toBeInTheDocument()
    expect(screen.getByText('Aprovado')).toBeInTheDocument()
  })

  it('deve mostrar skeleton quando loading é true', () => {
    const { container } = render(
      <VotacaoDetalhes votacao={mockVotacao} loading={true} />
    )

    const skeletons = container.querySelectorAll('.animate-pulse')
    expect(skeletons.length).toBeGreaterThan(0)
  })

  it('deve exibir botão de voltar quando onBack é informado', () => {
    const onBack = vi.fn()
    render(<VotacaoDetalhes votacao={mockVotacao} onBack={onBack} />)

    expect(screen.getByText('← Voltar')).toBeInTheDocument()
  })

  it('deve chamar onBack ao clicar no botão de voltar', () => {
    const onBack = vi.fn()
    render(<VotacaoDetalhes votacao={mockVotacao} onBack={onBack} />)

    const backButton = screen.getByText('← Voltar')
    backButton.click()

    expect(onBack).toHaveBeenCalled()
  })

  it('não deve exibir botão de voltar quando onBack não é informado', () => {
    render(<VotacaoDetalhes votacao={mockVotacao} />)

    expect(screen.queryByText('← Voltar')).not.toBeInTheDocument()
  })

  it('deve exibir seção de explicação quando llmExplanation é informada', () => {
    const explanation = 'Resumo em linguagem simples da votação.'
    render(
      <VotacaoDetalhes
        votacao={mockVotacao}
        llmExplanation={explanation}
      />
    )

    expect(screen.getByText('Explicação Simplificada')).toBeInTheDocument()
    expect(screen.getByText(explanation)).toBeInTheDocument()
  })

  it('deve mostrar skeleton da explicação quando llmLoading é true', () => {
    const { container } = render(
      <VotacaoDetalhes
        votacao={mockVotacao}
        llmExplanation=""
        llmLoading={true}
      />
    )

    expect(screen.getByText('Explicação Simplificada')).toBeInTheDocument()
    const skeletons = container.querySelectorAll('.animate-pulse')
    expect(skeletons.length).toBeGreaterThan(0)
  })

  it('não deve exibir seção de explicação quando não houver conteúdo e llmLoading for false', () => {
    render(<VotacaoDetalhes votacao={mockVotacao} />)

    expect(screen.queryByText('Explicação Simplificada')).not.toBeInTheDocument()
  })

  it('deve tratar votação sem proposição', () => {
    const votacaoSemProposicao: Votacao = {
      ...mockVotacao,
      proposicao: undefined,
    }

    render(<VotacaoDetalhes votacao={votacaoSemProposicao} />)

    expect(screen.getByText('Votação')).toBeInTheDocument()
  })
})
