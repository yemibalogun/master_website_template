from typing import Any, Dict
from app.extensions import db
from app.models.page import Page
from app.domain.invariants.page import assert_page
from app.utils.audit import log_action
from app.utils.transaction import transactional


ALLOWED_UPDATE_FIELDS = {"title", "slug", "meta", "status"}


def update_page(
    *,
    tenant_id: int,
    page_id: int,
    actor_id: int,
    data: Dict[str, Any],
) -> Page:
    """
    Update mutable fields on a page.

    Design rules:
    - Only whitelisted fields are mutable
    - No silent no-op updates
    - Invariants always revalidated
    """

    page = Page.query.filter_by(
        id=page_id,
        tenant_id=tenant_id,
    ).first()

    if not page:
        raise ValueError("Page not found")

    changed_fields: list[str] = []

    with transactional():
        for field in ALLOWED_UPDATE_FIELDS:
            if field in data and getattr(page, field) != data[field]:
                setattr(page, field, data[field])
                changed_fields.append(field)

        if not changed_fields:
            # Explicitly fail instead of silently succeeding
            raise ValueError("No valid fields provided for update")

        page.updated_by = actor_id

        # 🔒 Domain invariant enforcement
        assert_page(page)

        log_action(
            action="page.update",
            entity_type="page",
            entity_id=page.id,
            payload={
                "fields": changed_fields,
            },
        )

    return page
