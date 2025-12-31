from functools import wraps
from flask import g, jsonify
from flask_jwt_extended import get_jwt_identity

def tenant_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        tenant = g.current_tenant
        if not tenant:
            return jsonify({"error": "Tenant context missing"}), 400

        identity = get_jwt_identity()
        if identity.get("tenant_id") != tenant.id:
            return jsonify({"error": "Tenant mismatch"}), 403

        return fn(*args, **kwargs)
    return wrapper

def roles_required(*allowed_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            identity = get_jwt_identity()

            if identity.get("role") not in allowed_roles:
                return jsonify({"error": "Insufficient permissions"}), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def feature_enabled(feature_name):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            tenant = g.current_tenant

            if not hasattr(tenant, feature_name):
                return jsonify({"error": "Feature not recognized"}), 400

            if not getattr(tenant, feature_name):
                return jsonify({
                    "error": f"Feature '{feature_name}' is disabled for this tenant"
                }), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator
