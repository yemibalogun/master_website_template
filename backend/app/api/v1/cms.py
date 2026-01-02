# app/api/v1/cms.py
from flask import Blueprint, g, request, jsonify
from flask_jwt_extended import jwt_required
from app.utils.decorators import tenant_required, roles_required, feature_enabled
from app.utils.media import save_file
from app.models.page import Page
from app.models.section import Section
from app.models.block import Block
from app.extensions import db
from . import v1_bp # import the versioned blueprint

cms_bp = Blueprint("cms", __name__)

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

    return jsonify({
        "id": page.id,
        "title": page.title,
        "slug": page.slug,
        "seo": page.seo,
        "sections": [
            {
                "id": s.id,
                "type": s.type,
                "order": s.order,
                "settings": s.settings,
                "blocks": [
                    {
                        "id": b.id,
                        "type": b.type,
                        "order": b.order,
                        "content": b.content
                    } for b in s.blocks
                ]
            } for s in page.sections
        ]
    })

@cms_bp.route("/pages/<page_id>", methods=["PUT"])
@jwt_required()
@tenant_required
@roles_required("admin")
@feature_enabled("enable_cms")
def update_page(page_id):
    tenant = g.current_tenant
    page = Page.query.filter_by(id=page_id, tenant_id=tenant.id).first_or_404()
    data = request.get_json() or {}

    page.title = data.get("title", page.title)
    page.slug = data.get("slug", page.slug)
    page.status = data.get("status", page.status)
    page.seo = data.get("seo", page.seo)

    db.session.commit()
    return jsonify({"message": "Page updated successfully"}), 200


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

    section = Section()
    section.tenant_id = tenant.id
    section.page_id = page.id
    section.type = data.get("type")
    section.order = data.get("order", 0)
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

    db.session.delete(section)
    db.session.commit()
    return jsonify({"message": "Section deleted successfully"}), 200

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
    order = int(data.get("order", 0))
    content = data.get("content")

    if not block_type:
        return jsonify({"error": "Block type is required"}), 400

    media_url = None
    if "file" in request.files:
        media_url = save_file(request.files["file"])

    block = Block()
    block.tenant_id = tenant.id
    block.section_id = section.id
    block.type = block_type
    block.order = order
    block.content = content
    block.media_url = media_url

    db.session.add(block)
    db.session.commit()

    return jsonify({"id": block.id, "message": "Block created successfully"}), 201

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

    db.session.delete(block)
    db.session.commit()
    return jsonify({"message": "Block deleted successfully"}), 200


@cms_bp.route("/pages/<page_id>/sections/reorder", methods=["POST"])
@jwt_required()
@tenant_required
@roles_required("admin")
@feature_enabled("enable_cms")
def reorder_sections(page_id):
    tenant = g.current_tenant
    data = request.get_json()  # [{id: "...", order: 0}, ...]

    for item in data:
        section = Section.query.filter_by(
            id=item["id"], 
            tenant_id=tenant.id
        ).first()
        if section:
            section.order = item["order"]

    db.session.commit()
    return jsonify({"message": "Sections reordered"})