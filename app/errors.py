# WHAT: Makes every error return JSON instead of an HTML page.
# WHY:  API clients (React, tests) always expect JSON, even for 404 or 500.

from flask import jsonify
from werkzeug.exceptions import HTTPException


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