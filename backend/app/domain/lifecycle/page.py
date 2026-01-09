from typing import Set

# Explicit allowed state transitions
ALLOWED_PAGE_TRANSITIONS: dict[str, Set[str]] = {
    "draft": {"published"},
    "published": set(),  # published → draft ONLY via rollback
}

def assert_page_transition(*, from_status: str, to_status: str) -> None:
    """
    Guards page lifecycle transitions.
    Single source of truth for status changes.
    """
    allowed = ALLOWED_PAGE_TRANSITIONS.get(from_status, set())

    if to_status not in allowed:
        raise ValueError(
            f"Illegal page transition: {from_status} → {to_status}"
        )
