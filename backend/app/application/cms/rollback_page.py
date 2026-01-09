# app/application/cms/rollback_page.py
from typing import Dict, List
from datetime import datetime, timezone
from app.extensions import db
from app.models.page import Page
from app.models.page_version import PageVersion
from app.models.section import Section
from app.models.block import Block
from app.utils.transaction import transactional
from app.utils.versioning import snapshot_page, next_version
from app.utils.order import compact_order
from app.utils.audit import log_action
from app.utils.media import delete_file
from app.domain.invariants.page import assert_page
from app.domain.invariants.section import assert_section
from app.domain.lifecycle.page import assert_page_transition
from sqlalchemy import select


def rollback_page(
    *,
    tenant_id: str,
    page_id: str,
    rollback_version: int,
    actor_id: str
) -> Dict[str, int]:
    """
    Roll back a page to a previous version.

    Responsibilities:
    - Transactional snapshot restoration
    - Cleanup deleted media
    - Re-compact section & block ordering
    - Create new rollback version
    - Audit logging
    """

    # 1️⃣ Fetch the PageVersion to roll back to
    pv: PageVersion | None = (
        PageVersion.query
        .filter_by(page_id=page_id, tenant_id=tenant_id, version=rollback_version)
        .first()
    )

    if not pv:
        raise ValueError("PageVersion not found")

    snapshot = pv.snapshot

    # 2️⃣ Fetch live Page with row-level lock
    page: Page | None = (
        db.session.execute(
            select(Page)
            .where(Page.id == page_id, Page.tenant_id == tenant_id)
            .with_for_update()
        )
        .scalar_one_or_none()
    )

    if not page:
        raise ValueError("Page not found")

    # Ensure lifecycle transition is valid
    assert_page_transition(from_status=page.status, to_status="draft")
    page.status = "draft"

    media_to_cleanup: List[str] = []

    with transactional():
        # 3️⃣ Soft-delete current sections & blocks
        current_sections = (
            Section.query
            .filter_by(page_id=page.id, tenant_id=tenant_id, deleted_at=None)
            .all()
        )

        for section in current_sections:
            for block in section.blocks:
                if block.media_url:
                    media_to_cleanup.append(block.media_url)
                block.soft_delete()
            section.soft_delete()

        # 4️⃣ Restore sections & blocks from snapshot
        for s_data in snapshot["sections"]:
            section = Section()
            section.tenant_id = tenant_id
            section.page_id = page.id
            section.type = s_data["type"]
            section.order = s_data["order"]
            section.settings = s_data["settings"]

            db.session.add(section)
            db.session.flush()  # Ensure section.id

            for b_data in s_data["blocks"]:
                block = Block()
                block.tenant_id = tenant_id
                block.section_id = section.id
                block.type = b_data["type"]
                block.order = b_data["order"]
                block.content = b_data["content"]
                block.media_url = b_data.get("media_url")

                db.session.add(block)

        # 5️⃣ Normalize ordering
        sections = Section.query.filter_by(page_id=page.id, tenant_id=tenant_id, deleted_at=None)
        compact_order(sections)

        for section in sections:
            blocks_query = Block.query.filter_by(section_id=section.id, tenant_id=tenant_id, deleted_at=None)
            compact_order(blocks_query)

        # 6️⃣ Assert invariants
        assert_page(page)

        # 7️⃣ Create rollback PageVersion
        new_version = PageVersion()
        new_version.page_id = page.id
        new_version.tenant_id = tenant_id
        new_version.version = next_version(page.id, tenant_id)
        new_version.status = "rollback"
        new_version.snapshot = snapshot_page(page)
        new_version.created_by = actor_id

        db.session.add(new_version)

        # 8️⃣ Audit logging
        log_action(
            action="page.rollback",
            entity_type="page",
            entity_id=page.id,
            payload={
                "from_version": rollback_version,
                "to_version": new_version.version,
            }
        )

    # 9️⃣ Cleanup media outside transaction
    for media_url in media_to_cleanup:
        delete_file(media_url)

    return {
        "page_id": page.id,
        "new_version": new_version.version
    }
