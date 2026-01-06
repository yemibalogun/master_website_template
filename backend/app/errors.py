from flask import jsonify
from app.domain.invariants.exceptions import InvariantViolation

def register_error_handlers(app):
    @app.errorhandler(InvariantViolation)
    def handle_invariant_violation(error):
        response = jsonify({
            "error": "InvariantViolation",
            "message": str(error)
        })
        response.status_code = 400
        return response