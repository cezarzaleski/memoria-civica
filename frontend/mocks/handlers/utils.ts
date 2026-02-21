import { HttpResponse } from 'msw';
import type { PaginatedResponse } from '@/lib/types';

const DEFAULT_PAGE = 1;
const DEFAULT_PER_PAGE = 20;

export function parsePositiveInteger(value: string | null, fallback: number): number {
  const parsedValue = Number.parseInt(value ?? '', 10);
  return Number.isInteger(parsedValue) && parsedValue > 0 ? parsedValue : fallback;
}

export function parseStrictId(value: string | undefined | null): number | null {
  if (!value || !/^\d+$/.test(value)) {
    return null;
  }

  const parsedValue = Number(value);
  return Number.isSafeInteger(parsedValue) && parsedValue > 0 ? parsedValue : null;
}

export function getPaginationParams(url: URL): { page: number; perPage: number } {
  return {
    page: parsePositiveInteger(url.searchParams.get('page'), DEFAULT_PAGE),
    perPage: parsePositiveInteger(url.searchParams.get('per_page'), DEFAULT_PER_PAGE),
  };
}

export function createPaginatedResponse<T>(items: T[], page: number, perPage: number): PaginatedResponse<T> {
  const startIndex = (page - 1) * perPage;

  return {
    data: items.slice(startIndex, startIndex + perPage),
    pagination: {
      page,
      per_page: perPage,
      total: items.length,
    },
  };
}

export function validationError(message: string) {
  return HttpResponse.json(
    {
      error: {
        code: 'VALIDATION_ERROR',
        message,
      },
    },
    { status: 400 }
  );
}

export function notFoundError(message: string) {
  return HttpResponse.json(
    {
      error: {
        code: 'NOT_FOUND',
        message,
      },
    },
    { status: 404 }
  );
}
