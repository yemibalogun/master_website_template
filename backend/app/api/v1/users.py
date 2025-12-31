from flask import g, jsonify
from flask_jwt_extended import jwt_required
from app.models.user import User
from app.utils.decorators import (
    tenant_required,
    roles_required
)
from . import v1_bp


@v1_bp.route("/users", methods=["GET"])
@jwt_required()
@tenant_required
@roles_required("admin")
def list_users():
    users = User.query.filter_by(
        tenant_id=g.current_tenant.id
    ).all()

    return jsonify([
        {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active
        }
        for user in users
    ]), 200

