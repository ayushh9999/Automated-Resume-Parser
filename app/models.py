"""
models.py - Database Models (Tables)

This file defines the structure of our PostgreSQL database using SQLAlchemy.
Each class below becomes a table in the database:
    - Candidate  → stores basic info (name, email, phone)
    - Skill      → stores each skill found in a resume
    - Education  → stores degrees and institutions
    - Experience → stores job titles, companies, and durations

Relationship: One Candidate has many Skills, Educations, and Experiences.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

# Create the SQLAlchemy instance (connects Python objects to database tables)
db = SQLAlchemy()


# =============================================================================
# CANDIDATE TABLE — The main table that holds each parsed resume's owner
# =============================================================================
class Candidate(db.Model):
    """Main table: one row per uploaded resume / candidate."""

    __tablename__ = "candidates"  # Actual table name in PostgreSQL

    # --- Columns ---
    id = db.Column(db.Integer, primary_key=True)          # Auto-incrementing ID
    name = db.Column(db.String(200))                      # Candidate's full name
    email = db.Column(db.String(200))                     # Email address
    phone = db.Column(db.String(50))                      # Phone number
    filename = db.Column(db.String(300), nullable=False)   # Original uploaded filename
    raw_text = db.Column(db.Text)                         # Full extracted text from resume
    created_at = db.Column(                               # Timestamp of when resume was parsed
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )

    # --- Relationships ---
    # These link a candidate to their skills, education, and experience.
    # "cascade=all, delete-orphan" means: if a candidate is deleted,
    # their skills/education/experience are deleted too (no orphan rows).
    skills = db.relationship(
        "Skill", backref="candidate", lazy=True, cascade="all, delete-orphan"
    )
    educations = db.relationship(
        "Education", backref="candidate", lazy=True, cascade="all, delete-orphan"
    )
    experiences = db.relationship(
        "Experience", backref="candidate", lazy=True, cascade="all, delete-orphan"
    )

    def to_dict(self):
        """Convert this candidate (and related data) to a JSON-friendly dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "filename": self.filename,
            "skills": [s.to_dict() for s in self.skills],
            "education": [e.to_dict() for e in self.educations],
            "experience": [e.to_dict() for e in self.experiences],
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# =============================================================================
# SKILL TABLE — Each skill found in a resume gets its own row
# =============================================================================
class Skill(db.Model):
    """One skill extracted from a resume (e.g., 'python', 'react')."""

    __tablename__ = "skills"

    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(                              # Links back to the candidate
        db.Integer, db.ForeignKey("candidates.id"), nullable=False
    )
    name = db.Column(db.String(100), nullable=False)       # Skill name, e.g., "python"
    category = db.Column(db.String(50))                    # Category: "programming", "framework", "tool", "database", "soft"

    def to_dict(self):
        """Convert to dictionary for JSON response."""
        return {"id": self.id, "name": self.name, "category": self.category}


# =============================================================================
# EDUCATION TABLE — Degrees and institutions found in the resume
# =============================================================================
class Education(db.Model):
    """One education entry (e.g., 'B.Tech in Computer Science from MIT')."""

    __tablename__ = "educations"

    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(                              # Links back to the candidate
        db.Integer, db.ForeignKey("candidates.id"), nullable=False
    )
    degree = db.Column(db.String(200))                     # e.g., "B.Tech in Computer Science"
    institution = db.Column(db.String(300))                # e.g., "MIT"
    year = db.Column(db.String(50))                        # e.g., "2018-2022" or "2020"

    def to_dict(self):
        """Convert to dictionary for JSON response."""
        return {
            "id": self.id,
            "degree": self.degree,
            "institution": self.institution,
            "year": self.year,
        }


# =============================================================================
# EXPERIENCE TABLE — Work history entries from the resume
# =============================================================================
class Experience(db.Model):
    """One work experience entry (e.g., 'Software Engineer at Google, 2020-2023')."""

    __tablename__ = "experiences"

    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(                              # Links back to the candidate
        db.Integer, db.ForeignKey("candidates.id"), nullable=False
    )
    title = db.Column(db.String(200))                      # Job title, e.g., "Software Engineer"
    company = db.Column(db.String(300))                    # Company name, e.g., "Google"
    duration = db.Column(db.String(100))                   # Time period, e.g., "Jan 2020 - Present"
    description = db.Column(db.Text)                       # Job description / bullet points

    def to_dict(self):
        """Convert to dictionary for JSON response."""
        return {
            "id": self.id,
            "title": self.title,
            "company": self.company,
            "duration": self.duration,
            "description": self.description,
        }
