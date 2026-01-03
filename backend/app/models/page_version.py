from app.extensions import db
from .base import BaseModel
from .tenant_mixin import TenantMixin

class PageVersion(BaseModel, TenantMixin):
    __tablename__ = "page_versions"

    page_id = db.Column(
        db.String(36),
        db.ForeignKey("pages.id"),
        nullable=False
    )

    version = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False)  
    # draft | published | archived | rollback

    snapshot = db.Column(db.JSON, nullable=False)

    created_by = db.Column(db.String(36), nullable=True)

    __table_args__ = (
        db.UniqueConstraint("page_id", "version", name="uq_page_version"),
        db.Index("idx_page_version_page", "page_id"),
    )
