"use server"

import { cookies } from "next/headers"
import { redirect } from "next/navigation"

/**
 * Sets tenant context and redirects atomically.
 */
export async function selectTenant(tenantId: string): Promise<never> {
  if (!tenantId) {
    throw new Error("selectTenant: tenantId is required")
  }

  const cookieStore = await cookies()

  cookieStore.set("tenant_id", tenantId, {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
  })

  redirect("/admin")
}
