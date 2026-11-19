# WHAT: Creates the Flask app and connects everything (config, database, routes).
# WHY:  One place to build the app. Tests can build their own app with test settings.

from flask import Flask

from config import Config
from app.extensions import db, migrate


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # connect database and migrations to this app
    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)

    # needed so migrations can find our tables
    from app import models  # noqa: F401

    # add the routes
    from app.routes.health import health_bp
    app.register_blueprint(health_bp)

    from app.routes.batches import batches_bp
    app.register_blueprint(batches_bp)

    from app.routes.scenes import scenes_bp
    app.register_blueprint(scenes_bp)

    # every error returns JSON
    from app.errors import register_error_handlers
    register_error_handlers(app)

    return app