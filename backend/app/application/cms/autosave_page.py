from datetime import datetime, timezone
from app.extensions import db
from app.models.page import Page
from app.models.page_draft import PageDraft
from app.utils.transaction import transactional
from app.utils.versioning import snapshot_page
from app.utils.audit import log_action


def autosave_page(
    *,
    tenant_id: str,
    page_id: str,
    actor_id: str,
) -> None:
    """
    Autosave a draft of a page.

    Responsibilities:
    - Create or update a PageDraft record
    - Record timestamp and user
    - Audit logging
    """
    page: Page = (
        Page.query
        .filter_by(id=page_id, tenant_id=tenant_id, deleted_at=None)
        .first_or_404()
    )

    snapshot = snapshot_page(page)

    draft = PageDraft.query.filter_by(
        page_id=page.id,
        tenant_id=tenant_id
    ).first()

    with transactional():
        if not draft:
            draft = PageDraft()
            draft.page_id = page.id
            draft.tenant_id = tenant_id

        draft.snapshot = snapshot
        draft.updated_at = datetime.now(timezone.utc).astimezone()
        draft.updated_by = actor_id

        db.session.add(draft)

        log_action(
            action="page.autosave",
            entity_type="page",
            entity_id=page.id,
            payload={"actor_id": actor_id}
        )
