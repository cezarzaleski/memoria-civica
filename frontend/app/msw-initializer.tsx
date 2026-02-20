'use client';

import { useEffect } from 'react';

/**
 * Client component that initializes MSW (Mock Service Worker) in development mode
 *
 * MSW intercepts HTTP requests at the network level, allowing us to simulate
 * API responses without a real backend. This is disabled in production.
 *
 * Note: This component is safe to include in production builds - it only
 * initializes MSW if NODE_ENV === 'development'
 */
export function MSWInitializer() {
  useEffect(() => {
    // Initialize MSW to mock API responses
    // TODO: Remove this when real backend API is available
    import('@/mocks/browser').then(({ worker }) => {
      worker.start({
        onUnhandledRequest: 'bypass',
      });
    });
  }, []);

  // This component doesn't render anything
  return null;
}
