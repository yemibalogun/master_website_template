from app.extensions import db
from .base import BaseModel
from .tenant_mixin import TenantMixin

class Block(BaseModel, TenantMixin):
    __tablename__ = "blocks"

    section_id = db.Column(db.String(36), db.ForeignKey("sections.id"), nullable=False)
    type = db.Column(db.String(100), nullable=False)  # text, image, video, button
    order = db.Column(db.Integer, default=0)
    content = db.Column(db.JSON, default={}) # JSON for text/button data
    media_url = db.Column(db.String(512), nullable=True) # URL for images/videos if applicable
