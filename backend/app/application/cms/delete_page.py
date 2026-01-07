from app.extensions import db
from app.models.page import Page
from app.models.section import Section
from app.models.block import Block
from app.utils.audit import log_action
from app.utils.transaction import transactional


def delete_page(
    *,
    tenant_id: int,
    page_id: str,
    actor_id: int,
) -> None:
    """
    Hard-delete a page and all its descendants.

    Notes:
    - Uses soft-delete if your models implement SoftDeleteMixin
    - Blocks → Sections → Page (bottom-up)
    """

    page = Page.query.filter_by(
        id=page_id,
        tenant_id=tenant_id,
    ).first()

    if not page:
        raise ValueError("Page not found")

    with transactional():
        # 🔥 Delete blocks first
        Block.query.filter_by(
            tenant_id=tenant_id,
        ).join(Section).filter(
            Section.page_id == page.id
        ).delete(synchronize_session=False)

        # 🔥 Delete sections
        Section.query.filter_by(
            tenant_id=tenant_id,
            page_id=page.id,
        ).delete(synchronize_session=False)

        # 🔥 Delete page
        db.session.delete(page)

        log_action(
            action="page.delete",
            entity_type="page",
            entity_id=page_id,
            payload={
                "deleted_by": actor_id,
            },
        )
