from datetime import datetime

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy


# --------------------------------------------------
# Database setup
# --------------------------------------------------

db = SQLAlchemy()


# --------------------------------------------------
# Database Models
# --------------------------------------------------

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(100),
        nullable=False,
        unique=True
    )

    # One application can have many deployments
    deployments = db.relationship(
        "Deployment",
        back_populates="application",
        cascade="all, delete-orphan"
    )


class Environment(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(50),
        nullable=False,
        unique=True
    )

    # One environment can have many deployments
    deployments = db.relationship(
        "Deployment",
        back_populates="environment",
        cascade="all, delete-orphan"
    )


class Deployment(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Foreign key connecting deployment to application
    application_id = db.Column(
        db.Integer,
        db.ForeignKey("application.id"),
        nullable=False
    )

    # Foreign key connecting deployment to environment
    environment_id = db.Column(
        db.Integer,
        db.ForeignKey("environment.id"),
        nullable=False
    )

    version = db.Column(
        db.String(50),
        nullable=False
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="PENDING"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    # Relationships
    application = db.relationship(
        "Application",
        back_populates="deployments"
    )

    environment = db.relationship(
        "Environment",
        back_populates="deployments"
    )


# --------------------------------------------------
# Flask Application
# --------------------------------------------------

def create_app():

    app = Flask(__name__)

    # SQLite database
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///deployops.db"

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Connect SQLAlchemy to Flask
    db.init_app(app)

    # Create database tables
    with app.app_context():
        db.create_all()

    # --------------------------------------------------
    # Home
    # --------------------------------------------------

    @app.route("/")
    def home():
        return "Welcome to DeployOps!"

    # --------------------------------------------------
    # Health Check
    # --------------------------------------------------

    @app.route("/health")
    def health():
        return jsonify({
            "status": "healthy"
        })

    # ==================================================
    # APPLICATIONS
    # ==================================================

    # GET ALL APPLICATIONS
    @app.route("/applications", methods=["GET"])
    def get_applications():

        applications = Application.query.all()

        result = [
            {
                "id": application.id,
                "name": application.name
            }
            for application in applications
        ]

        return jsonify(result)

    # CREATE APPLICATION
    @app.route("/applications", methods=["POST"])
    def create_application():

        data = request.get_json()

        if not data or "name" not in data:
            return jsonify({
                "error": "Application name is required"
            }), 400

        application = Application(
            name=data["name"]
        )

        db.session.add(application)

        try:
            db.session.commit()

        except Exception:
            db.session.rollback()

            return jsonify({
                "error": "Application name already exists"
            }), 400

        return jsonify({
            "id": application.id,
            "name": application.name
        }), 201

    # GET ONE APPLICATION
    @app.route(
        "/applications/<int:application_id>",
        methods=["GET"]
    )
    def get_application(application_id):

        application = db.session.get(
            Application,
            application_id
        )

        if not application:
            return jsonify({
                "error": "Application not found"
            }), 404

        return jsonify({
            "id": application.id,
            "name": application.name
        })

    # UPDATE APPLICATION
    @app.route(
        "/applications/<int:application_id>",
        methods=["PUT"]
    )
    def update_application(application_id):

        application = db.session.get(
            Application,
            application_id
        )

        if not application:
            return jsonify({
                "error": "Application not found"
            }), 404

        data = request.get_json()

        if not data or "name" not in data:
            return jsonify({
                "error": "Application name is required"
            }), 400

        application.name = data["name"]

        try:
            db.session.commit()

        except Exception:
            db.session.rollback()

            return jsonify({
                "error": "Application name already exists"
            }), 400

        return jsonify({
            "id": application.id,
            "name": application.name
        })

    # DELETE APPLICATION
    @app.route(
        "/applications/<int:application_id>",
        methods=["DELETE"]
    )
    def delete_application(application_id):

        application = db.session.get(
            Application,
            application_id
        )

        if not application:
            return jsonify({
                "error": "Application not found"
            }), 404

        db.session.delete(application)
        db.session.commit()

        return jsonify({
            "message": "Application deleted successfully"
        })

    # ==================================================
    # ENVIRONMENTS
    # ==================================================

    # GET ALL ENVIRONMENTS
    @app.route("/environments", methods=["GET"])
    def get_environments():

        environments = Environment.query.all()

        result = [
            {
                "id": environment.id,
                "name": environment.name
            }
            for environment in environments
        ]

        return jsonify(result)

    # CREATE ENVIRONMENT
    @app.route("/environments", methods=["POST"])
    def create_environment():

        data = request.get_json()

        if not data or "name" not in data:
            return jsonify({
                "error": "Environment name is required"
            }), 400

        environment = Environment(
            name=data["name"]
        )

        db.session.add(environment)

        try:
            db.session.commit()

        except Exception:
            db.session.rollback()

            return jsonify({
                "error": "Environment already exists"
            }), 400

        return jsonify({
            "id": environment.id,
            "name": environment.name
        }), 201

    # ==================================================
    # DEPLOYMENTS
    # ==================================================

    # GET ALL DEPLOYMENTS
    @app.route("/deployments", methods=["GET"])
    def get_deployments():

        deployments = Deployment.query.all()

        result = [
            {
                "id": deployment.id,
                "application": deployment.application.name,
                "environment": deployment.environment.name,
                "version": deployment.version,
                "status": deployment.status,
                "created_at": deployment.created_at.isoformat()
            }
            for deployment in deployments
        ]

        return jsonify(result)

    # CREATE DEPLOYMENT
    @app.route("/deployments", methods=["POST"])
    def create_deployment():

        data = request.get_json()

        required_fields = [
            "application_id",
            "environment_id",
            "version"
        ]

        # Validate required fields
        for field in required_fields:

            if field not in data:
                return jsonify({
                    "error": f"{field} is required"
                }), 400

        # Check application exists
        application = db.session.get(
            Application,
            data["application_id"]
        )

        if not application:
            return jsonify({
                "error": "Application not found"
            }), 404

        # Check environment exists
        environment = db.session.get(
            Environment,
            data["environment_id"]
        )

        if not environment:
            return jsonify({
                "error": "Environment not found"
            }), 404

        # Create deployment
        deployment = Deployment(
            application_id=data["application_id"],
            environment_id=data["environment_id"],
            version=data["version"],
            status="PENDING"
        )

        db.session.add(deployment)
        db.session.commit()

        return jsonify({
            "id": deployment.id,
            "application": application.name,
            "environment": environment.name,
            "version": deployment.version,
            "status": deployment.status,
            "created_at": deployment.created_at.isoformat()
        }), 201

    # --------------------------------------------------
    # Return Flask application
    # --------------------------------------------------

    return app


# --------------------------------------------------
# Create application
# --------------------------------------------------

app = create_app()


# --------------------------------------------------
# Run application
# --------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)

