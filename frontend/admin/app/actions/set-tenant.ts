"use server"

import { cookies } from "next/headers"
import { redirect } from "next/navigation"

/**
 * Sets the active tenant in an HttpOnly cookie.
 * Runs ONLY on the server.
 */

export async function setTenant(
    tenantId: string,
    nextPath: string = "/admin"
): Promise<never> {
    if (!tenantId) {
        throw new Error("tenantId is required")
    }

    const cookieStore = await cookies()

    cookieStore.set("tenant_id", tenantId, {
        httpOnly: true,
        sameSite: "lax",
        secure: process.env.NODE_ENV === "production",
        path: "/",
    })

    // Hard redirect to ensure middleware re-runs
    redirect(nextPath)
}