from typing import Dict
from flask import g
from app.extensions import db
from app.models.page import Page
from app.models.page_version import PageVersion
from app.utils.transaction import transactional
from app.utils.versioning import snapshot_page, next_version
from app.utils.audit import log_action
from app.domain.invariants.page import assert_page


def publish_page(
    *,
    tenant_id: str,
    page_id: str,
    actor_id: str,
) -> Dict[str, int]:
    """
    Publishes a page and creates an immutable version snapshot.

    This function owns:
    - transactional boundary
    - invariant enforcement
    - version creation
    - audit logging

    It deliberately knows NOTHING about Flask, requests, or responses.
    """

    # Fetch page inside service to guarantee tenant isolation
    page: Page = (
        Page.query
        .filter_by(id=page_id, tenant_id=tenant_id)
        .first_or_404()
    )

    with transactional():
        # State transition
        page.status = "published"

        # Enforce publish-specific invariants
        assert_page(page, publish=True)

        # Create immutable snapshot version
        version = PageVersion()
        version.page_id = page.id
        version.tenant_id = tenant_id
        version.version = next_version(page.id, tenant_id)
        version.status = "published"
        version.snapshot = snapshot_page(page)
        version.created_by = actor_id

        db.session.add(version)
        db.session.flush()  # ensures version.version is available

        # Audit AFTER all invariants pass
        log_action(
            action="page.publish",
            entity_type="page",
            entity_id=page.id,
            payload={"version": version.version},
        )

    # Return minimal DTO — API decides response shape
    return {
        "page_id": page.id,
        "version": version.version,
    }