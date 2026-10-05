from flask import Flask

from app.extensions import db


def create_app(test_config=None):

    app = Flask(__name__)

    # Default application configuration
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI="sqlite:///deployops.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    # Override configuration when testing
    if test_config:
        app.config.update(test_config)

    # Initialize database
    db.init_app(app)

    # Import models so SQLAlchemy knows about the tables
    from app import models

    # Register API routes
    from app.routes import register_routes
    register_routes(app)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app

