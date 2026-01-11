"use server"

import { cookies } from "next/headers"
import { redirect } from "next/navigation"

/**
 * Persists tenant context and redirects.
 */
export async function selectTenant(tenantId: string): Promise<never> {
  if (!tenantId || typeof tenantId !== "string") {
    throw new Error("Invalid tenant id")
  }

  const cookieStore = await cookies()

  // Persist tenant for middleware + backend propagation
  cookieStore.set("tenant_id", tenantId, {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
  })

  // Redirect to admin root (or dashboard)
  redirect("/admin")
}
