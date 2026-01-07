# app/application/cms/unpublish_page.py
from datetime import datetime, timezone
from app.extensions import db
from app.models.page import Page
from app.utils.transaction import transactional
from app.utils.audit import log_action

def unpublish_page(*, tenant_id: str, page_id: str, actor_id: str) -> None:
    """
    Marks a page as unpublished.
    """
    page = Page.query.filter_by(id=page_id, tenant_id=tenant_id, deleted_at=None).first_or_404()

    with transactional():
        page.status = "draft"
        page.updated_at = datetime.now(timezone.utc).astimezone()
        page.updated_by = actor_id
        db.session.add(page)

        log_action(
            action="page.unpublish",
            entity_type="page",
            entity_id=page.id,
            payload={"actor_id": actor_id}
        )
