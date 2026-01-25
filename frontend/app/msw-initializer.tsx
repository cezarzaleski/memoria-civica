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
    // Only initialize MSW in development mode
    if (process.env.NODE_ENV === 'development') {
      // Dynamically import MSW worker to avoid bundling it in production
      import('@/mocks/browser').then(({ worker }) => {
        // Start the MSW worker
        // This will begin intercepting all fetch requests matching our handlers
        worker.start({
          onUnhandledRequest: 'warn', // Log warnings for unhandled requests
        });
      });
    }
  }, []);

  // This component doesn't render anything
  return null;
}
