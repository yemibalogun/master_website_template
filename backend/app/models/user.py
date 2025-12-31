from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from .base import BaseModel
from .tenant_mixin import TenantMixin

class User(BaseModel, TenantMixin):
    __tablename__ = 'users'

    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    role = db.Column(db.String(50), nullable=False, default='user')
    is_active = db.Column(db.Boolean, default=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

