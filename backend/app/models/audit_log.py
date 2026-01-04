# app/models/audit_log.py
from app.extensions import db
from .base import BaseModel
from .tenant_mixin import TenantMixin
from sqlalchemy import event 



class AuditLog(BaseModel, TenantMixin):
    __tablename__ = "audit_logs"

    __table_args__ = (
        db.Index("ix_audit_cursor", "tenant_id", "created_at", "id"),
        db.Index("ix_audit_actor_action", "tenant_id", "actor_id", "action"),
    )

    actor_id = db.Column(db.String(36), nullable=False, index=True)
    action = db.Column(db.String(50), nullable=False, index=True)

    entity_type = db.Column(db.String(50), nullable=False, index=True)
    entity_id = db.Column(db.String(36), nullable=False, index=True)

    payload = db.Column(db.JSON, nullable=False, default=dict)  # ✅ renamed

    def to_dict(self):
        return {
            "id": self.id,
            "actor_id": self.actor_id,
            "action": self.action,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "payload": self.payload,
            "created_at": self.created_at.isoformat()
        }
    
@event.listens_for(AuditLog, 'before_update')
@event.listens_for(AuditLog, 'before_delete')
def prevent_audit_mutation(mapper, connection, target):
    raise RuntimeError("Audit logs are immutable")