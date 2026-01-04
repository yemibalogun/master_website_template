from datetime import datetime, timezone
from app.extensions import db
from .base import BaseModel

class Tenant(BaseModel):
    __tablename__ = "tenants"

    # Basic info
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=True)

    # Feature toggles (modern SaaS)
    enable_ecommerce = db.Column(db.Boolean, default=False)
    enable_bookings = db.Column(db.Boolean, default=False)
    enable_cms = db.Column(db.Boolean, default=True)
    enable_roles = db.Column(db.Boolean, default=True)
    enable_sso = db.Column(db.Boolean, default=False)
    enable_2fa = db.Column(db.Boolean, default=True)
    enable_blog = db.Column(db.Boolean, default=True)
    enable_newsletter = db.Column(db.Boolean, default=False)
    enable_seo_tools = db.Column(db.Boolean, default=True)
    enable_analytics = db.Column(db.Boolean, default=True)
    enable_subscriptions = db.Column(db.Boolean, default=False)
    enable_coupons = db.Column(db.Boolean, default=False)
    enable_inventory = db.Column(db.Boolean, default=True)
    enable_shipping = db.Column(db.Boolean, default=False)
    enable_calendar_sync = db.Column(db.Boolean, default=False)
    enable_appointments = db.Column(db.Boolean, default=True)
    enable_notifications = db.Column(db.Boolean, default=True)
    enable_ai_assistant = db.Column(db.Boolean, default=False)
    enable_multilingual = db.Column(db.Boolean, default=True)
    enable_api_access = db.Column(db.Boolean, default=False)

    # JSON field for future toggles (flexible)
    features = db.Column(db.JSON, default=dict)

    # Timestamps (timezone-aware)
    created_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    def has_feature(self, feature_name: str) -> bool:
        """
        Check if a feature is enabled for this tenant.
        """
        # Check JSON overrides first
        if self.features.get(feature_name) is not None:
            return self.features.get(feature_name)

        # Fallback to attribute toggles
        attr_name = f"enable_{feature_name}"
        return getattr(self, attr_name, False)
