# app/utils/pagination.py
from __future__ import annotations

from datetime import datetime
from typing import Optional, Tuple, TypedDict, Type, Any

from sqlalchemy.orm import Query
from sqlalchemy.sql import or_, and_
from werkzeug.exceptions import BadRequest


class CursorMeta(TypedDict):
    """
    Strongly-typed cursor pagination metadata.

    Explicit keys prevent contract drift across list_* endpoints.
    """
    has_more: bool
    next_cursor: Optional[str]
    prev_cursor: Optional[str]


def encode_cursor(created_at: datetime, row_id: Any) -> str:
    """
    Encode a cursor using a stable, deterministic sort key.

    Format: ISO8601|<id>

    Notes:
    - Human-readable for debugging/admin tooling
    - Assumes created_at is timezone-consistent across rows
    """
    if not isinstance(created_at, datetime) or row_id is None:
        raise ValueError("created_at and row_id are required to encode cursor")

    return f"{created_at.isoformat()}|{row_id}"


def decode_cursor(cursor: str) -> Tuple[datetime, str]:
    """
    Decode a cursor into (created_at, id).

    Raises:
    - BadRequest if cursor format or timestamp is invalid
    """
    if not cursor or "|" not in cursor:
        raise BadRequest("Invalid cursor format")

    try:
        ts_str, row_id = cursor.split("|", 1)
        return datetime.fromisoformat(ts_str), row_id
    except Exception as exc:
        # Ensures clean API error instead of 500
        raise BadRequest("Invalid cursor format") from exc


def apply_cursor(
    query: Query,
    *,
    model: Type[Any],
    cursor: Optional[str],
    direction: str = "next",
) -> Query:
    """
    Apply cursor-based filtering to a SQLAlchemy query.

    Ordering contract (MANDATORY):
      ORDER BY created_at DESC, id DESC

    Direction semantics:
    - next: fetch records *after* the cursor
    - prev: fetch records *before* the cursor

    Required model attributes:
    - created_at
    - id
    """
    if not cursor:
        return query

    cursor_ts, cursor_id = decode_cursor(cursor)

    if direction == "next":
        return query.filter(
            or_(
                model.created_at < cursor_ts,
                and_(
                    model.created_at == cursor_ts,
                    model.id < cursor_id,
                ),
            )
        )

    if direction == "prev":
        return query.filter(
            or_(
                model.created_at > cursor_ts,
                and_(
                    model.created_at == cursor_ts,
                    model.id > cursor_id,
                ),
            )
        )

    raise BadRequest("Invalid pagination direction")


def paginate_cursor(
    query: Query,
    *,
    model: Type[Any],
    limit: int,
    direction: str = "next",
) -> tuple[list[Any], CursorMeta]:
    """
    Execute a cursor-paginated query.

    Strategy:
    - Fetch limit + 1 rows to detect continuation
    - Trim extra row from result set
    - Generate cursors from boundary rows only

    Returns:
    - items: list of ORM objects
    - meta: CursorMeta (has_more, next_cursor, prev_cursor)
    """
    if limit <= 0:
        raise BadRequest("Limit must be greater than zero")

    # Enforce canonical ordering
    ordered_query = query.order_by(
        model.created_at.desc(),
        model.id.desc(),
    )

    rows = ordered_query.limit(limit + 1).all()

    has_more = len(rows) > limit
    items = rows[:limit]

    next_cursor: Optional[str] = None
    prev_cursor: Optional[str] = None

    if items:
        # Cursor for fetching older records
        if direction == "next" and has_more:
            last = items[-1]
            next_cursor = encode_cursor(last.created_at, last.id)

        # Cursor for fetching newer records
        if direction == "prev":
            first = items[0]
            prev_cursor = encode_cursor(first.created_at, first.id)

    return items, {
        "has_more": has_more,
        "next_cursor": next_cursor,
        "prev_cursor": prev_cursor,
    }
