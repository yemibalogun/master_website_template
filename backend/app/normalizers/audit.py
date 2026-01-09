# app/normalizers/audit.py
from __future__ import annotations

from typing import Dict, Any
from app.models.audit_log import AuditLog


def normalize_audit_log(log: AuditLog) -> Dict[str, Any]:
    """
    Normalizes an AuditLog model into API-safe JSON.

    Notes:
    - entity_id is always serialized as string for consistency
    - payload is assumed to be JSON-serializable
    """

    if not log:
        raise ValueError("AuditLog cannot be None")

    return {
        "id": log.id,
        "tenant_id": log.tenant_id,
        "actor_id": log.actor_id,
        "action": log.action,
        "entity_type": log.entity_type,
        "entity_id": str(log.entity_id) if log.entity_id is not None else None,
        "payload": log.payload or {},
        "created_at": log.created_at.isoformat(),
    }
