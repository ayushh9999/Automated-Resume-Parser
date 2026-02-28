"""
config.py - Application Configuration

This file loads settings from the .env file (like database URL, secret key)
and makes them available to the Flask app. If a .env value is missing,
it falls back to a default value.
"""

import os
from dotenv import load_dotenv

# Load environment variables from the .env file in the project root
load_dotenv()


class Config:
    """Central configuration class. Flask reads all settings from here."""

    # SECRET_KEY is used by Flask to sign session cookies and protect forms.
    # In production, always use a strong random string.
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

    # PostgreSQL connection string.
    # Format: postgresql://USERNAME:PASSWORD@HOST:PORT/DATABASE_NAME
    # We use Neon DB (cloud PostgreSQL) — paste your connection string in .env
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "postgresql://postgres:password@localhost:5432/resume_parser"
    )

    # Disable Flask-SQLAlchemy event tracking (saves memory, not needed here)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Folder where uploaded resumes are temporarily saved before parsing
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")

    # Maximum file upload size: 16 MB (prevents huge files from crashing the server)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

    # Only allow these file types to be uploaded
    ALLOWED_EXTENSIONS = {"pdf", "docx"}
