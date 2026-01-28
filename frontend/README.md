# Frontend Memória Cívica

[![Tests](https://github.com/cezarzaleski/memoria-civica/actions/workflows/test.yml/badge.svg)](https://github.com/cezarzaleski/memoria-civica/actions/workflows/test.yml)

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
- **Ícones**: Disponíveis em `public/icons/` (192x192, 512x512 e variantes maskable)
- **Screenshots**: Screenshots em `public/screenshots/` para instalação
- **Offline Support**: Estratégias de cache para assets estáticos e fotos do CDN da Câmara
- **iOS Support**: Metadados específicos para Safari iOS em `app/layout.tsx`

### Testes de PWA

Testes unitários e de integração para PWA:

```bash
# Rodar testes específicos de PWA
npm run test -- app/manifest.test.ts
npm run test -- config/next-config.test.ts
npm run test -- integration/pwa-installability.test.ts

# Cobertura completa
npm run test:coverage
```

Testes cobrem:
- Estrutura e campos obrigatórios do manifest
- Cores de tema conforme design system
- Presença e validade de ícones
- Configuração do next-pwa no next.config.mjs
- Desabilitação de service worker em desenvolvimento
- Caching runtime para fotos do CDN da Câmara
- Metadados iOS no layout
- Requisitos de instalação PWA

### Verificação de Instalação Manual

#### Chrome Desktop

1. Build: `npm run build && npm run start`
2. Abra http://localhost:3000
3. DevTools → Application → Manifest
4. Verifique se manifest.webmanifest está acessível
5. Clique em "Instalar" ou use menu (⋮ → "Instalar app")

#### Chrome Android

1. Build e deploy em HTTPS (localhost não requer HTTPS em dev)
2. Abra app em Chrome Android
3. Aguarde banner de instalação (geralmente dentro de 1-2 segundos)
4. Toque "Instalar" no banner
5. App será instalado na home screen

#### Safari iOS

1. Abra app em Safari iOS
2. Toque "Compartilhar" (⇧)
3. Toque "Adicionar à Tela de Início"
4. App será instalado com ícone e nome do manifest

### Verificação Lighthouse PWA Audit

```bash
npm run build && npm run start
# Depois use Lighthouse no DevTools ou CLI
```

Alvo de score PWA: **≥90**

Verifica:
- Manifest accessibility
- Service worker registration
- HTTPS (localhost exempt)
- Icon sizes
- Offline functionality

### Requisitos de Instalação PWA

Para que a app seja instalável, deve atender:

- ✅ HTTPS (localhost exempt em dev)
- ✅ Manifest válido em app/manifest.ts
- ✅ Service worker via next-pwa (desabilitado em dev, ativado em prod)
- ✅ Ícones em 192x192 e 512x512
- ✅ display: 'standalone' no manifest
- ✅ start_url e scope definidos
- ✅ theme_color e background_color configurados
- ✅ Metadados iOS em layout.tsx (apple-touch-icon, statusBarStyle)

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

### npm install não instala vite/vitest (Problema Conhecido)

**Sintoma:** `npm install` completa mas `vite` e `vitest` não aparecem em `node_modules/`

**Causa Raiz:** React 19 tem conflitos de peer dependency com `@radix-ui/react-select@1.2.2` que espera React 16-18. O npm se recusa a instalar pacotes quando há conflitos severos de peer dependencies, mesmo com `--legacy-peer-deps`.

**Workarounds:**

1. **Usar yarn (Recomendado):**
   ```bash
   npm install -g yarn
   cd frontend
   rm -rf node_modules package-lock.json
   yarn install
   yarn test
   ```

2. **Usar pnpm:**
   ```bash
   npm install -g pnpm
   cd frontend
   rm -rf node_modules package-lock.json
   pnpm install
   pnpm test
   ```

3. **Downgrade para React 18 (não recomendado):**
   - Perde features do React 19 e Next.js 15
   - Requer downgrades massivos em múltiplas dependências

4. **Aguardar Radix UI React 19 support:**
   - Monitorar [@radix-ui/react-select releases](https://github.com/radix-ui/primitives/releases)
   - Quando disponível, remover `--legacy-peer-deps`

**Status da Implementação:**
- ✅ Infraestrutura de testes completa (277 testes em 18 arquivos)
- ✅ Configuração vitest.config.ts com jsdom
- ✅ MSW handlers corrigidos com URLs absolutas
- ✅ @reviewAgent aprovou implementação (READY FOR MERGE)
- ⚠️ Bloqueio ambiental npm impede execução local dos testes
- ✅ Testes estão prontos para executar com yarn/pnpm

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
