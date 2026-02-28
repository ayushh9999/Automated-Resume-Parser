"""
routes.py - API Endpoints (All the URLs the App Responds To)

This file defines what happens when a user:
    - Visits the homepage          → GET  /
    - Uploads a resume             → POST /api/upload
    - Views all candidates         → GET  /api/candidates
    - Views a single candidate     → GET  /api/candidates/<id>
    - Deletes a candidate          → DELETE /api/candidates/<id>
    - Searches by skills           → GET  /api/search/skills?skills=python,flask

The upload endpoint is the most important — it:
    1. Saves the uploaded file temporarily
    2. Extracts text from it (parser.py)
    3. Runs NLP extraction (extractor.py)
    4. Saves the results to the database (models.py)
    5. Deletes the temporary file
"""

import os
from flask import Blueprint, request, jsonify, render_template, current_app
from werkzeug.utils import secure_filename  # Sanitizes filenames to prevent attacks
from app.models import db, Candidate, Skill, Education, Experience
from app.parser import extract_text       # Step 2: file → raw text
from app.extractor import extract_all     # Step 3: raw text → structured data

# Create a Blueprint — a way to organize routes into a separate module
# instead of putting everything in app.py
api = Blueprint("api", __name__)


def _normalize_email(value: str | None) -> str | None:
    """Normalize email for consistent matching (trim + lowercase)."""
    if not value:
        return None
    return value.strip().lower()


def _normalize_phone(value: str | None) -> str | None:
    """Normalize phone for matching by keeping only digits."""
    if not value:
        return None
    digits = "".join(char for char in value if char.isdigit())
    return digits or None


def _find_existing_candidate(data: dict) -> Candidate | None:
    """
    Try to find an existing candidate so re-uploads update instead of duplicating.

    Matching priority:
        1) Email (most reliable)
        2) Phone (normalized digits)
    """
    normalized_email = _normalize_email(data.get("email"))
    if normalized_email:
        existing = Candidate.query.filter(
            db.func.lower(Candidate.email) == normalized_email
        ).first()
        if existing:
            return existing

    normalized_phone = _normalize_phone(data.get("phone"))
    if normalized_phone:
        candidates_with_phone = Candidate.query.filter(Candidate.phone.isnot(None)).all()
        for candidate in candidates_with_phone:
            if _normalize_phone(candidate.phone) == normalized_phone:
                return candidate

    return None


def _allowed_file(filename: str) -> bool:
    """
    Check if the uploaded file has an allowed extension (PDF or DOCX).
    Returns True if allowed, False otherwise.
    """
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in current_app.config["ALLOWED_EXTENSIONS"]
    )


# =============================================================================
# HOMEPAGE — Serves the web UI
# =============================================================================


@api.route("/")
def index():
    """Serve the main upload page (index.html)."""
    return render_template("index.html")


# =============================================================================
# UPLOAD & PARSE — The core endpoint that processes resumes
# =============================================================================


@api.route("/api/upload", methods=["POST"])
def upload_resume():
    """
    Upload a resume file, parse it, extract information, and save to database.

    Flow:
        1. Validate the uploaded file (exists? correct type?)
        2. Save it temporarily to disk
        3. Extract raw text from PDF/DOCX
        4. Run NLP extraction to get name, email, skills, etc.
        5. Save all extracted data to PostgreSQL
        6. Delete the temporary file
        7. Return the parsed data as JSON
    """

    # --- Validation ---
    # Check if a file was actually included in the request
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    # Only allow PDF and DOCX files
    if not _allowed_file(file.filename):
        return jsonify({"error": "File type not allowed. Use PDF or DOCX."}), 400

    # --- Save the file temporarily ---
    upload_dir = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)  # Create uploads/ folder if it doesn't exist
    filename = secure_filename(file.filename)  # Sanitize filename (remove dangerous chars)
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)  # Write file to disk

    try:
        # --- Step 1: Extract text from the file ---
        raw_text = extract_text(filepath)
        if not raw_text.strip():
            return jsonify({"error": "Could not extract text from the file."}), 422

        # --- Step 2: Run NLP extraction ---
        # This returns a dict with: name, email, phone, skills, education, experience
        data = extract_all(raw_text)

        # --- Step 3: Save to database (upsert behavior) ---
        # If the candidate already exists, update that row instead of creating a duplicate.
        # Identity matching uses email first, then normalized phone.
        candidate = _find_existing_candidate(data)
        is_update = candidate is not None

        if is_update:
            candidate.name = data["name"] or candidate.name
            candidate.email = data["email"] or candidate.email
            candidate.phone = data["phone"] or candidate.phone
            candidate.filename = filename
            candidate.raw_text = raw_text

            # Replace old extracted details with the latest resume content
            candidate.skills.clear()
            candidate.educations.clear()
            candidate.experiences.clear()
            db.session.flush()
        else:
            candidate = Candidate(
                name=data["name"],
                email=data["email"],
                phone=data["phone"],
                filename=filename,
                raw_text=raw_text,
            )
            db.session.add(candidate)
            db.session.flush()  # Flush to get the auto-generated candidate.id

        # Save each skill as a separate row linked to this candidate
        for skill in data["skills"]:
            db.session.add(
                Skill(
                    candidate_id=candidate.id,
                    name=skill["name"],
                    category=skill["category"],
                )
            )

        # Save each education entry
        for edu in data["education"]:
            db.session.add(
                Education(
                    candidate_id=candidate.id,
                    degree=edu.get("degree"),
                    institution=edu.get("institution"),
                    year=edu.get("year"),
                )
            )

        # Save each work experience entry
        for exp in data["experience"]:
            db.session.add(
                Experience(
                    candidate_id=candidate.id,
                    title=exp.get("title"),
                    company=exp.get("company"),
                    duration=exp.get("duration"),
                    description=exp.get("description"),
                )
            )

        # Commit all changes to the database at once
        db.session.commit()

        # Return the parsed candidate data as JSON
        if is_update:
            return jsonify(
                {
                    "message": "Existing candidate updated successfully",
                    "candidate": candidate.to_dict(),
                }
            ), 200

        return jsonify(
            {"message": "Resume parsed successfully", "candidate": candidate.to_dict()}
        ), 201

    except Exception as e:
        # Something went wrong — undo all database changes
        db.session.rollback()
        return jsonify({"error": f"Failed to parse resume: {str(e)}"}), 500
    finally:
        # Always clean up: delete the temporary uploaded file
        if os.path.exists(filepath):
            os.remove(filepath)


# =============================================================================
# CANDIDATE ENDPOINTS — List, View, Delete candidates
# =============================================================================


@api.route("/api/candidates", methods=["GET"])
def list_candidates():
    """
    List all candidates, optionally filtered by a search query.

    Query params:
        ?q=searchterm  → searches in name, email, and full resume text

    Returns:
        JSON array of all matching candidates (newest first)
    """
    query = request.args.get("q", "").strip()

    # Start with all candidates
    candidates_query = Candidate.query

    # If a search term was provided, filter results
    if query:
        search = f"%{query}%"  # SQL LIKE pattern: %term%
        candidates_query = candidates_query.filter(
            db.or_(
                Candidate.name.ilike(search),      # Search in name
                Candidate.email.ilike(search),     # Search in email
                Candidate.raw_text.ilike(search),  # Search in full resume text
            )
        )

    # Return results sorted by newest first
    candidates = candidates_query.order_by(Candidate.created_at.desc()).all()
    return jsonify([c.to_dict() for c in candidates])


@api.route("/api/candidates/<int:candidate_id>", methods=["GET"])
def get_candidate(candidate_id: int):
    """Get a single candidate by their database ID. Returns 404 if not found."""
    candidate = Candidate.query.get_or_404(candidate_id)
    return jsonify(candidate.to_dict())


@api.route("/api/candidates/<int:candidate_id>", methods=["DELETE"])
def delete_candidate(candidate_id: int):
    """
    Delete a candidate and all their related data (skills, education, experience).
    The cascade setting in models.py ensures related rows are deleted too.
    """
    candidate = Candidate.query.get_or_404(candidate_id)
    db.session.delete(candidate)
    db.session.commit()
    return jsonify({"message": "Candidate deleted"}), 200


# =============================================================================
# SKILL SEARCH — Find candidates who have specific skills
# =============================================================================


@api.route("/api/search/skills", methods=["GET"])
def search_by_skills():
    """
    Search for candidates who have specific skills.

    Usage:
        GET /api/search/skills?skills=python,flask,docker

    How it works:
        1. Split the comma-separated skills from the query string
        2. JOIN the candidates table with skills table
        3. Filter for candidates who have ANY of the requested skills
        4. Return unique candidates (DISTINCT prevents duplicates)
    """
    skills_param = request.args.get("skills", "").strip()
    if not skills_param:
        return jsonify({"error": "Provide ?skills=python,flask,..."}), 400

    # Split "python,flask,docker" into ["python", "flask", "docker"]
    skill_names = [s.strip().lower() for s in skills_param.split(",") if s.strip()]

    # Query: find candidates who have at least one of the requested skills
    candidates = (
        Candidate.query.join(Skill)                              # JOIN with skills table
        .filter(db.func.lower(Skill.name).in_(skill_names))     # WHERE skill IN (...)
        .distinct()                                              # Remove duplicate candidates
        .all()
    )

    return jsonify([c.to_dict() for c in candidates])
