import pytest

from app import create_app
from app.extensions import db


@pytest.fixture
def client():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })

    with app.app_context():
        db.drop_all()
        db.create_all()

    with app.test_client() as client:
        yield client

    with app.app_context():
        db.session.remove()
        db.drop_all()


def test_home(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.data == b"Welcome to DeployOps Platform!"


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json["status"] == "healthy"


def test_get_applications_empty(client):
    response = client.get("/applications")

    assert response.status_code == 200
    assert response.json == []


def test_create_application(client):
    response = client.post(
        "/applications",
        json={
            "name": "payment-api"
        }
    )

    assert response.status_code == 201
    assert response.json["name"] == "payment-api"


def test_get_application(client):
    client.post(
        "/applications",
        json={
            "name": "payment-api"
        }
    )

    response = client.get("/applications/1")

    assert response.status_code == 200
    assert response.json["name"] == "payment-api"


def test_create_environment(client):
    response = client.post(
        "/environments",
        json={
            "name": "staging"
        }
    )

    assert response.status_code == 201
    assert response.json["name"] == "staging"


def test_create_deployment(client):
    # Create application
    application_response = client.post(
        "/applications",
        json={
            "name": "payment-api"
        }
    )

    application_id = application_response.json["id"]

    # Create environment
    environment_response = client.post(
        "/environments",
        json={
            "name": "staging"
        }
    )

    environment_id = environment_response.json["id"]

    # Create deployment
    response = client.post(
        "/deployments",
        json={
            "application_id": application_id,
            "environment_id": environment_id,
            "version": "v1.0.0"
        }
    )

    assert response.status_code == 201
    assert response.json["application"] == "payment-api"
    assert response.json["environment"] == "staging"
    assert response.json["version"] == "v1.0.0"
    assert response.json["status"] == "PENDING"


def test_deployment_rejects_unknown_application(client):
    response = client.post(
        "/deployments",
        json={
            "application_id": 999,
            "environment_id": 1,
            "version": "v1.0.0"
        }
    )

    assert response.status_code == 404

