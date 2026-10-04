from datetime import datetime

from app.extensions import db


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(100),
        nullable=False,
        unique=True
    )

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

    deployments = db.relationship(
        "Deployment",
        back_populates="environment",
        cascade="all, delete-orphan"
    )


class Deployment(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    application_id = db.Column(
        db.Integer,
        db.ForeignKey("application.id"),
        nullable=False
    )

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

    application = db.relationship(
        "Application",
        back_populates="deployments"
    )

    environment = db.relationship(
        "Environment",
        back_populates="deployments"
    )