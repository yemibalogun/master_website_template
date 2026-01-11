import { httpGlobal } from "./http.global"

export type Tenant = {
  id: string
  name: string
}

export async function fetchTenants(
  params: { token: string }
): Promise<Tenant[]> {
  return httpGlobal<Tenant[]>("/v1/tenants", {
    method: "GET",
    token: params.token,
  })
}
