from app.extensions import db
from .base import BaseModel
from .tenant_mixin import TenantMixin
from .soft_delete_mixin import SoftDeleteMixin

class Page(BaseModel, TenantMixin, SoftDeleteMixin):
    __tablename__ = 'pages'

    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), nullable=False, index=True)
    status = db.Column(db.String(50), default='draft', index=True)
    seo = db.Column(db.JSON(none_as_null=True), default=dict)

    __table_args__ = (
        db.UniqueConstraint("tenant_id", "slug", name="uq_page_slug_per_tenant"),
    )

    # Relationship to Sections (ordered, cascade deletes)
    sections = db.relationship(
        "Section",
        back_populates="page",
        order_by="Section.order",
        cascade="all, delete-orphan"
    )