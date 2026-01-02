from app.extensions import db
from .base import BaseModel
from .tenant_mixin import TenantMixin

class Block(BaseModel, TenantMixin):
    __tablename__ = "blocks"

    section_id = db.Column(db.String(36), db.ForeignKey("sections.id"), nullable=False)
    type = db.Column(db.String(100), nullable=False)  # text, image, video, button
    order = db.Column(db.Integer, nullabe=False, default=0)
    content = db.Column(db.JSON, default=dict) # JSON for text/button data
    media_url = db.Column(db.String(512), nullable=True) # URL for images/videos if applicable

    # Relationship to parent Section
    section = db.relationship("Section", back_populates="blocks")

    __table_args__ = (
        db.UniqueConstraint("section_id", "order", name="uq_section_block_order"),
        db.Index("idx_block_section_order", "section_id", "order"),
    )

