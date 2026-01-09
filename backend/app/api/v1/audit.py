# app/api/v1/audit.py
from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required
from app.utils.decorators import tenant_required, roles_required
from app.models.audit_log import AuditLog
from app.utils.pagination import apply_cursor, paginate_cursor
from app.normalizers.audit import normalize_audit_log

audit_bp = Blueprint("audit", __name__)


@audit_bp.route("/audit_logs", methods=["GET"])
@jwt_required()
@tenant_required
def list_audit_logs():
    tenant = g.current_tenant

    limit = request.args.get("limit", 50, type=int)
    cursor = request.args.get("cursor")
    direction = request.args.get("direction", "next")

    entity_type = request.args.get("entity_type")
    entity_id = request.args.get("entity_id")

    query = AuditLog.query.filter_by(
        tenant_id=tenant.id,
    )

    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)

    if entity_id:
        query = query.filter(AuditLog.entity_id == entity_id)

    query = apply_cursor(
        query,
        model=AuditLog,
        cursor=cursor,
        direction=direction,
    )

    logs, meta = paginate_cursor(
        query,
        model=AuditLog,
        limit=limit,
        direction=direction,
    )

    return jsonify({
        "items": [normalize_audit_log(l) for l in logs],
        "pagination": meta,
    }), 200
