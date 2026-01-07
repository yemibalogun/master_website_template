# app/utils/pagination.py
from __future__ import annotations

from datetime import datetime
from typing import Optional, Tuple
from sqlalchemy.sql import or_, and_
from werkzeug.exceptions import BadRequest


def encode_cursor(created_at: datetime, row_id: str) -> str:
    """
    Encodes a cursor from a stable sort key.
    Format: ISO8601|<id>

    Kept human-readable for debugging and admin tooling.
    """
    if not created_at or not row_id:
        raise ValueError("Cannot encode cursor without created_at and id")

    return f"{created_at.isoformat()}|{row_id}"


def decode_cursor(cursor: str) -> Tuple[datetime, str]:
    """
    Decodes cursor into (created_at, id).

    Raises BadRequest for invalid formats to surface clean API errors.
    """
    try:
        ts_str, row_id = cursor.split("|", 1)
        return datetime.fromisoformat(ts_str), row_id
    except Exception as exc:
        raise BadRequest("Invalid cursor format") from exc

def apply_cursor(
    query,
    model,
    cursor: Optional[str],
):
    """
    Applies cursor-based pagination filtering.

    Ordering assumption:
      ORDER BY created_at DESC, id DESC

    Requires model to expose:
      - created_at
      - id
    """
    if not cursor:
        return query

    cursor_ts, cursor_id = decode_cursor(cursor)

    return query.filter(
        or_(
            model.created_at < cursor_ts,
            and_(
                model.created_at == cursor_ts,
                model.id < cursor_id,
            ),
        )
    )

def paginate_cursor(
    query,
    model,
    limit: int,
):
    """
    Executes a cursor-paginated query.

    Returns:
      (items, meta)

    Meta includes:
      - has_more
      - next_cursor
    """
    if limit <= 0:
        raise BadRequest("Limit must be greater than zero")

    rows = (
        query
        .order_by(model.created_at.desc(), model.id.desc())
        .limit(limit + 1)  # Fetch one extra row
        .all()
    )

    has_more = len(rows) > limit
    items = rows[:limit]

    next_cursor = None
    if has_more:
        if not items:
            return items, {
                "has_more": False,
                "next_cursor": None,
            }

        last = items[-1]
        next_cursor = encode_cursor(last.created_at, last.id)

    return items, {
        "has_more": has_more,
        "next_cursor": next_cursor,
    }
