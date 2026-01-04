from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required
from app.utils.decorators import tenant_required, roles_required
from app.models.audit_log import AuditLog

audit_bp = Blueprint("audit", __name__)

@audit_bp.route("/audit-logs", methods=["GET"])
@jwt_required()
@tenant_required
@roles_required("admin")
def list_audit_logs():
    tenant = g.current_tenant

    query = AuditLog.query.filter_by(tenant_id=tenant.id)

    # Optional filters
    if action := request.args.get("action"):
        query = query.filter_by(action=action)

    if entity_type := request.args.get("entity_type"):
        query = query.filter_by(entity_type=entity_type)

    if entity_id := request.args.get("entity_id"):
        query = query.filter_by(entity_id=entity_id)

    logs = (
        query
        .order_by(AuditLog.created_at.desc())
        .limit(100)
        .all()
    )

    return jsonify([
        {
            "id": log.id,
            "actor_id": log.actor_id,
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "payload": log.payload,
            "created_at": log.created_at,
        }
        for log in logs
    ])
