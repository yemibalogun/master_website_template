from flask import Flask, send_file, current_app
from .config import config_by_name
from .extensions import db, migrate, jwt
from .api.v1 import v1_bp
from .middleware.tenant_middleware import tenant_middleware
from .errors import register_error_handlers
from flask_swagger_ui import get_swaggerui_blueprint
import os


def create_app(config_name: str = "development") -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # -------------------------------------------------
    # Extensions
    # -------------------------------------------------
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # -------------------------------------------------
    # Middleware
    # -------------------------------------------------
    tenant_middleware(app)

    # -------------------------------------------------
    # API Blueprints
    # -------------------------------------------------
    app.register_blueprint(v1_bp, url_prefix="/api/v1")
    register_error_handlers(app)

    # -------------------------------------------------
    # Serve OpenAPI YAML (PUBLIC, NO TENANT)
    # -------------------------------------------------
    @app.route("/openapi/cms.yaml", methods=["GET"], endpoint="openapi_cms")
    def serve_openapi():
        spec_path = os.path.join(
            current_app.root_path,
            "api",
            "v1",
            "cms_openapi.yaml",
        )

        if not os.path.exists(spec_path):
            raise FileNotFoundError("cms_openapi.yaml not found")

        return send_file(
            spec_path,
            mimetype="application/yaml",
            as_attachment=False,
        )

    # -------------------------------------------------
    # Swagger UI
    # -------------------------------------------------
    SWAGGER_URL = "/swagger"
    API_URL = "/openapi/cms.yaml"

    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            "app_name": "CMS API",
            "deepLinking": True,
            "persistAuthorization": True,
        },
    )

    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    return app
