from app.extensions import db

class TenantMixin:
    tenant_id = db.Column(
        db.String(36),
        db.ForeignKey('tenant.id'),
        nullable=False,
        index=True
    )