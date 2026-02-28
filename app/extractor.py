"""
extractor.py - NLP & Regex Extraction Engine

This is the brain of the resume parser. It takes the raw text extracted
from a resume (by parser.py) and pulls out structured information:

    - Name         → using spaCy's Named Entity Recognition (NER)
    - Email        → using regex pattern matching
    - Phone        → using regex pattern matching
    - Skills       → by matching against a dictionary of 100+ known skills
    - Education    → by finding degree patterns (B.Tech, MBA, etc.)
    - Experience   → by finding date ranges and job titles

Libraries used:
    - spaCy:  NLP library for detecting person names in text
    - re:     Python's built-in regex library for pattern matching
"""

import re
import spacy


# =============================================================================
# SKILL DICTIONARIES
# =============================================================================
# These sets contain known skills grouped by category.
# When we find any of these words in a resume, we flag them as a skill.
# You can easily add more skills to any category!

# Programming languages the candidate might know
PROGRAMMING_LANGUAGES = {
    "python", "java", "javascript", "typescript", "c++", "c#", "c", "ruby",
    "go", "golang", "rust", "swift", "kotlin", "scala", "php", "perl", "r",
    "matlab", "dart", "lua", "haskell", "elixir", "clojure", "shell",
    "bash", "powershell", "sql", "html", "css", "sass", "less",
}

# Frameworks and libraries (web, ML, UI, etc.)
FRAMEWORKS_AND_LIBRARIES = {
    "react", "angular", "vue", "vue.js", "next.js", "nuxt.js", "svelte",
    "django", "flask", "fastapi", "spring", "spring boot", "express",
    "node.js", "nodejs", ".net", "asp.net", "rails", "ruby on rails",
    "laravel", "symfony", "gin", "fiber", "tensorflow", "pytorch", "keras",
    "scikit-learn", "pandas", "numpy", "matplotlib", "opencv", "spacy",
    "nltk", "transformers", "hugging face", "langchain",
    "bootstrap", "tailwind", "material ui", "jquery",
}

# DevOps tools, cloud platforms, and productivity tools
TOOLS_AND_PLATFORMS = {
    "git", "github", "gitlab", "bitbucket", "docker", "kubernetes", "k8s",
    "aws", "azure", "gcp", "google cloud", "heroku", "vercel", "netlify",
    "jenkins", "travis ci", "circleci", "github actions", "terraform",
    "ansible", "vagrant", "nginx", "apache", "linux", "unix", "windows",
    "macos", "jira", "confluence", "slack", "figma", "postman",
}

# Database technologies
DATABASES = {
    "mysql", "postgresql", "postgres", "sqlite", "mongodb", "redis",
    "cassandra", "dynamodb", "firebase", "supabase", "elasticsearch",
    "neo4j", "mariadb", "oracle", "sql server", "mssql", "couchdb",
}

# Soft skills and methodologies
SOFT_SKILLS = {
    "leadership", "communication", "teamwork", "problem solving",
    "problem-solving", "critical thinking", "time management",
    "project management", "agile", "scrum", "kanban",
}

# Combine all skills into one dictionary: skill_name → category
# This makes it easy to look up both the skill and its category at once
ALL_SKILLS = {
    **{s: "programming" for s in PROGRAMMING_LANGUAGES},
    **{s: "framework" for s in FRAMEWORKS_AND_LIBRARIES},
    **{s: "tool" for s in TOOLS_AND_PLATFORMS},
    **{s: "database" for s in DATABASES},
    **{s: "soft" for s in SOFT_SKILLS},
}

# =============================================================================
# DEGREE PATTERNS — Regex to find education entries like "B.Tech", "MBA", etc.
# =============================================================================
# Each pattern matches a degree type optionally followed by a field of study.
# Example matches: "Bachelor of Science", "B.Tech in Computer Science", "MBA"
DEGREE_PATTERNS = [
    r"(?:Bachelor|B\.?S\.?|B\.?A\.?|B\.?Sc\.?|B\.?E\.?|B\.?Tech\.?)"
    r"(?:\s+(?:of|in)\s+[\w\s,]+)?",
    r"(?:Master|M\.?S\.?|M\.?A\.?|M\.?Sc\.?|M\.?E\.?|M\.?Tech\.?|MBA)"
    r"(?:\s+(?:of|in)\s+[\w\s,]+)?",
    r"(?:Ph\.?D\.?|Doctorate|Doctor of Philosophy)"
    r"(?:\s+(?:of|in)\s+[\w\s,]+)?",
    r"(?:Associate|A\.?S\.?|A\.?A\.?)"
    r"(?:\s+(?:of|in)\s+[\w\s,]+)?",
    r"(?:Diploma|Certificate)\s+(?:in\s+[\w\s,]+)?",
]

# =============================================================================
# SECTION HEADER PATTERNS — Regex to locate resume sections
# =============================================================================
# Resumes are typically divided into sections like "EDUCATION", "EXPERIENCE", etc.
# These patterns help us find where each section starts so we can extract
# the right content from the right section.
SECTION_HEADERS = {
    "education": re.compile(
        r"^(?:EDUCATION|ACADEMIC|QUALIFICATIONS|ACADEMICS)", re.IGNORECASE | re.MULTILINE
    ),
    "experience": re.compile(
        r"^(?:EXPERIENCE|WORK\s*EXPERIENCE|EMPLOYMENT|PROFESSIONAL\s*EXPERIENCE|WORK\s*HISTORY)",
        re.IGNORECASE | re.MULTILINE,
    ),
    "skills": re.compile(
        r"^(?:SKILLS|TECHNICAL\s*SKILLS|CORE\s*COMPETENCIES|TECHNOLOGIES|PROFICIENCIES)",
        re.IGNORECASE | re.MULTILINE,
    ),
}


def _load_spacy_model():
    """
    Load the spaCy English NLP model.

    We use "en_core_web_sm" which can recognize names, organizations, dates, etc.
    If it's not installed, we fall back to a blank model (name detection won't work,
    but the app won't crash).
    """
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        # Model not downloaded yet — use a basic blank model as fallback
        return spacy.blank("en")


# Load the NLP model once when this file is imported (not on every function call)
nlp = _load_spacy_model()


# =============================================================================
# CORE EXTRACTION FUNCTIONS
# =============================================================================
# Each function below extracts one type of information from the resume text.


def extract_email(text: str) -> str | None:
    """
    Find the first email address in the text using regex.

    Pattern matches: user.name+tag@example.co.in
    Returns None if no email is found.
    """
    match = re.search(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", text)
    return match.group(0) if match else None


def extract_phone(text: str) -> str | None:
    """
    Find the first phone number in the text using regex.

    Handles formats like:
        +91-9876543210, (123) 456-7890, 123.456.7890
    Returns None if no phone number is found.
    """
    patterns = [
        # International format: +91-9876543210 or +1 (123) 456-7890
        r"\+?\d{1,3}[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}",
        # US format: (123) 456-7890
        r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0).strip()
    return None


def extract_name(text: str) -> str | None:
    """
    Extract the candidate's name from the resume text.

    Strategy (two approaches, tries the best one first):
        1. Use spaCy NER to find entities labeled as "PERSON"
           (only looks at the first 500 characters — names are always at the top)
        2. Fallback: take the first line that looks like a name
           (short, only letters/spaces, no emails or numbers)
    """
    # Approach 1: Use spaCy's Named Entity Recognition
    # Feed the top of the resume to spaCy and look for PERSON entities
    doc = nlp(text[:500])  # Only process the top — names are at the beginning
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text.strip()

    # Approach 2: Fallback — guess the name from the first line
    # Skip lines that look like emails, URLs, or phone numbers
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        # Skip lines containing email, URL, or long numbers (probably not a name)
        if re.search(r"@|http|www|\d{5,}", line):
            continue
        # A name is usually short and contains only letters, spaces, dots, hyphens
        if len(line) < 60 and re.match(r"^[A-Za-z\s.\-']+$", line):
            return line
    return None


def extract_skills(text: str) -> list[dict]:
    """
    Find all skills mentioned in the resume by matching against our skill dictionary.

    How it works:
        1. Convert resume text to lowercase (so "Python" matches "python")
        2. Loop through every skill in ALL_SKILLS
        3. Search for each skill in the text
        4. For short skills (like "c" or "r"), use word boundaries to avoid
           false positives (e.g., "c" inside "company")
        5. Return a sorted list of found skills with their categories

    Returns:
        List of dicts like: [{"name": "python", "category": "programming"}, ...]
    """
    text_lower = text.lower()
    found = []
    seen = set()  # Track already-found skills to avoid duplicates

    for skill, category in ALL_SKILLS.items():
        # For very short skill names (1-2 chars like "c", "r"),
        # use word boundaries (\b) to avoid matching inside other words
        if len(skill) <= 2:
            pattern = rf"\b{re.escape(skill)}\b"
        else:
            pattern = re.escape(skill)

        # Check if this skill appears in the resume text
        if re.search(pattern, text_lower) and skill not in seen:
            found.append({"name": skill, "category": category})
            seen.add(skill)

    # Sort skills alphabetically for consistent output
    return sorted(found, key=lambda x: x["name"])


def _find_section(text: str, section: str) -> str:
    """
    Extract the text that belongs to a specific resume section.

    Example: If section="education", this finds the "EDUCATION" header
    in the resume and returns everything between it and the next section header.

    Args:
        text:     Full resume text
        section:  Section name ("education", "experience", or "skills")

    Returns:
        The text under that section, or empty string if not found.
    """
    header = SECTION_HEADERS.get(section)
    if not header:
        return ""

    # Find where this section starts
    match = header.search(text)
    if not match:
        return ""  # Section not found in resume

    start = match.end()  # Text begins right after the header

    # Find where the NEXT section starts (so we know where this one ends)
    # We check for all common resume section headers
    all_headers = re.compile(
        r"^(?:EDUCATION|ACADEMIC|QUALIFICATIONS|EXPERIENCE|WORK\s*EXPERIENCE|"
        r"EMPLOYMENT|PROFESSIONAL\s*EXPERIENCE|SKILLS|TECHNICAL\s*SKILLS|"
        r"CORE\s*COMPETENCIES|PROJECTS|CERTIFICATIONS|AWARDS|HONORS|"
        r"PUBLICATIONS|REFERENCES|SUMMARY|OBJECTIVE|PROFILE|INTERESTS|"
        r"LANGUAGES|VOLUNTEER|ACTIVITIES|HOBBIES)",
        re.IGNORECASE | re.MULTILINE,
    )

    # Look for the first section header that appears AFTER our section
    next_match = None
    for m in all_headers.finditer(text):
        if m.start() > start:
            next_match = m
            break

    # Extract text from our section start to the next section (or end of text)
    end = next_match.start() if next_match else len(text)
    return text[start:end].strip()


def extract_education(text: str) -> list[dict]:
    """
    Extract education entries (degrees, institutions, years) from the resume.

    How it works:
        1. Find the "EDUCATION" section of the resume
        2. Search for degree patterns (B.Tech, MBA, Ph.D., etc.)
        3. For each degree found, look nearby for:
           - A year or year range (e.g., "2018-2022")
           - An institution name (e.g., "IIT Delhi")
        4. Deduplicate results (same degree mentioned twice = one entry)

    Returns:
        List of dicts like:
        [{"degree": "B.Tech in CS", "institution": "IIT Delhi", "year": "2018-2022"}, ...]
    """
    # Step 1: Narrow down to the education section (if it exists)
    section = _find_section(text, "education")
    if not section:
        section = text  # Fallback: search the entire resume

    entries = []

    # Step 2: Search for each degree pattern
    for pattern in DEGREE_PATTERNS:
        for match in re.finditer(pattern, section, re.IGNORECASE):
            degree = match.group(0).strip()

            # Step 3a: Look for a year near this degree (within ~100 chars before/after)
            context = section[max(0, match.start() - 100): match.end() + 150]
            year_match = re.search(
                r"(?:19|20)\d{2}(?:\s*[-–]\s*(?:19|20)\d{2}|(?:\s*[-–]\s*(?:Present|Current)))?",
                context, re.IGNORECASE
            )
            year = year_match.group(0).strip() if year_match else None

            # Step 3b: Try to find the institution name
            # Look at lines adjacent to the degree line (above or below)
            institution = None
            lines = context.split("\n")
            for i, line in enumerate(lines):
                if degree.lower() in line.lower():
                    # Check the line below, above, and two below for institution
                    for offset in [1, -1, 2]:
                        idx = i + offset
                        if 0 <= idx < len(lines):
                            candidate_line = lines[idx].strip()
                            # Institution names don't start with digits
                            if candidate_line and not re.match(r"^\d", candidate_line):
                                institution = candidate_line
                                break
                    break

            entries.append({
                "degree": degree,
                "institution": institution,
                "year": year,
            })

    # Step 4: Remove duplicate degrees (keep the first occurrence)
    seen = set()
    unique = []
    for entry in entries:
        key = entry["degree"].lower()
        if key not in seen:
            seen.add(key)
            unique.append(entry)

    return unique


def extract_experience(text: str) -> list[dict]:
    """
    Extract work experience entries from the resume.

    How it works:
        1. Find the "EXPERIENCE" section
        2. Look for date ranges (e.g., "Jan 2020 - Present", "2019-2022")
           — each date range signals a new job entry
        3. Text before the date = job title (and possibly company)
        4. Text after the date (until the next date) = job description
        5. Try to split "Software Engineer at Google" into title + company

    Returns:
        List of dicts like:
        [{"title": "SWE", "company": "Google", "duration": "2020-2023", "description": "..."}]
    """
    # Step 1: Get only the experience section
    section = _find_section(text, "experience")
    if not section:
        return []  # No experience section found

    entries = []
    lines = section.split("\n")

    # Step 2: Define what a date range looks like
    # Matches: "Jan 2020 - Dec 2022", "2019 - Present", "March 2021 - Current"
    date_pattern = re.compile(
        r"(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*\d{4}"
        r"\s*[-–]\s*(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*\d{4}|Present|Current))"
        r"|(?:(?:19|20)\d{2}\s*[-–]\s*(?:(?:19|20)\d{2}|Present|Current))",
        re.IGNORECASE,
    )

    current_entry = None    # The job entry we're currently building
    desc_lines = []         # Collects description lines for current entry

    # Step 3: Process each line
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue  # Skip blank lines

        date_match = date_pattern.search(stripped)
        if date_match:
            # Found a new date range → this is a new job entry

            # First, save the previous entry (if any)
            if current_entry:
                current_entry["description"] = " ".join(desc_lines).strip() or None
                entries.append(current_entry)

            # Extract the duration (e.g., "Jan 2020 - Present")
            duration = date_match.group(0).strip()

            # Everything before the date is the job title + company
            title_company = stripped[: date_match.start()].strip().rstrip("|,–-").strip()

            # Step 4: Try to separate title from company
            # Look for common separators: "at", "-", "|", ","
            title, company = title_company, None
            for sep in [" at ", " - ", " | ", ", "]:
                if sep in title_company:
                    parts = title_company.split(sep, 1)
                    title = parts[0].strip()     # e.g., "Software Engineer"
                    company = parts[1].strip()   # e.g., "Google"
                    break

            current_entry = {
                "title": title or None,
                "company": company,
                "duration": duration,
            }
            desc_lines = []  # Reset description for new entry
        elif current_entry:
            # No date on this line → it's part of the job description
            desc_lines.append(stripped)

    # Don't forget to save the last entry!
    if current_entry:
        current_entry["description"] = " ".join(desc_lines).strip() or None
        entries.append(current_entry)

    return entries


def extract_all(text: str) -> dict:
    """
    Master function: runs ALL extractors on the resume text and returns
    everything in one clean dictionary.

    This is the only function that routes.py needs to call.

    Args:
        text: Raw text extracted from the resume file

    Returns:
        Dictionary with keys: name, email, phone, skills, education, experience
    """
    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
        "education": extract_education(text),
        "experience": extract_experience(text),
    }
