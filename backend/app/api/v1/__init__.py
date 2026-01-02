from flask import Blueprint

# Create the versioned blueprint
v1_bp = Blueprint("v1", __name__)

# Import route modules so they register with v1_bp
from . import health
from . import auth
from . import users
from . import protected
from . import admin
from . import cms