// admin/context/TenantContext.tsx
"use client"

import { createContext, useContext, ReactNode } from "react"

type TenantContextType = {
  tenantId: string
}

const TenantContext = createContext<TenantContextType | undefined>(undefined)

type ProviderProps = {
  tenantId: string
  children: ReactNode
}

export function TenantProvider({ tenantId, children }: ProviderProps) {
  return (
    <TenantContext.Provider value={{ tenantId }}>
      {children}
    </TenantContext.Provider>
  )
}

export function useTenant(): TenantContextType {
  const ctx = useContext(TenantContext)

  if (!ctx) {
    throw new Error("useTenant must be used within TenantProvider")
  }

  return ctx
}
