from app.extensions import db
from .base import BaseModel
from .tenant_mixin import TenantMixin
from .soft_delete_mixin import SoftDeleteMixin

class Section(BaseModel, TenantMixin, SoftDeleteMixin):
    __tablename__ = "sections"
    
    page_id = db.Column(db.String(36), db.ForeignKey("pages.id"), nullable=False)
    type = db.Column(db.String(100), nullable=False)  # hero, features, gallery
    order = db.Column(db.Integer, nullable=False, default=0)
    settings = db.Column(db.JSON, default=dict)

    # Relationship to parent Page
    page = db.relationship(
        "Page",
        back_populates="sections"
    )

    # Relationship to child Blocks
    blocks = db.relationship(
        "Block",
        back_populates="section",
        order_by="Block.order",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        db.UniqueConstraint("page_id", "order", name="uq_page_section_order"),
        db.Index("idx_section_page_order", "page_id", "order"),
    )
