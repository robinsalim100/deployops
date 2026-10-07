import os

from flask import Flask

from app.extensions import db


def create_app(test_config=None):

    app = Flask(__name__)

    # Use PostgreSQL when DATABASE_URL is provided.
    # Otherwise use local SQLite.
    database_url = os.getenv(
        "DATABASE_URL",
        "sqlite:///deployops.db"
    )

    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI=database_url,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    # Test configuration can override the default configuration.
    if test_config:
        app.config.update(test_config)

    # Initialize database
    db.init_app(app)

    # Import models so SQLAlchemy knows about the tables
    from app import models

    # Register API routes
    from app.routes import register_routes
    register_routes(app)

    # Create tables
    with app.app_context():
        db.create_all()

    return app