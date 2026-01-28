import { setupWorker } from 'msw/browser';
import { handlers } from './handlers';

/**
 * Browser-side MSW worker setup for development and testing
 */
export const worker = setupWorker(...handlers);
