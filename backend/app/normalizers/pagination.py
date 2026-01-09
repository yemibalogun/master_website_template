# app/normalizers/pagination.py
from typing import Callable, Any, List, Optional, Dict

from app.utils.pagination import CursorMeta


def normalize_pagination(
    items: List[Any],
    normalize_fn: Callable[[Any], Dict[str, Any]],
    *,
    cursor: Optional[CursorMeta] = None,
    page: Optional[int] = None,
    per_page: Optional[int] = None,
    total: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Normalize paginated API responses.

    Supports:
    - Cursor-based pagination (preferred)
    - Offset-based pagination (legacy / admin views)

    Exactly ONE pagination strategy should be used per response.
    """

    # Normalize ORM objects → dicts
    normalized_items = [normalize_fn(item) for item in items]

    response: Dict[str, Any] = {
        "items": normalized_items,
    }

    # -------------------------------
    # Cursor-based pagination
    # -------------------------------
    if cursor is not None:
        response["pagination"] = {
            "has_more": cursor["has_more"],
            "next_cursor": cursor["next_cursor"],
            "prev_cursor": cursor["prev_cursor"],
        }
        return response

    # -------------------------------
    # Offset-based pagination (optional)
    # -------------------------------
    if page is not None and per_page is not None:
        response["pagination"] = {
            "page": page,
            "per_page": per_page,
        }

        if total is not None:
            response["pagination"]["total"] = total
            response["pagination"]["total_pages"] = (
                (total + per_page - 1) // per_page
            )

    return response
