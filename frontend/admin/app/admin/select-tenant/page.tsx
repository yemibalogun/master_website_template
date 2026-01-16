import { cookies } from "next/headers"
import { redirect } from "next/navigation"
import { TenantSwitcher } from "@/components/TenantSwitcher"
import { fetchTenants } from "@/services/tenants"
import { selectTenant } from "@/app/actions/select-tenant"

export default async function SelectTenantPage() {
  const cookieStore = await cookies()
  const token = cookieStore.get("access_token")?.value

  if (!token) {
    redirect("/admin/login")
  }

  const tenants = await fetchTenants({ token })

  // ✅ AUTO-SELECT when only one tenant exists
  if (tenants.length === 1) {
    await selectTenant(tenants[0].id)
  }

  return (
    <main>
      <h1>Select a tenant</h1>
      <TenantSwitcher tenants={tenants} />
    </main>
  )
}
