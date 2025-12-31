from flask import request, g, jsonify
from app.models.tenant import Tenant
from app.extensions import db

def tenant_middleware(app):
    @app.before_request
    def load_tenant():
        tenant_id = request.headers.get('X-Tenant-ID')
        if not tenant_id:
            return jsonify({"error": "X-Tenant-ID header is missing"}), 400

        tenant = Tenant.query.filter_by(id=tenant_id, is_active=True).first()
        if not tenant:
            return jsonify({"error": "Invalid tenant"}), 404

        # Attach tenant to global context
        g.current_tenant = tenant