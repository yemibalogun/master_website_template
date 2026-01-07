from typing import Any, Dict
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.models.page import Page
from app.domain.invariants.page import assert_page
from app.utils.audit import log_action
from app.utils.transaction import transactional


def create_page(
    *,
    tenant_id: int,
    actor_id: int,
    data: Dict[str, Any],
) -> Page:
    """
    Create a new CMS page in DRAFT state.

    Edge cases handled:
    - Missing required fields
    - Duplicate slug per tenant
    - Invariant violations
    """

    title: str | None = data.get("title")
    slug: str | None = data.get("slug")

    if not title or not slug:
        raise ValueError("Both title and slug are required")

    page = Page()
    page.tenant_id=tenant_id
    page.title=title
    page.slug=slug
    page.status="draft"
    try:
        with transactional():
            db.session.add(page)
            db.session.flush()  # ensures page.id is available

            # 🔒 Domain invariants (single source of truth)
            assert_page(page)

            log_action(
                action="page.create",
                entity_type="page",
                entity_id=page.id,
                payload={
                    "title": page.title,
                    "slug": page.slug,
                    "status": page.status,
                },
            )

        return page

    except IntegrityError as exc:
        # Typically raised by unique constraints (e.g., tenant_id + slug)
        db.session.rollback()
        raise ValueError("A page with this slug already exists") from exc
