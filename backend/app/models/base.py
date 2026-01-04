import uuid
from datetime import datetime, timezone
from app.extensions import db

local_time_now = datetime.now(timezone.utc).astimezone()

class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    created_at = db.Column(db.DateTime, default=local_time_now, index=True)
    updated_at = db.Column(db.DateTime, default=local_time_now, onupdate=local_time_now, index=True)