from typing import Dict, List
from app.extensions import db
from app.models.page import Page
from app.domain.invariants.page import assert_page
from app.utils.transaction import transactional
from app.utils.audit import log_action

ALLOWED_ACTIONS = {"publish", "unpublish"}

def bulk_publish_pages(
    *,
    tenant_id: str,
    page_ids: List[int],
    action: str,
    actor_id: str,
) -> Dict[str, int | str]:  # ✅ allow int or str

    """
    Bulk publish or unpublish pages.

    Responsibilities:
    - Transactional update
    - Enforce invariants on publish
    - Audit logging
    """
    if action not in ALLOWED_ACTIONS:
        raise ValueError(f"Invalid action: {action}")

    pages = (
        Page.query
        .filter(
            Page.id.in_(page_ids),
            Page.tenant_id == tenant_id,
            Page.deleted_at.is_(None)  # type: ignore
        )
        .all()
    )

    with transactional():
        for page in pages:
            if action == "publish":
                page.status = "published"
                assert_page(page, publish=True)  # enforce publish invariant
            else:
                page.status = "draft"

        # Audit once per batch
        log_action(
            action=f"page.bulk_{action}",
            entity_type="page",
            entity_id="*",
            payload={"count": len(pages), "actor_id": actor_id},
        )

    return {"count": len(pages), "action": action}
