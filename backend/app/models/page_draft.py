from app.extensions import db
from .base import BaseModel
from .tenant_mixin import TenantMixin
from .soft_delete_mixin import SoftDeleteMixin


class PageDraft(BaseModel, TenantMixin):
    __tablename__ = "page_drafts"

    page_id = db.Column(db.String(36), db.ForeignKey("pages.id"), nullable=False)
    snapshot = db.Column(db.JSON, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    updated_by = db.Column(db.String(36), nullable=False)
