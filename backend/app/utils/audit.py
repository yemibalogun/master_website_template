# app/services/audit_logger.py
from app.extensions import db
from app.models.audit_log import AuditLog

def log_action(
    *,
    actor_id: str,
    tenant_id: str,
    action: str,
    entity_type: str,
    entity_id: str,
    payload: dict | None = None
):
    log = AuditLog()

    log.actor_id = actor_id
    log.tenant_id = tenant_id
    log.action = action
    log.entity_type = entity_type
    log.entity_id = entity_id
    log.payload = payload or {}

    db.session.add(log)
