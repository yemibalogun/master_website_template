"use client"

import { useTransition } from "react"
import { selectTenant } from "@/app/actions/select-tenant"

export type Tenant = {
    id: string
    name: string
}

type Props = {
    tenants: Tenant[]
    currentTenantId?: string
}

export function TenantSwitcher({ tenants }: Props) {
    const [isPending, startTransition] = useTransition()

    function handleSelect(tenantId: string): void {
        if (!tenantId) return
        
        startTransition(() => {
            // Server Action invocation
            selectTenant(tenantId)
        })
    }

    if (tenants.length === 0) {
        return <p>No tenants available.</p>
    }

    return (
        <ul>
            {tenants.map((tenant) => (
                <li key={tenant.id}>
                    <button
                        type="button"
                        disabled={isPending}
                        onClick={() => handleSelect(tenant.id)}
                    >
                        {tenant.name}
                    </button>
                </li>
            ))}
        </ul>
    )
}