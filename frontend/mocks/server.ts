import { setupServer } from 'msw/node';
import { handlers } from './handlers';

/**
 * Server-side MSW setup for testing
 */
export const server = setupServer(...handlers);
