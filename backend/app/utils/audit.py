from flask import g
from app.extensions import db
from app.models.audit_log import AuditLog
from typing import Optional

def log_action(
    *,
    action: str,
    entity_type: str,
    entity_id: Optional[str],
    payload: dict | None = None
):
    if not hasattr(g, "current_tenant") or not hasattr(g, "current_user"):
        return  # Skip logging if user or tenant context is missing
    log = AuditLog()

    log.actor_id = getattr(g, "current_user", None) and g.current_user.id
    log.tenant_id = g.current_tenant.id
    log.action = action
    log.entity_type = entity_type
    log.entity_id = entity_id
    log.payload = payload or {}

    db.session.add(log)
