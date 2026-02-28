"""
app.py - Application Factory

This file creates and configures the Flask application.
It uses the "factory pattern" — a function that builds and returns
the app object. This makes testing and configuration easier.
"""

from flask import Flask
from config import Config          # Our settings (DB URL, secret key, etc.)
from app.models import db           # SQLAlchemy database instance
from app.routes import api          # All our API endpoints


def create_app(config_class=Config):
    """
    Build and return a fully configured Flask application.

    Steps:
        1. Create the Flask app
        2. Load configuration (database URL, secret key, etc.)
        3. Connect SQLAlchemy to the app (so we can talk to PostgreSQL)
        4. Register all API routes
        5. Create database tables if they don't exist yet
    """

    # Create the Flask app; tell it where to find HTML templates
    app = Flask(__name__, template_folder="templates")

    # Load all settings from our Config class (config.py)
    app.config.from_object(config_class)

    # Connect the SQLAlchemy database engine to this Flask app
    db.init_app(app)

    # Register the "api" blueprint — this adds all our routes
    # (upload, search, delete, etc.) to the app
    app.register_blueprint(api)

    # Create all database tables (candidates, skills, educations, experiences)
    # if they don't already exist in PostgreSQL
    with app.app_context():
        db.create_all()

    return app
