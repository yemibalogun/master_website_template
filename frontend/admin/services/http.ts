import { ApiError } from "./errors"

type HttpMethod = "GET" | "POST" | "PUT" | "DELETE" | "PATCH"

export type TenantRequestOptions = {
  token: string              // ✅ required
  tenantId: string           // ✅ required
  method?: HttpMethod
  body?: unknown
  signal?: AbortSignal
}

/**
 * Tenant-scoped HTTP client.
 * Used AFTER tenant selection.
 */
export async function http<T>(
  path: string,
  options: TenantRequestOptions
): Promise<T> {
  const {
    method = "GET",
    body,
    token,
    tenantId,
    signal,
  } = options

  const res = await fetch(
    `${process.env.NEXT_PUBLIC_API_BASE_URL}${path}`,
    {
      method,
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
        "X-Tenant-ID": tenantId,
      },
      body: body ? JSON.stringify(body) : undefined,
      signal,
    }
  )

  let payload: unknown = null

  try {
    payload = await res.json()
  } catch {
    // 204 / empty body
  }

  if (!res.ok) {
    throw new ApiError(
      (payload as { message?: string })?.message || "HTTP Error",
      res.status,
      payload
    )
  }

  return payload as T
}
