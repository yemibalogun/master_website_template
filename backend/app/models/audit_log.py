# app/models/audit_log.py
from app.extensions import db
from .base import BaseModel
from .tenant_mixin import TenantMixin

class AuditLog(BaseModel, TenantMixin):
    __tablename__ = "audit_logs"

    actor_id = db.Column(db.String(36), nullable=False)
    action = db.Column(db.String(50), nullable=False)

    entity_type = db.Column(db.String(50), nullable=False)
    entity_id = db.Column(db.String(36), nullable=False)

    payload = db.Column(db.JSON, default=dict)  # ✅ renamed
