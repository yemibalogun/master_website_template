from flask import request, jsonify, g
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token
)
from app.models.user import User
from . import v1_bp


@v1_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request body"}), 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    tenant = g.current_tenant
    if not tenant:
        return jsonify({"error": "Tenant context missing"}), 400

    user = User.query.filter_by(
        email=email,
        tenant_id=tenant.id
    ).first()

    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    if not user.is_active:
        return jsonify({"error": "User account disabled"}), 403

    identity = {
        "user_id": user.id,
        "tenant_id": tenant.id,
        "role": user.role
    }

    access_token = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity)

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token
    }), 200
