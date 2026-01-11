import { cookies } from "next/headers"
import { TenantSwitcher } from "@/components/TenantSwitcher"
import { fetchTenants } from "@services/tenants"

export default async function SelectTenantPage() {
    const cookieStore = await cookies()
    const token = cookieStore.get("access_token")?.value

    if (!token) {
        throw new Error("Unauthenticated")
    }

    // Backend call: GET /v1/tenants
    const tenants = await fetchTenants({ token })

    return (
        <main>
            <h1>Select a tenant</h1>
            <TenantSwitcher tenants={tenants} />
        </main>
    )
    }
