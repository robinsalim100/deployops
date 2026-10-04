from flask import jsonify, request

from app.extensions import db
from app.models import Application, Environment, Deployment


def register_routes(app):

    # ----------------------------------------------
    # Home
    # ----------------------------------------------

    @app.route("/")
    def home():
        return "Welcome to DeployOps Platform!"

    # ----------------------------------------------
    # Health
    # ----------------------------------------------

    @app.route("/health")
    def health():
        return jsonify({
            "status": "healthy"
        })

    # ==============================================
    # APPLICATIONS
    # ==============================================

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

    # ==============================================
    # ENVIRONMENTS
    # ==============================================

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

    # ==============================================
    # DEPLOYMENTS
    # ==============================================

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

    @app.route("/deployments", methods=["POST"])
    def create_deployment():

        data = request.get_json()

        if not data:
            return jsonify({
                "error": "Request body is required"
            }), 400

        required_fields = [
            "application_id",
            "environment_id",
            "version"
        ]

        for field in required_fields:
            if field not in data:
                return jsonify({
                    "error": f"{field} is required"
                }), 400

        application = db.session.get(
            Application,
            data["application_id"]
        )

        if not application:
            return jsonify({
                "error": "Application not found"
            }), 404

        environment = db.session.get(
            Environment,
            data["environment_id"]
        )

        if not environment:
            return jsonify({
                "error": "Environment not found"
            }), 404

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