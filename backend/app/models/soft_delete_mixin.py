# app/models/soft_delete_mixin.py
from app.extensions import db
from datetime import datetime, timezone

local_time_now = datetime.now(timezone.utc).astimezone()

class SoftDeleteMixin:
    deleted_at = db.Column(db.DateTime, nullable=True)

    def soft_delete(self):
        self.deleted_at = local_time_now

    @property
    def is_deleted(self):
        return self.deleted_at is not None
