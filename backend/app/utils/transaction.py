from contextlib import contextmanager
from app.extensions import db

@contextmanager
def transactional():
    """Context manager for database transactions."""
    try:
        yield
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise