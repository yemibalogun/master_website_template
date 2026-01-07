# app/api/v1/audit.py
from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required
from app.utils.decorators import tenant_required, roles_required
from app.models.audit_log import AuditLog
from app.utils.pagination import apply_cursor, paginate_cursor

audit_bp = Blueprint("audit", __name__)


@audit_bp.route("/", methods=["GET"])
@jwt_required()
@tenant_required
@roles_required("admin")
def list_audit_logs():
    tenant = g.current_tenant

    limit: int = min(int(request.args.get("limit", 20)), 100)
    cursor: str | None = request.args.get("cursor")

    query = AuditLog.query.filter(
        AuditLog.tenant_id == tenant.id
    )

    # Optional filters (stay at API layer)
    if action := request.args.get("action"):
        query = query.filter(AuditLog.action == action)

    if entity_type := request.args.get("entity_type"):
        query = query.filter(AuditLog.entity_type == entity_type)

    if entity_id := request.args.get("entity_id"):
        query = query.filter(AuditLog.entity_id == entity_id)

    # 🔑 Cursor application (shared infra logic)
    query = apply_cursor(
        query=query,
        model=AuditLog,
        cursor=cursor,
    )

    logs, meta = paginate_cursor(
        query=query,
        model=AuditLog,
        limit=limit,
    )

    return jsonify({
        "data": [log.to_dict() for log in logs],
        "meta": meta,
    }), 200
