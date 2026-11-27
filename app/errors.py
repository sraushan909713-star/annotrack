# WHAT: Makes every error return JSON instead of an HTML page.
# WHY:  API clients (React, tests) always expect JSON, even for 404 or 500.

from flask import jsonify
from werkzeug.exceptions import HTTPException
from marshmallow import ValidationError
from app.extensions import jwt


def error(message, code):
    return jsonify(error=message), code


def register_error_handlers(app):
    # handles Flask's own errors (404, 405, ...), e.g. from get_or_404
    @app.errorhandler(HTTPException)
    def handle_http_error(e):
        return error(e.description, e.code)

    # handles any crash: logs the details, but hides them from the client
    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        app.logger.exception(e)
        return error("internal server error", 500)

    # bad input anywhere -> 400 with the error for each field
    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        return jsonify(error="validation failed", details=e.messages), 400

    # JWT problems -> 401 in our usual {"error": ...} shape
    @jwt.unauthorized_loader
    def missing_token(reason):
        return error("missing or invalid token", 401)

    @jwt.invalid_token_loader
    def invalid_token(reason):
        return error("invalid token", 401)

    @jwt.expired_token_loader
    def expired_token(jwt_header, jwt_payload):
        return error("token expired, please log in again", 401)
