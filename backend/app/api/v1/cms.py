# app/api/v1/cms.py
from flask import Blueprint, g, request, jsonify
from flask_jwt_extended import jwt_required
from app.utils.decorators import tenant_required, roles_required, feature_enabled
from app.utils.media import save_file, delete_file
from app.utils.order import compact_order
from app.models.page import Page
from app.models.section import Section
from app.models.block import Block
from app.extensions import db
from app.normalizers.page import normalize_page
from app.normalizers.section import normalize_section
from app.normalizers.pagination import normalize_pagination
from app.normalizers.block import normalize_block
from . import v1_bp # import the versioned blueprint

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
def create_page():
    tenant = g.current_tenant
    data = request.get_json(silent=True) or {}

    if not data.get("title") or not data.get("slug"):
        return jsonify({"error": "Title and slug are required"}), 400
    
    existing = Page.query.filter_by(
        tenant_id=tenant.id,
        slug=data["slug"]
    ).first()

    if existing:
        return jsonify({"error": "Slug already exists"}), 409

    page = Page()
    
    page.tenant_id = tenant.id  # add tenant
    page.title = data["title"]
    page.slug = data["slug"]
    page.status = data.get("status", "draft")
    page.seo = data.get("seo", {})

    db.session.add(page)
    db.session.commit()

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

    return jsonify(normalize_page(page, admin=False))

@cms_bp.route("/pages/<page_id>", methods=["PUT"])
@jwt_required()
@tenant_required
@roles_required("admin")
@feature_enabled("enable_cms")
def update_page(page_id):
    tenant = g.current_tenant
    page = Page.query.filter_by(id=page_id, tenant_id=tenant.id).first_or_404()
    data = request.get_json() or {}

    # Slug collision check
    if "slug" in data and data["slug"] != page.slug:
        exists = Page.query.filter_by(
            tenant_id=tenant.id,
            slug=data["slug"]
        ).first()
        if exists:
            return jsonify({"error": "Slug already exists"}), 409

    page.title = data.get("title", page.title)
    page.slug = data.get("slug", page.slug)
    page.status = data.get("status", page.status)
    page.seo = data.get("seo", page.seo)

    db.session.commit()
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
def publish_page(page_id):
    tenant = g.current_tenant
    page = Page.query.filter_by(id=page_id, tenant_id=tenant.id).first_or_404()

    page.status = "published"
    db.session.commit()

    return jsonify({"message": "Page published successfully"}), 200

@cms_bp.route("/pages/<page_id>/unpublish", methods=["POST"])
@jwt_required()
@tenant_required
@roles_required("admin")
@feature_enabled("enable_cms")
def unpublish_page(page_id):
    tenant = g.current_tenant
    page = Page.query.filter_by(id=page_id, tenant_id=tenant.id).first_or_404()

    page.status = "draft"
    db.session.commit()

    return jsonify({"message": "Page unpublished successfully"}), 200


@cms_bp.route("/pages/<page_id>", methods=["DELETE"])
@jwt_required()
@tenant_required
@roles_required("admin")
@feature_enabled("enable_cms")
def delete_page(page_id):
    tenant = g.current_tenant
    page = Page.query.filter_by(id=page_id, tenant_id=tenant.id).first_or_404()

    db.session.delete(page)
    db.session.commit()
    return jsonify({"message": "Page deleted successfully"}), 200

@cms_bp.route("/pages", methods=["GET"])
@jwt_required()
@tenant_required
@roles_required("admin")
@feature_enabled("enable_cms")
def list_pages():
    tenant = g.current_tenant

    status = request.args.get("status") #draft | published | None
    page_num = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))

    query = Page.query.filter_by(tenant_id=tenant.id)
    if status:
        query = query.filter_by(status=status)

    pagination = query.order_by(Page.created_at.desc()).paginate(page=page_num, per_page=per_page, error_out=False)

    return jsonify(
        normalize_pagination(
            pagination,
            lambda p: normalize_page(p, admin=True)
        )
    )

@cms_bp.route("/pages/<page_id>/sections", methods=["GET"])
@jwt_required()
@tenant_required
@roles_required("admin")
@feature_enabled("enable_cms")
def list_sections(page_id):
    tenant = g.current_tenant

    page_num = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))

    query = Section.query.filter_by(page_id=page_id, tenant_id=tenant.id)
    pagination = query.order_by(Section.order.asc()).paginate(page=page_num, per_page=per_page, error_out=False)
    
    return jsonify(
        normalize_pagination(
            pagination,
            lambda s: normalize_section(s, admin=True)
        )
    )
    
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

    # Determine the current max order for this page
    max_order = db.session.query(db.func.max(Section.order))\
        .filter_by(page_id=page.id, tenant_id=tenant.id)\
        .scalar() or 0
    
    section = Section()
    section.tenant_id = tenant.id
    section.page_id = page.id
    section.type = section_type
    section.order = max_order + 1
    section.settings = data.get("settings", {})

    db.session.add(section)
    db.session.commit()
    return jsonify({"id": section.id, "message": "Section created successfully"}), 201

@cms_bp.route("/sections/<section_id>", methods=["PUT"])
@jwt_required()
@tenant_required
@roles_required("admin")
@feature_enabled("enable_cms")
def update_section(section_id):
    tenant = g.current_tenant
    section = Section.query.filter_by(id=section_id, tenant_id=tenant.id).first_or_404()
    data = request.get_json()

    section.type = data.get("type", section.type)
    section.order = data.get("order", section.order)
    section.settings = data.get("settings", section.settings)

    db.session.commit()
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

    db.session.delete(section)
    db.session.flush()

    # Re-compact remaining sections on the page
    compact_order(
        Section.query.filter_by(page_id=page_id, tenant_id=tenant.id)
    )

    db.session.commit()

    return jsonify({"message": "Section deleted and order re-compacted"}), 200


@cms_bp.route("/sections/<section_id>/blocks", methods=["GET"])
@jwt_required()
@tenant_required
@roles_required("admin")
@feature_enabled("enable_cms")
def list_blocks(section_id):
    tenant = g.current_tenant

    page_num = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))

    query = Block.query.filter_by(tenant_id=tenant.id, section_id=section_id)
    pagination = query.order_by(Block.order.asc()).paginate(page=page_num, per_page=per_page, error_out=False)
    
    return jsonify(
        normalize_pagination(
            pagination,
            lambda b: normalize_block(b, admin=True)
        )
    )


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
    page_num = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", len(data)))

    # Fetch only sections in the current page
    pagination = Section.query.filter_by(
        page_id=page_id, 
        tenant_id=tenant.id
        ).order_by(Section.order.asc())\
        .paginate(page=page_num, per_page=per_page, error_out=False)

    # Map paginated sections by id for validation
    section_map = {s.id: s for s in pagination.items}

    for item in data:
        if item["id"] in section_map:
            section_map[item["id"]].order = item["order"]

    db.session.flush()

    # FINAL STEP: re-compact ALL sections on this page
    compact_order(
        Section.query.filter_by(page_id=page_id, tenant_id=tenant.id)
    )

    db.session.commit()
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
    section = Section.query.filter_by(id=section_id, tenant_id=tenant.id).first_or_404()
    
    data = request.form
    
    block_type = data.get("type")
    if not block_type:
        return jsonify({"error": "Block type is required"}), 400
    
    if block_type not in ALLOWED_BLOCK_TYPES:
        return jsonify({"error": "Invalid block type"}), 400

    # Determine the current max order for this section
    max_order = db.session.query(db.func.max(Block.order))\
        .filter_by(section_id=section.id, tenant_id=tenant.id)\
        .scalar() or 0
    
    content = data.get("content")
    media_url = save_file(request.files["file"]) if "file" in request.files else None

    block = Block()
    block.tenant_id = tenant.id
    block.section_id = section.id
    block.type = block_type
    block.order = max_order + 1  # append at the end
    block.content = content
    block.media_url = media_url

    db.session.add(block)
    db.session.commit()
    return jsonify({"id": block.id, "order": block.order, "message": "Block created successfully"}), 201

@cms_bp.route("/blocks/<block_id>", methods=["PUT"])
@jwt_required()
@tenant_required
@roles_required("admin")
@feature_enabled("enable_cms")
def update_block(block_id):
    tenant = g.current_tenant
    block = Block.query.filter_by(id=block_id, tenant_id=tenant.id).first_or_404()
    
    data = request.form if request.form else request.get_json(silent=True) or {}

    block.type = data.get("type", block.type)
    block.order = int(data.get("order", block.order))
    block.content = data.get("content", block.content)

    if 'file' in request.files:
        # Here you would normally save the file and get its URL
        block.media_url = save_file(request.files["file"])  # assuming save_file is a utility function

    db.session.commit()
    return jsonify({"message": "Block updated successfully"}), 200


@cms_bp.route("/blocks/<block_id>", methods=["DELETE"])
@jwt_required()
@tenant_required
@roles_required("admin")
@feature_enabled("enable_cms")
def delete_block(block_id):
    tenant = g.current_tenant
    block = Block.query.filter_by(id=block_id, tenant_id=tenant.id).first_or_404()

    section_id = block.section_id

    # Delete media file first
    if block.media_url:
        delete_file(block.media_url)

    db.session.delete(block)
    db.session.flush()

    compact_order(
        Block.query.filter_by(section_id=section_id, tenant_id=tenant.id)
    )

    db.session.commit()
    return jsonify({"message": "Block deleted and order re-compacted"}), 200


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
    page_num = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", len(data)))

    # Fetch only blocks in the current page
    pagination = Block.query.filter_by(
        section_id=section_id, 
        tenant_id=tenant.id
        ).order_by(Block.order.asc())\
        .paginate(page=page_num, per_page=per_page, error_out=False)

    block_map = {b.id: b for b in pagination.items}

    for item in data:
        if item["id"] in block_map:
            block_map[item["id"]].order = item["order"]

    db.session.flush()

    compact_order(
        Block.query.filter_by(section_id=section_id, tenant_id=tenant.id)
    )

    db.session.commit()
    return jsonify({"message": f"Blocks reordered and normalized"}), 200


