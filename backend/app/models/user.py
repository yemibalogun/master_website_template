from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from .base import BaseModel
from .tenant_mixin import TenantMixin

class User(BaseModel, TenantMixin):
    __tablename__ = 'users'

    email = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    last_login_at = db.Column(db.DateTime)

    role = db.Column(db.String(50), nullable=False, default='user')
    is_active = db.Column(db.Boolean, default=True)

    __table_args__ = (
        db.UniqueConstraint(
            'tenant_id', 'email', 
            name='uq_user_email_per_tenant'
        ),
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

