export type AuditAction =
  | "create"
  | "update"
  | "publish"
  | "rollback"
  | "delete"

export type AuditEntry = {
  id: string
  entity_type: "page" | "media" | "user"
  entity_id: string
  action: AuditAction
  actor_id: string
  created_at: string
  metadata: Record<string, unknown>
}
