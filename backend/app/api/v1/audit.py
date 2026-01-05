from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required
from app.utils.decorators import tenant_required, roles_required
from app.models.audit_log import AuditLog
from sqlalchemy import or_, and_
from datetime import datetime

audit_bp = Blueprint("audit", __name__)

@audit_bp.route("/", methods=["GET"])
@jwt_required()
@tenant_required
@roles_required("admin")
def list_audit_logs():
    tenant = g.current_tenant

    # Cursor Pagination 
    limit = min(int(request.args.get("limit", 20)), 100)
    cursor = request.args.get("cursor")

    query = AuditLog.query.filter(
        AuditLog.tenant_id == tenant.id
    )

    # Optional filters
    if action := request.args.get("action"):
        query = query.filter(AuditLog.action == action)

    if entity_type := request.args.get("entity_type"):
        query = query.filter(AuditLog.entity_type == entity_type)

    if entity_id := request.args.get("entity_id"):
        query = query.filter(AuditLog.entity_id == entity_id)

    # Cursor parsing 
    if cursor:
        try:
            ts_str, last_id = cursor.split("|")
            cursor_ts = datetime.fromisoformat(ts_str)

            query = query.filter(
                or_(
                    AuditLog.created_at < cursor_ts,
                    and_(
                        AuditLog.created_at == cursor_ts,
                        AuditLog.id < last_id
                    )
                )
            )
        except ValueError:
            return jsonify({"error": "Invalid cursor format"}), 400
        
    logs = (
        query.order_by(AuditLog.created_at.desc(), AuditLog.id.desc())
        .limit(limit + 1)   # Fetch extra row to detect "has_more"
        .all()
    )

    has_more = len(logs) > limit
    logs = logs[:limit]

    next_cursor = None
    if has_more:
        last = logs[-1]
        next_cursor = f"{last.created_at.isoformat()}|{last.id}"

    return jsonify({
        "data": [
            {
                "id": log.id,
                "actor_id": log.actor_id,
                "action": log.action,
                "entity_type": log.entity_type,
                "entity_id": log.entity_id,
                "payload": log.payload,
                "created_at": log.created_at.isoformat(),
            }
            for log in logs
        ],
        "meta": {
            "next_cursor": next_cursor,
            "has_more": has_more,
        }
    }), 200

