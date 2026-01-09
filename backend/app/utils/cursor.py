# app/utils/cursor.py
from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, Optional, Tuple
from flask import request
from sqlalchemy.sql import and_, or_

def parse_cursor(raw: Optional[Dict[str, Any]]) -> Optional[Tuple[datetime, int]]:
    """
    Parse and validate cursor payload.

    Cursor shape:
    {
        "created_at": ISO8601 string,
        "id": int
    }
    """
    if not raw:
        return None

    try:
        created_at = datetime.fromisoformat(raw["created_at"])
        entity_id = int(raw["id"])
        return created_at, entity_id
    except (KeyError, TypeError, ValueError):
        raise ValueError("Invalid cursor format")


def apply_cursor_filter(
    query,
    *,
    cursor: Tuple[datetime, int],
    model,
    direction: str,
):
    """
    Apply cursor filtering to a SQLAlchemy query.

    direction:
    - "next": fetch records AFTER cursor
    - "prev": fetch records BEFORE cursor
    """
    created_at, entity_id = cursor

    if direction == "next":
        return query.filter(
            or_(
                model.created_at > created_at,
                and_(
                    model.created_at == created_at,
                    model.id > entity_id,
                ),
            )
        )

    if direction == "prev":
        return query.filter(
            or_(
                model.created_at < created_at,
                and_(
                    model.created_at == created_at,
                    model.id < entity_id,
                ),
            )
        )

    raise ValueError("Invalid cursor direction")
