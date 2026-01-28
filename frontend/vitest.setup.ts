import '@testing-library/jest-dom';
import { server } from '@/mocks/server';
import { beforeAll, afterEach, afterAll, vi } from 'vitest';

// React 19 compatibility: Tell React this environment supports act()
// This is required for React 19 to properly enable act() in the test environment
// Combined with NODE_ENV='test' in vitest.config.ts, this ensures React.act is available
globalThis.IS_REACT_ACT_ENVIRONMENT = true;

// Start MSW server before tests
beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));

// Reset handlers after each test
afterEach(() => server.resetHandlers());

// Clean up after all tests
afterAll(() => server.close());

// Mock Next.js router
vi.mock('next/router', () => ({
  useRouter: () => ({
    push: vi.fn(),
    pathname: '/',
    query: {},
    asPath: '/',
  }),
}));

// Mock window.matchMedia (only in jsdom environment)
if (typeof window !== 'undefined') {
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: vi.fn().mockImplementation((query) => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  });
}

// Mock PointerEvent for Radix UI Select components
// Radix UI uses PointerEvent which is not fully supported in jsdom
class MockPointerEvent extends Event {
  button: number;
  ctrlKey: boolean;
  pointerType: string;

  constructor(type: string, props: PointerEventInit = {}) {
    super(type, props);
    this.button = props.button ?? 0;
    this.ctrlKey = props.ctrlKey ?? false;
    this.pointerType = props.pointerType ?? 'mouse';
  }
}

if (!global.PointerEvent) {
  global.PointerEvent = MockPointerEvent as any;
  if (typeof global.window !== 'undefined') {
    global.window.PointerEvent = MockPointerEvent as any;
  }
}

// Mock HTMLElement methods required by Radix UI (only in jsdom environment)
if (typeof window !== 'undefined' && window.HTMLElement) {
  Object.assign(window.HTMLElement.prototype, {
    scrollIntoView: vi.fn(),
    releasePointerCapture: vi.fn(),
    hasPointerCapture: vi.fn(),
    setPointerCapture: vi.fn(),
  });
}
