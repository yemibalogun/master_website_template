from flask import Flask, send_from_directory
from .config import config_by_name
from .extensions import db, migrate, jwt
from .api.v1 import v1_bp
from .middleware.tenant_middleware import tenant_middleware
from .errors import register_error_handlers
from flask_swagger_ui import get_swaggerui_blueprint
import os

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

     # --- Serve OpenAPI YAML ---
    @app.route("/docs/cms_openapi.yaml")
    def serve_openapi():
        # backend/docs folder
        docs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs")
        return send_from_directory(docs_dir, "cms_openapi.yaml")

    # --- Optional: Swagger UI ---
    try:
        SWAGGER_URL = "/swagger"
        API_URL = "/docs/cms_openapi.yaml"

        swaggerui_blueprint = get_swaggerui_blueprint(
            SWAGGER_URL,
            API_URL,
            config={"app_name": "CMS API"}
        )

        app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    except ImportError:
        pass  # skip if flask_swagger_ui not installed

    return app