# WHAT: A simple /health endpoint that returns {"status": "ok"}.
# WHY:  Docker, AWS and monitoring tools call it to check the app is running.

from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health():
    return jsonify(status="ok"), 200