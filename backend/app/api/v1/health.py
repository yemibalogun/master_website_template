from flask import Blueprint, jsonify
from . import v1_bp

@v1_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "ok",
        "service": "backend-platform"
    })