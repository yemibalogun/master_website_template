import { ApiError } from "./errors"

type HttpMethod = "GET" | "POST" | "PUT" | "DELETE" | "PATCH"

export type GlobalRequestOptions = {
  token?: string            // optional (login won’t have one)
  method?: HttpMethod
  body?: unknown
  signal?: AbortSignal
}

/**
 * Global (non-tenant) HTTP client.
 * Used for auth, tenant discovery, etc.
 */
export async function httpGlobal<T>(
  path: string,
  options: GlobalRequestOptions = {}
): Promise<T> {
  const {
    method = "GET",
    body,
    token,
    signal,
  } = options

  const headers: HeadersInit = {
    "Content-Type": "application/json",
  }

  if (token) {
    headers["Authorization"] = `Bearer ${token}`
  }

  const res = await fetch(
    `${process.env.NEXT_PUBLIC_API_BASE_URL}${path}`,
    {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
      signal,
    }
  )

  let payload: unknown = null

  try {
    payload = await res.json()
  } catch {}

  if (!res.ok) {
    throw new ApiError(
      (payload as { message?: string })?.message || "HTTP Error",
      res.status,
      payload
    )
  }

  return payload as T
}
