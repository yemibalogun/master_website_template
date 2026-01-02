from app.extensions import db
from .base import BaseModel
from .tenant_mixin import TenantMixin

class Page(BaseModel, TenantMixin):
    __tablename__ = 'pages'

    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(50), default='draft')
    seo = db.Column(db.JSON, default={})

    __table_args__ = (
        db.UniqueConstraint("tenant_id", "slug", nam_e="uq_page_slug_per_tenant"),
    )

    # Relationship to Sections (ordered, cascade deletes)
    sections = db.relationship(
        "Section",
        back_populates="page",
        order_by="Section.order",
        cascade="all, delete-orphan"
    )