from flask import request, abort
from datetime import timezone
from dateutil.parser import parse


def normalize_ts(ts):
    """
    Ensure datetime is timezone-aware.
    Defaults to UTC if naive.
    """
    if ts.tzinfo is None:
        return ts.replace(tzinfo=timezone.utc)
    return ts


def enforce_optimistic_lock(entity):
    """
    Enforces optimistic locking using the If-Unmodified-Since header.
    Raises 409 Conflict if the entity has been modified since.
    """
    client_ts = request.headers.get("If-Unmodified-Since")
    if not client_ts:
        return  # No optimistic lock requested

    try:
        client_ts = normalize_ts(parse(client_ts))
    except Exception:
        abort(400, description="Invalid If-Unmodified-Since header")

    server_ts = normalize_ts(entity.updated_at)

    if server_ts > client_ts:
        abort(
            409,
            description="Conflict detected. Resource has been modified."
        )
