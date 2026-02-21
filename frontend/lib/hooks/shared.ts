import type { PaginationMeta } from '@/lib/types'

type QueryValue = string | number | boolean | null | undefined

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null
}

export function buildEndpoint(path: string, params: Record<string, QueryValue> = {}): string {
  const searchParams = new URLSearchParams()

  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null || value === '') {
      return
    }

    searchParams.append(key, String(value))
  })

  const queryString = searchParams.toString()
  return queryString ? `${path}?${queryString}` : path
}

export function parsePaginatedPayload<T>(payload: unknown): {
  data: T[]
  pagination: PaginationMeta | null
} {
  if (!isRecord(payload)) {
    return { data: [], pagination: null }
  }

  const data = Array.isArray(payload.data) ? (payload.data as T[]) : []
  const paginationCandidate = payload.pagination

  if (!isRecord(paginationCandidate)) {
    return { data, pagination: null }
  }

  const page = Number(paginationCandidate.page)
  const perPage = Number(paginationCandidate.per_page)
  const total = Number(paginationCandidate.total)

  if (!Number.isFinite(page) || !Number.isFinite(perPage) || !Number.isFinite(total)) {
    return { data, pagination: null }
  }

  return {
    data,
    pagination: {
      page,
      per_page: perPage,
      total,
    },
  }
}

export function parseSinglePayload<T>(payload: unknown): T | null {
  if (!isRecord(payload) || !('data' in payload)) {
    return null
  }

  return payload.data as T
}

export async function readErrorMessage(response: Response, fallbackPrefix: string): Promise<string> {
  const fallbackMessage = `${fallbackPrefix}: ${response.status}`

  try {
    const payload = (await response.clone().json()) as unknown

    if (!isRecord(payload) || !isRecord(payload.error)) {
      return fallbackMessage
    }

    const message = payload.error.message

    if (typeof message === 'string' && message.trim().length > 0) {
      return message
    }
  } catch {
    return fallbackMessage
  }

  return fallbackMessage
}
