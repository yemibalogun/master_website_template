# app/application/cms/publish_page.py
from typing import Dict
from sqlalchemy import select
from app.extensions import db
from app.models.page import Page
from app.models.page_version import PageVersion
from app.utils.transaction import transactional
from app.utils.versioning import snapshot_page, next_version
from app.utils.audit import log_action
from app.domain.invariants.page import assert_page
from app.domain.lifecycle.page import assert_page_transition


def publish_page(
    *,
    tenant_id: str,
    page_id: str,
    actor_id: str,
) -> Dict[str, int]:
    """
    Publishes a page and creates an immutable version snapshot.

    Responsibilities:
    - transactional boundary
    - invariant enforcement
    - version creation
    - audit logging
    """

    # 1️⃣ Fetch page with row-level lock
    page = (
        db.session.execute(
            select(Page)
            .where(Page.id == page_id, Page.tenant_id == tenant_id)
            .with_for_update()
        )
        .scalar_one_or_none()
    )

    if not page:
        raise ValueError("Page not found")

    with transactional():
        # 2️⃣ Lifecycle transition enforcement
        assert_page_transition(from_status=page.status, to_status="published")

        # 3️⃣ Apply state change
        page.status = "published"

        # 4️⃣ Enforce publish-specific invariants
        assert_page(page, publish=True)

        # 5️⃣ Create immutable PageVersion
        version = PageVersion()
        version.page_id = page.id
        version.tenant_id = tenant_id
        version.version = next_version(page.id, tenant_id)
        version.status = "published"
        version.snapshot = snapshot_page(page)
        version.created_by = actor_id

        db.session.add(version)
        db.session.flush()  # ensures version.version is available

        # 6️⃣ Audit logging
        log_action(
            action="page.publish",
            entity_type="page",
            entity_id=page.id,
            payload={"version": version.version},
        )

    return {
        "page_id": page.id,
        "version": version.version,
    }
