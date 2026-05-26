export type ApiError = {
  status: number
  message: string
}

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8010'

function normalizeErrorMessage(payload: unknown, status: number): string {
  if (
    typeof payload === 'object' &&
    payload !== null &&
    'detail' in payload &&
    typeof payload.detail === 'string'
  ) {
    return payload.detail
  }

  if (
    typeof payload === 'object' &&
    payload !== null &&
    'detail' in payload &&
    Array.isArray(payload.detail) &&
    payload.detail.length > 0
  ) {
    const firstDetail = payload.detail[0]
    if (
      typeof firstDetail === 'object' &&
      firstDetail !== null &&
      'msg' in firstDetail &&
      typeof firstDetail.msg === 'string'
    ) {
      return firstDetail.msg
    }
  }

  return `リクエストに失敗しました（ステータス: ${status}）`
}

export async function apiRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
    ...init,
  })

  if (!response.ok) {
    let payload: unknown = null
    try {
      payload = await response.json()
    } catch {
      payload = null
    }

    throw {
      status: response.status,
      message: normalizeErrorMessage(payload, response.status),
    } satisfies ApiError
  }

  return (await response.json()) as T
}

export function toErrorMessage(error: unknown, fallback: string): string {
  if (
    typeof error === 'object' &&
    error !== null &&
    'message' in error &&
    typeof error.message === 'string'
  ) {
    return error.message
  }

  return fallback
}
