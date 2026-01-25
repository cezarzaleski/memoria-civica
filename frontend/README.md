# Frontend Memória Cívica

Frontend da aplicação Memória Cívica - PWA para acompanhar votações e deputados do Congresso Nacional.

## Stack Tecnológico

- **Next.js 15** - Framework React com App Router
- **React 19** - Biblioteca de UI
- **TypeScript** - Type safety
- **Tailwind CSS** - Estilização utility-first
- **Shadcn/UI** - Componentes acessíveis e customizáveis
- **MSW (Mock Service Worker)** - Mocking de APIs
- **next-pwa** - Progressive Web App capabilities
- **Vitest** - Test runner
- **React Testing Library** - Testes de componentes

## Estructura do Projeto

```
frontend/
├── app/                # Next.js App Router
│   ├── layout.tsx      # Root layout
│   ├── page.tsx        # Home page
│   ├── manifest.ts     # PWA manifest
│   └── globals.css     # Global styles com CSS variables
├── components/         # Componentes React
│   ├── ui/            # Shadcn UI components
│   └── features/      # Domain-specific components
├── lib/
│   ├── types/         # TypeScript type definitions
│   ├── hooks/         # Custom React hooks
│   └── utils.ts       # Utility functions
├── mocks/
│   ├── browser.ts     # MSW browser setup
│   ├── server.ts      # MSW server setup (testing)
│   └── handlers/      # API mock handlers
├── public/            # Static assets
│   └── icons/         # PWA icons
├── __tests__/         # Test files
│   ├── components/    # Component tests
│   └── integration/   # Integration tests
├── next.config.mjs    # Next.js + PWA config
├── tailwind.config.ts # Tailwind configuration
├── tsconfig.json      # TypeScript config
├── vitest.config.ts   # Test runner config
└── package.json       # Dependencies
```

## Configuração e Desenvolvimento

### Instalação

```bash
cd frontend
npm install  # ou pnpm install
```

### Desenvolvimento

```bash
npm run dev
```

Acesse http://localhost:3000

### Testes

```bash
npm run test          # Rodar testes
npm run test:coverage # Cobertura de testes
```

### Linting e Formatação

```bash
npm run lint    # ESLint
npm run format  # Prettier
```

### Build para Produção

```bash
npm run build
npm run start
```

## Recuross PWA

A aplicação está configurada como PWA com:

- **Manifest**: `app/manifest.ts` com metadados de instalação
- **Service Worker**: Configurado via next-pwa
- **Ícones**: Placeholders em `public/icons/` (adicionar ícones reais)
- **Offline Support**: Estratégias de cache para assets estáticos

Para testar a instalação:

1. Build: `npm run build && npm run start`
2. Abra DevTools → Application → Manifest
3. Instale no celular (Chrome Android) ou "Instalar app" (Safari iOS)

## Integração com Backend

MSW permite desenvolvimento sem backend. Para integrar com API real:

1. Remova os handlers MSW ou desabilite com variável de ambiente
2. Atualize os hooks em `lib/hooks/` para chamar endpoints reais
3. Configure CORS no backend se necessário

Os endpoints esperados estão documentados em `mocks/handlers/`

## Padrões de Código

### Importações Absolutas

Use o alias `@/` para importações:

```tsx
import { cn } from '@/lib/utils';
import type { Votacao } from '@/lib/types';
```

### Tipagem

Todos os componentes devem ter tipos explícitos:

```tsx
interface VotacaoCardProps {
  votacao: Votacao;
  onClick?: (id: string) => void;
}

export function VotacaoCard({ votacao, onClick }: VotacaoCardProps) {
  // ...
}
```

### Componentes

- Componentes em PascalCase: `VotacaoCard.tsx`
- Arquivos em kebab-case: `votacao-card.tsx` (opcional, PascalCase também aceito)
- Hooks customizados em camelCase: `useVotacoes.ts`

### Testes

Target mínimo de cobertura:

- **Componentes features**: 70%
- **Componentes UI (Shadcn)**: 50% (ou sem testes)
- **Integração**: Fluxos principais cobertes

Use React Testing Library focando em comportamento do usuário, não implementação.

## Troubleshooting

### MSW não está interceptando requests

1. Verifique se `npm run dev` está rodando
2. Abra DevTools → Network e procure por `browser-request-*.js`
3. Se não aparecer, reinicie o servidor

### Tailwind CSS não aplicando estilos

1. Verifique se `tailwind.config.ts` está correto
2. Limpe: `rm -rf .next` e `npm run dev`
3. Verifique path patterns em `tailwind.config.ts`

### Build fails com TypeScript

Rode `npm run build` localmente para ver erro real:

```bash
npm run build 2>&1 | head -50
```

## Próximos Passos

- [ ] Instalar componentes Shadcn necessários (Button, Card, etc)
- [ ] Implementar MSW handlers para APIs
- [ ] Criar componentes feature (VotacaoCard, DeputadoCard, etc)
- [ ] Implementar páginas (Feed, Detalhes, etc)
- [ ] Adicionar PWA icons reais
- [ ] Testes e integração

## Referências

- [Next.js 15 Docs](https://nextjs.org/docs)
- [React 19](https://react.dev)
- [Shadcn/UI](https://ui.shadcn.com)
- [MSW](https://mswjs.io)
- [Tailwind CSS](https://tailwindcss.com)
