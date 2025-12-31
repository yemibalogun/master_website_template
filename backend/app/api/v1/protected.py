from flask import jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import v1_bp


@v1_bp.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    identity = get_jwt_identity()
    tenant = g.current_tenant

    if not tenant:
        return jsonify({"error": "Tenant context missing"}), 400

    # Enforce tenant isolation
    if identity["tenant_id"] != tenant.id:
        return jsonify({"error": "Tenant mismatch"}), 403

    return jsonify({
        "message": "Access granted",
        "user_id": identity["user_id"],
        "tenant_id": tenant.id,
        "tenant_name": tenant.name
    }), 200
