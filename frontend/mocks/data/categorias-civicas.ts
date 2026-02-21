import type { CategoriaCivica } from '@/lib/types';

export const CATEGORIAS_CIVICAS_FIXTURES: CategoriaCivica[] = [
  {
    id: 1,
    codigo: 'saude-publica',
    nome: 'Saúde Pública',
    descricao: 'Políticas de acesso, financiamento e qualidade do SUS.',
    icone: 'heart-pulse',
  },
  {
    id: 2,
    codigo: 'educacao',
    nome: 'Educação',
    descricao: 'Educação básica, técnica e superior com foco em inclusão.',
    icone: 'graduation-cap',
  },
  {
    id: 3,
    codigo: 'seguranca-publica',
    nome: 'Segurança Pública',
    descricao: 'Prevenção da violência e fortalecimento da segurança cidadã.',
    icone: 'shield-check',
  },
  {
    id: 4,
    codigo: 'economia-trabalho',
    nome: 'Economia e Trabalho',
    descricao: 'Emprego, renda, desenvolvimento produtivo e equilíbrio fiscal.',
    icone: 'briefcase',
  },
  {
    id: 5,
    codigo: 'meio-ambiente',
    nome: 'Meio Ambiente',
    descricao: 'Mudanças climáticas, preservação e transição ecológica.',
    icone: 'leaf',
  },
  {
    id: 6,
    codigo: 'direitos-civis',
    nome: 'Direitos Civis',
    descricao: 'Direitos humanos, igualdade e proteção de grupos vulneráveis.',
    icone: 'scale',
  },
  {
    id: 7,
    codigo: 'infraestrutura',
    nome: 'Infraestrutura',
    descricao: 'Mobilidade, saneamento e logística para o desenvolvimento.',
    icone: 'building-2',
  },
  {
    id: 8,
    codigo: 'transparencia',
    nome: 'Transparência e Integridade',
    descricao: 'Controle social, dados abertos e combate à corrupção.',
    icone: 'search-check',
  },
];

export function getCategoriaCivicaById(id: number): CategoriaCivica | undefined {
  return CATEGORIAS_CIVICAS_FIXTURES.find((categoria) => categoria.id === id);
}
