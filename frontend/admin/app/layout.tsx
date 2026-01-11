// admin/app/layout.tsx
import { cookies } from "next/headers"
import { redirect } from "next/navigation"
import { TenantProvider } from "@/context/TenantContext"

export default async function AdminLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const cookieStore = await cookies()
  const tenantId = cookieStore.get("tenant_id")?.value

  if (!tenantId) {
    // Middleware should prevent this, but we harden anyway
    redirect("/admin/select-tenant")
  }

  return (
    <html lang="en">
      <body>
        <TenantProvider tenantId={tenantId}>
          {children}
        </TenantProvider>
      </body>
    </html>
  )
}
