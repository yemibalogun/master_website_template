# app/api/v1/cms.py
from flask import Blueprint, g, request, jsonify
from flask_jwt_extended import jwt_required
from app.application.cms.publish_page import publish_page
from app.application.cms.rollback_page import rollback_page
from app.application.cms.bulk_publish import bulk_publish_pages
from app.application.cms.autosave_page import autosave_page
from app.application.cms.unpublish_page import unpublish_page
from app.application.cms.create_page import create_page
from app.application.cms.update_page import update_page
from app.application.cms.delete_page import delete_page
from app.utils.decorators import tenant_required, roles_required, feature_enabled
from app.utils.media import save_file, delete_file
from app.utils.order import compact_order
from app.utils.audit import log_action
from app.utils.optimistic_lock import enforce_optimistic_lock
from app.utils.transaction import transactional
from app.utils.pagination import paginate_cursor, apply_cursor
from app.models.page import Page
from app.models.section import Section
from app.models.block import Block
from app.models.page_version import PageVersion
from app.extensions import db
from app.normalizers.page import normalize_page
from app.normalizers.section import normalize_section
from app.normalizers.pagination import normalize_pagination
from app.normalizers.block import normalize_block
from app.domain.invariants.page import assert_page
from app.domain.invariants.section import assert_section
from app.domain.invariants.block import assert_block_order, assert_block_media
from datetime import datetime 
from typing import List, cast, Dict

cms_bp = Blueprint("cms", __name__)

# Define allowed types
ALLOWED_SECTION_TYPES = {"hero", "features", "gallery", "content"}
ALLOWED_BLOCK_TYPES = {"text", "image", "video", "button"}

# ------------------------
# Pages
# ------------------------

@cms_bp.route("/pages", methods=["POST"])
@jwt_required()
@tenant_required
@roles_required("admin")
@feature_enabled("enable_cms")
def create_page_route():
    tenant = g.current_tenant
    user = g.current_user
    data = request.get_json(silent=True) or {}

    # Call the service layer using keyword arguments
    page = create_page(
        tenant_id=tenant.id,
        actor_id=user.id,
        data=data
    )

    return jsonify({
        "id": page.id, 
        "message": "Page created successfully"
    }), 201

@cms_bp.route("/pages/<slug>", methods=["GET"])
@jwt_required()
@tenant_required
@feature_enabled("enable_cms")
def get_page(slug):
    tenant = g.current_tenant
    page = Page.query.filter_by(
        tenant_id=tenant.id,
        slug=slug,
        status="published"
    ).first_or_404()

    return jsonify(normalize_page(page, admin=False))

@cms_bp.route("/pages/id/<page_id>", methods=["GET"])
@jwt_required()
@tenant_required
@roles_required("admin")
@feature_enabled("enable_cms")
def get_page_by_id(page_id):
    tenant = g.current_tenant
    page = Page.query.filter_by(
        tenant_id=tenant.id,
        id=page_id
    ).first_or_404()

    return jsonify(normalize_page(page, admin=True))

@cms_bp.route("/pages/<page_id>", methods=["PUT"])
@jwt_required()
@tenant_required
@roles_required("admin")
@feature_enabled("enable_cms")
def update_page_route(page_id):
    tenant = g.current_tenant
    user = g.current_user
    data = request.get_json() or {}
    
    # Call the service layer using keyword arguments
    update_page(
        tenant_id=tenant.id,
        page_id=page_id,
        actor_id=user.id,
        data=data
    )
    
    return jsonify({"message": "Page updated successfully"}), 200

@cms_bp.route("/pages/<page_id>/preview", methods=["GET"])
@jwt_required()
@tenant_required
@roles_required("admin")
@feature_enabled("enable_cms")
def preview_page(page_id):
    tenant = g.current_tenant
    page = Page.query.filter_by(
        id=page_id,
        tenant_id=tenant.id
    ).first_or_404()

    return jsonify(normalize_page(page, admin=True, preview=True))


@cms_bp.route("/pages/<page_id>/publish", methods=["POST"])
@jwt_required()
@tenant_required
@roles_required("admin")
@feature_enabled("enable_cms")
def publish_page_route(page_id):
    tenant = g.current_tenant
    user = g.current_user

    result = publish_page(
        tenant_id=tenant.id,
        page_id=page_id,
        actor_id=user.id
    )
    return jsonify(
        {
            "message": "Page published",
            "version": result["version"]
        }), 200
    
@cms_bp.route("/pages/<page_id>/unpublish", methods=["POST"])
@jwt_required()
@tenant_required
@roles_required("admin")
@feature_enabled("enable_cms")
def unpublish_page_route(page_id):
    tenant = g.current_tenant
    page = Page.query.filter_by(id=page_id, tenant_id=tenant.id).first_or_404()
    user = g.current_user

    unpublish_page(
        tenant_id=tenant.id,
        actor_id=user.id,
        page_id=page.id
    )
    return jsonify({"message": "Page unpublished successfully"}), 200


@cms_bp.route("/pages/<page_id>", methods=["DELETE"])
@jwt_required()
@tenant_required
@roles_required("admin")
@feature_enabled("enable_cms")
def delete_page_route(page_id):
    tenant = g.current_tenant
    page = Page.query.filter_by(id=page_id, tenant_id=tenant.id).first_or_404()
    user = g.current_user

    delete_page(
        tenant_id=tenant.id,
        page_id=page.id,
        actor_id=user.id
    )
    
    return jsonify({"message": "Page deleted successfully"}), 200

@cms_bp.route("/pages", methods=["GET"])
@jwt_required()
@tenant_required
def list_pages():
    tenant = g.current_tenant
    limit = min(request.args.get("limit", 20, type=int), 100)
    cursor = request.args.get("cursor")

    query = Page.query.filter_by(
        tenant_id=tenant.id,
        deleted_at=None,
    )

    query = apply_cursor(query, model=Page, cursor=cursor)
    items, meta = paginate_cursor(query, model=Page, limit=limit)

    # ✅ Tell Pylance these are Page instances
    items: List[Page] = items

    return jsonify(
        normalize_pagination(
            items,
            normalize_fn=normalize_page,
            cursor=meta
        )
        
    ), 200


@cms_bp.get("/pages/<int:page_id>/sections")
@jwt_required()
@tenant_required
def list_sections(page_id: int):
    tenant = g.current_tenant

    limit = min(request.args.get("limit", 20, type=int), 100)
    cursor = request.args.get("cursor")

    query = Section.query.filter_by(
        tenant_id=tenant.id,
        page_id=page_id,
        deleted_at=None,
    )

    query = apply_cursor(query, model=Section, cursor=cursor)
    items, meta = paginate_cursor(query, model=Section, limit=limit)

    return jsonify(
        normalize_pagination(
            items,
            normalize_fn=normalize_section,
            cursor=meta
        )
    ), 200


@cms_bp.route("/pages/<page_id>/versions", methods=["GET"])
@jwt_required()
@tenant_required
@roles_required("admin")
def list_versions(page_id):
    tenant = g.current_tenant

    limit = min(request.args.get("limit", 10, type=int), 50)
    cursor = request.args.get("cursor")

    query = PageVersion.query.filter_by(
        tenant_id=tenant.id,
        page_id=page_id,
    )

    query = apply_cursor(query, model=PageVersion, cursor=cursor)
    versions, meta = paginate_cursor(query, model=PageVersion, limit=limit)

    return jsonify(
        normalize_pagination(
            versions,
            normalize_fn=lambda v: {
                "id": v.id,
                "version": v.version,
                "status": v.status,
                "created_at": v.created_at.isoformat(),
                "created_by": v.created_by,
            },
            cursor=meta
        )
    ), 200


@cms_bp.route("/pages/<page_id>/rollback/<int:version>", methods=["POST"])
@jwt_required()
@tenant_required
@roles_required("admin")
def rollback_page_route(page_id, version):
    tenant = g.current_tenant
    user = g.current_user

    # -------------------------------
    # 2️⃣ Otherwise → POST request with version → perform rollback
    # -------------------------------
    result = rollback_page(
        tenant_id=tenant.id,
        page_id=page_id,
        rollback_version=version,
        actor_id=user.id
    )

    return jsonify({
        "message": f"Rolled back to version {version}",
        "new_version": result["version"]
    }), 200


# ------------------------
# Sections
# ------------------------
@cms_bp.route("/pages/<page_id>/sections", methods=["POST"])
@jwt_required()
@tenant_required
@roles_required("admin")
@feature_enabled("enable_cms")
def create_section(page_id):
    tenant = g.current_tenant
    page = Page.query.filter_by(id=page_id, tenant_id=tenant.id).first_or_404()
    data = request.get_json()
    
    section_type = data.get("type")

    if not section_type:
        return jsonify({"error": "Section type is required"}), 400

    if section_type not in ALLOWED_SECTION_TYPES:
        return jsonify({"error": "Invalid section type"}), 400

    with transactional():
        # Determine the current max order for this page
        max_order = db.session.query(db.func.max(Section.order))\
            .filter_by(page_id=page.id, tenant_id=tenant.id)\
            .scalar() or 0
        
        section = Section(
            tenant_id=tenant.id,
            page_id=page.id,
            type=section_type,
            order=max_order + 1,
            settings=data.get("settings", {})
        )

        db.session.add(section)
        db.session.flush()

        assert_section(section)  # Invariant Enforcement Point
        assert_page(page)
        
        log_action(
            action="section.create",
            entity_type="section",
            entity_id=section.id,
            payload={
                "page_id": page.id,
                "type": section.type,
                "order": section.order
            }
        )
  
    return jsonify({"id": section.id, "message": "Section created successfully"}), 201

@cms_bp.route("/sections/<section_id>", methods=["PUT"])
@jwt_required()
@tenant_required
@roles_required("admin")
@feature_enabled("enable_cms")
def update_section(section_id):
    tenant = g.current_tenant
    section = Section.query.filter_by(id=section_id, tenant_id=tenant.id).first_or_404()
    
    # -----------------------
    # Optimistic Locking Check
    # -----------------------
    enforce_optimistic_lock(section)

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
  
    if "type" in data and data["type"] not in ALLOWED_SECTION_TYPES:
        return jsonify({"error": "Invalid section type"}), 400

    with transactional():
        changed_fields = []

        for field in ("type", "order", "settings"):
            if field in data and getattr(section, field) != data[field]:
                setattr(section, field, data[field])
                changed_fields.append(field)

        assert_section(section)  # Invariant Enforcement Point
        assert_page(section.page)

        if changed_fields:
            log_action(
                action="section.update",
                entity_type="section",
                entity_id=section.id,
                payload={"fields": changed_fields}
            )

    return jsonify({"message": "Section updated successfully"}), 200


@cms_bp.route("/sections/<section_id>", methods=["DELETE"])
@jwt_required()
@tenant_required
@roles_required("admin")
@feature_enabled("enable_cms")
def delete_section(section_id):
    tenant = g.current_tenant
    section = Section.query.filter_by(id=section_id, tenant_id=tenant.id).first_or_404()

    page_id = section.page_id

    media_to_cleanup = []
    
    with transactional():
        for block in section.blocks:
            if block.media_url:
                media_to_cleanup.append(block.media_url)
            block.soft_delete()

        section.soft_delete()
        db.session.flush()

        compact_order(
            Section.query.filter_by(page_id=page_id, tenant_id=tenant.id, deleted_at=None)
        )

        assert_page(section.page)

        log_action(
            action="section.delete",
            entity_type="section",
            entity_id=section.id,
            payload={"page_id": page_id}
        )
    for media_url in media_to_cleanup:
        delete_file(media_url)

    return jsonify({"message": "Section deleted and order re-compacted"}), 200

@cms_bp.route("/sections/<section_id>/blocks", methods=["GET"])
@jwt_required()
@tenant_required
@roles_required("admin")
def list_blocks(section_id):
    tenant = g.current_tenant

    limit = min(request.args.get("limit", 20, type=int), 100)
    cursor = request.args.get("cursor")

    query = Block.query.filter_by(
        tenant_id=tenant.id,
        section_id=section_id,
        deleted_at=None
    )

    query = apply_cursor(query, Block, cursor)
    blocks, meta = paginate_cursor(query, Block, limit)

    return jsonify(
        normalize_pagination(
            blocks,
            normalize_fn=normalize_block,
            cursor=meta
        )
    ), 200

# ------------------------
# Sections
# ------------------------
@cms_bp.route("/pages/<page_id>/sections/reorder", methods=["POST"])
@jwt_required()
@tenant_required
@roles_required("admin")
@feature_enabled("enable_cms")
def reorder_sections(page_id):
    tenant = g.current_tenant
    data = request.get_json()  # [{id: "...", order: 0}, ...]
    
    
    if not isinstance(data, list):
        return jsonify({"error": "Invalid payload"}), 400

    # Optional: paginate the reordering
    page_num = request.args.get("page", 1, type=int)
    per_page = int(request.args.get("per_page", len(data)))

    # Fetch only sections in the current page
    pagination = Section.query.filter_by(
        page_id=page_id, 
        tenant_id=tenant.id
        ).order_by(Section.order.asc())\
        .paginate(page=page_num, per_page=per_page, error_out=False)

    with transactional():
        # Map paginated sections by id for validation
        section_map = {s.id: s for s in pagination.items}

        for item in data:
            if item["id"] in section_map:
                section_map[item["id"]].order = item["order"]

        db.session.flush()

        # FINAL STEP: re-compact ALL sections on this page
        compact_order(
            Section.query.filter_by(page_id=page_id, tenant_id=tenant.id, deleted_at=None)
        )

        assert_page(Page.query.filter_by(id=page_id, tenant_id=tenant.id).first_or_404())

        log_action(
            action="section.reorder",
            entity_type="page",
            entity_id=page_id,
            payload={
                "page": page_num,
                "per_page": per_page,
                "count": len(data)
            }
        )

    return jsonify({"message": "Sections reordered and normalized"}), 200


# ------------------------
# Blocks
# ------------------------
@cms_bp.route("/sections/<section_id>/blocks", methods=["POST"])
@jwt_required()
@tenant_required
@roles_required("admin")
@feature_enabled("enable_cms")
def create_block(section_id):
    tenant = g.current_tenant
    section = Section.query.filter_by(
        id=section_id,
        tenant_id=tenant.id
    ).first_or_404()

    data = request.form
    block_type = data.get("type")

    if not block_type:
        return jsonify({"error": "Block type is required"}), 400

    if block_type not in ALLOWED_BLOCK_TYPES:
        return jsonify({"error": "Invalid block type"}), 400

    file = request.files.get("file")
    media_url = None

    try:
        # Save file first (temporary success)
        if file:
            media_url = save_file(file)

        with transactional():
            max_order = (
                db.session.query(db.func.max(Block.order))
                .filter_by(section_id=section.id, tenant_id=tenant.id)
                .scalar()
                or 0
            )

            block = Block(
                tenant_id=tenant.id,
                section_id=section.id,
                type=block_type,
                order=max_order + 1,
                content=data.get("content"),
                media_url=media_url
            )
          
            db.session.add(block)
            db.session.flush()

            assert_block_order(block)
            assert_block_media(block)
            assert_section(section)

            log_action(
                action="block.create",
                entity_type="block",
                entity_id=block.id,
                payload={
                    "section_id": section.id,
                    "type": block.type,
                    "order": block.order,
                },
            )

        return jsonify(
            {
                "id": block.id,
                "order": block.order,
                "message": "Block created successfully",
            }
        ), 201

    except Exception:
        # 🔥 CLEANUP ON FAILURE
        if media_url:
            delete_file(media_url)
        raise

@cms_bp.route("/blocks/<block_id>", methods=["PUT"])
@jwt_required()
@tenant_required
@roles_required("admin")
@feature_enabled("enable_cms")
def update_block(block_id):
    tenant = g.current_tenant
    block = Block.query.filter_by(id=block_id, tenant_id=tenant.id).first_or_404()

    enforce_optimistic_lock(block)

    data = request.form if request.form else request.get_json(silent=True) or {}

    # ✅ VALIDATE FIRST — BEFORE SAVING FILE
    if "type" in data and data["type"] not in ALLOWED_BLOCK_TYPES:
        return jsonify({"error": "Invalid block type"}), 400

    new_media_url = None
    old_media_url = block.media_url

    try:
        # SAVE FILE ONLY AFTER VALIDATION
        if "file" in request.files:
            new_media_url = save_file(request.files["file"])

        with transactional():
            if new_media_url:
                block.media_url = new_media_url

            for field in ("type", "order", "content"):
                if field in data:
                    setattr(block, field, data[field])

            assert_block_order(block)
            assert_block_media(block)
            assert_section(block.section)

            log_action(
                action="block.update",
                entity_type="block",
                entity_id=block.id
            )

        # ✅ DELETE OLD FILE AFTER COMMIT
        if new_media_url and old_media_url:
            delete_file(old_media_url)

        return jsonify({"message": "Block updated successfully"}), 200
    except Exception:
        # 🔥 CLEANUP IF TRANSACTION FAILS
        if new_media_url:
            delete_file(new_media_url)
        raise

@cms_bp.route("/blocks/<block_id>", methods=["DELETE"])
@jwt_required()
@tenant_required
@roles_required("admin")
@feature_enabled("enable_cms")
def delete_block(block_id):
    tenant = g.current_tenant
    block = Block.query.filter_by(id=block_id, tenant_id=tenant.id).first_or_404()

    media_to_delete = block.media_url

    with transactional():
        block.soft_delete()
        assert_section(block.section)

        log_action(
            action="block.delete",
            entity_type="block",
            entity_id=block.id
        )

    # ✅ DELETE FILE AFTER COMMIT
    if media_to_delete:
        delete_file(media_to_delete)

    return jsonify({"message": "Block deleted successfully"}), 200


@cms_bp.route("/sections/<section_id>/blocks/reorder", methods=["POST"])
@jwt_required()
@tenant_required
@roles_required("admin")
@feature_enabled("enable_cms")
def reorder_blocks(section_id):
    tenant = g.current_tenant
    data = request.get_json()  # [{id: "...", order: 0}, ...]

    if not isinstance(data, list):
        return jsonify({"error": "Invalid payload"}), 400

    # Optional: paginate the reordering
    page_num = request.args.get("page", 1, type=int)
    per_page = int(request.args.get("per_page", len(data)))

    # Fetch only blocks in the current page
    pagination = Block.query.filter_by(
        section_id=section_id, 
        tenant_id=tenant.id
        ).order_by(Block.order.asc())\
        .paginate(page=page_num, per_page=per_page, error_out=False)

    with transactional():
        # Map paginated blocks by id for validation
        block_map = {b.id: b for b in pagination.items}

        for item in data:
            if item["id"] in block_map:
                block_map[item["id"]].order = item["order"]

        db.session.flush()

        compact_order(
            Block.query.filter_by(section_id=section_id, tenant_id=tenant.id, deleted_at=None)
        )
        section = Section.query.filter_by(id=section_id, tenant_id=tenant.id).first_or_404()
        assert_section(section)

        log_action(
            action="block.reorder",
            entity_type="section",
            entity_id=section_id,
            payload={
                "page": page_num,
                "per_page": per_page,
                "count": len(data)
            }
        )

    return jsonify({"message": f"Blocks reordered and normalized"}), 200


@cms_bp.route("/pages/<page_id>/autosave", methods=["POST"])
@jwt_required()
@tenant_required
@roles_required("admin")
def autosave_page_route(page_id):
    tenant = g.current_tenant
    user = g.current_user
    
    autosave_page(
        tenant_id=tenant.id,
        page_id=page_id,
        actor_id=user.id
    )

    return jsonify({"message": "Draft autosaved"}), 200


@cms_bp.route("/pages/bulk/publish", methods=["POST"])
@jwt_required()
@tenant_required
@roles_required("admin")
def bulk_publish():
    tenant = g.current_tenant
    user = g.current_user
    data = request.get_json() or {}

    page_ids = data.get("page_ids", [])
    action = data.get("action")

    if action not in {"publish", "unpublish"}:
        return jsonify({"error": "Invalid action"}), 400

    result = bulk_publish_pages(
        tenant_id=tenant.id,
        page_ids=page_ids,
        action=action,
        actor_id=user.id
    )

    return jsonify({
        "message": f"Pages {action}ed successfully",
        "count": result["count"],
        "action": result["action"]
    }), 200

