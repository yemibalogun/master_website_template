from flask import Flask
from .config import config_by_name
from .extensions import db, migrate, jwt
from .api.v1 import v1_bp
from .middleware.tenant_middleware import tenant_middleware
from .errors import register_error_handlers

def create_app(config_name="development"):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Register middleware
    tenant_middleware(app)

    # Register versioned API blueprints
    app.register_blueprint(v1_bp, url_prefix='/api/v1')
    register_error_handlers(app)
    
    return app