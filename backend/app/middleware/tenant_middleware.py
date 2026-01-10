from flask import request, g, abort
from app.models.tenant import Tenant
from app.extensions import db

# Routes that do NOT require tenant context
EXEMPT_PATH_PREFIXES = (
    "/openapi/",
    "/swagger",
    "/static/",
    "/favicon.ico",
)

def tenant_middleware(app):
    @app.before_request
    def resolve_tenant():
        # ---------------------------------------------
        # Skip tenant enforcement for exempt routes
        # ---------------------------------------------
        for prefix in EXEMPT_PATH_PREFIXES:
            if request.path.startswith(prefix):
                return  # allow through without tenant

        tenant_id = request.headers.get("X-Tenant-ID")
        if not tenant_id:
            abort(400, description="X-Tenant-ID header is missing")

        tenant = Tenant.query.filter_by(id=tenant_id, is_active=True).first()

        if not tenant:
            abort(404, description="Tenant not found")

        g.current_tenant = tenant