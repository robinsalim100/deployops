from flask import Flask

from app.extensions import db


def create_app():

    app = Flask(__name__)

    # SQLite configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///deployops.db"

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize database
    db.init_app(app)

    # Import models so SQLAlchemy knows about the tables
    from app import models

    # Register API routes
    from app.routes import register_routes
    register_routes(app)

    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()

    return app