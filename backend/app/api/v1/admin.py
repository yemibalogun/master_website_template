from flask import jsonify
from flask_jwt_extended import jwt_required
from app.utils.decorators import roles_required
from . import v1_bp

@v1_bp.route("/admin/dashboard", methods=["GET"])
@jwt_required()
@roles_required("admin")
def admin_dashboard():
    return jsonify({
        "message": "Welcome admin!"
    })