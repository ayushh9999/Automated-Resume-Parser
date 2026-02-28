<div align="center">

# 📄 Automated Resume Parser

### 🤖 AI-powered resume analysis — extract, categorize & search candidate data instantly

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![spaCy](https://img.shields.io/badge/spaCy-NLP-09A3D5?style=for-the-badge&logo=spacy&logoColor=white)](https://spacy.io)

<br>

**Upload a PDF or DOCX resume** → Get structured candidate data in seconds

*Name · Email · Phone · Skills · Education · Work Experience*

</div>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📤 **Drag & Drop Upload** | Upload PDF or DOCX resumes via an intuitive drag-and-drop UI |
| 🧠 **AI Name Detection** | Uses spaCy NER (Named Entity Recognition) to identify candidate names |
| 📧 **Contact Extraction** | Automatically pulls out email addresses and phone numbers |
| 💻 **Skill Categorization** | Detects 100+ skills and sorts them into categories: `programming`, `framework`, `tool`, `database`, `soft` |
| 🎓 **Education Parsing** | Finds degrees (B.Tech, MBA, Ph.D., etc.), institutions, and graduation years |
| 💼 **Experience Parsing** | Extracts job titles, companies, durations, and descriptions |
| 🔍 **Smart Search** | Search candidates by name, email, keywords, or comma-separated skills |
| 🗑️ **CRUD Operations** | View, search, and delete candidate records through the UI and API |
| 🐘 **PostgreSQL Storage** | All data stored in a relational database with full foreign key relationships |

---

## 🛠️ Tech Stack

<table>
<tr><td><strong>Layer</strong></td><td><strong>Technology</strong></td><td><strong>Purpose</strong></td></tr>
<tr><td>🐍 Backend</td><td>Python, Flask</td><td>Web server & API</td></tr>
<tr><td>🧠 NLP</td><td>spaCy (<code>en_core_web_sm</code>)</td><td>Name entity recognition</td></tr>
<tr><td>📄 PDF Parsing</td><td>PDFPlumber</td><td>Extract text from PDFs</td></tr>
<tr><td>📝 DOCX Parsing</td><td>python-docx</td><td>Extract text from Word files</td></tr>
<tr><td>🐘 Database</td><td>PostgreSQL + SQLAlchemy</td><td>Persistent data storage</td></tr>
<tr><td>🎨 Frontend</td><td>HTML / CSS / JavaScript</td><td>Upload UI & results display</td></tr>
</table>

---

## ⚙️ How It Works

```
┌──────────────┐     ┌───────────────┐     ┌─────────────────┐     ┌──────────────┐
│  📤 Upload   │────▶│  📖 Extract   │────▶│  🧠 NLP Parse   │────▶│  🐘 Store    │
│  PDF / DOCX  │     │  Raw Text     │     │  Name, Skills…  │     │  PostgreSQL  │
└──────────────┘     └───────────────┘     └─────────────────┘     └──────────────┘
                      PDFPlumber /          spaCy NER +              SQLAlchemy
                      python-docx           Regex Patterns           ORM
```

### Step-by-step:

1. **📤 Upload** — User uploads a PDF or DOCX resume via the web UI or API
2. **📖 Text Extraction** — `PDFPlumber` (PDF) or `python-docx` (DOCX) converts the file to plain text
3. **🧠 NLP Processing** — spaCy's NER identifies names; regex patterns extract emails, phones, education & experience
4. **💻 Skill Matching** — A curated dictionary of **100+ skills** is matched against the text, auto-categorized by type
5. **🐘 Database Storage** — Extracted data is saved across **4 relational tables** with foreign key relationships
6. **🔍 Search** — Full-text and skill-based search lets you query the entire candidate database

---

## 📁 Project Structure

```
resume-parser/
│
├── 🚀 run.py                  # Entry point — start the app here
├── ⚙️ config.py               # Configuration (DB URL, upload limits, secrets)
├── 📦 requirements.txt        # Python dependencies
├── 🔒 .env.example            # Environment variable template
├── 🙈 .gitignore              # Git ignore rules
│
└── app/
    ├── __init__.py             # Package initializer
    ├── 🏭 app.py              # Flask application factory
    ├── 🗃️ models.py           # Database models (4 tables)
    ├── 📖 parser.py           # PDF & DOCX text extraction
    ├── 🧠 extractor.py        # NLP + regex extraction engine
    ├── 🛣️ routes.py           # API endpoints (upload, search, CRUD)
    └── templates/
        └── 🎨 index.html      # Single-page web UI
```

---

## 🚀 Quick Start

### Prerequisites

- 🐍 **Python 3.10+**
- 🐘 **PostgreSQL** (local or cloud — [Neon DB](https://neon.tech) works great!)

### 1️⃣ Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/resume-parser.git
cd resume-parser
```

### 2️⃣ Create the database

```sql
-- In psql or your database tool:
CREATE DATABASE resume_parser;
```

> 💡 **Using Neon DB?** Just create a project in the [Neon Console](https://console.neon.tech) — no local PostgreSQL needed!

### 3️⃣ Set up environment variables

```bash
cp .env.example .env
```

Edit `.env` with your database credentials:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/resume_parser
SECRET_KEY=your-secret-key-here
UPLOAD_FOLDER=uploads
```

### 4️⃣ Install dependencies

```bash
# Create & activate virtual environment
python -m venv venv
venv\Scripts\activate        # 🪟 Windows
# source venv/bin/activate   # 🍎 macOS / 🐧 Linux

# Install packages
pip install -r requirements.txt

# Download the spaCy NLP model (required for name detection)
python -m spacy download en_core_web_sm
```

### 5️⃣ Run the app

```bash
python run.py
```

```
==================================================
  Resume Parser — http://127.0.0.1:5000
==================================================
 * Running on http://127.0.0.1:5000
```

🎉 Open **http://127.0.0.1:5000** in your browser and start uploading resumes!

---

## 🔌 API Reference

All endpoints return JSON responses.

| Method | Endpoint | Description | Example |
|--------|----------|-------------|---------|
| `GET` | `/` | 🎨 Web UI | Browser |
| `POST` | `/api/upload` | 📤 Upload & parse a resume | `curl -F file=@resume.pdf localhost:5000/api/upload` |
| `GET` | `/api/candidates` | 📋 List all candidates | `?q=john` for search |
| `GET` | `/api/candidates/<id>` | 👤 Get single candidate | `/api/candidates/1` |
| `DELETE` | `/api/candidates/<id>` | 🗑️ Delete a candidate | `/api/candidates/1` |
| `GET` | `/api/search/skills` | 🔍 Search by skills | `?skills=python,flask,docker` |

### 📤 Upload Example (cURL)

```bash
curl -X POST -F "file=@resume.pdf" http://127.0.0.1:5000/api/upload
```

### 📋 Response Example

```json
{
  "message": "Resume parsed successfully",
  "candidate": {
    "id": 1,
    "name": "Ayush Mondal",
    "email": "ayush@example.com",
    "phone": "+91-9876543210",
    "skills": [
      { "name": "python", "category": "programming" },
      { "name": "flask", "category": "framework" },
      { "name": "postgresql", "category": "database" }
    ],
    "education": [
      { "degree": "B.Tech in Computer Science", "institution": "IIT Delhi", "year": "2018-2022" }
    ],
    "experience": [
      { "title": "Software Engineer", "company": "Google", "duration": "2022 - Present", "description": "..." }
    ]
  }
}
```

---

## 🗄️ Database Schema

The app uses **4 related tables**:

```
┌─────────────────┐       ┌──────────────┐
│   candidates    │──────▶│    skills     │
│─────────────────│  1:N  │──────────────│
│ id              │       │ id           │
│ name            │       │ candidate_id │
│ email           │       │ name         │
│ phone           │       │ category     │
│ filename        │       └──────────────┘
│ raw_text        │
│ created_at      │       ┌──────────────┐
│                 │──────▶│  educations  │
│                 │  1:N  │──────────────│
│                 │       │ id           │
│                 │       │ candidate_id │
│                 │       │ degree       │
│                 │       │ institution  │
│                 │       │ year         │
│                 │       └──────────────┘
│                 │
│                 │       ┌──────────────┐
│                 │──────▶│ experiences  │
│                 │  1:N  │──────────────│
│                 │       │ id           │
│                 │       │ candidate_id │
│                 │       │ title        │
│                 │       │ company      │
│                 │       │ duration     │
│                 │       │ description  │
└─────────────────┘       └──────────────┘
```

---

## 💡 Skills Detected

The parser recognizes **100+ skills** across 5 categories:

| Category | Examples |
|----------|----------|
| 💻 **Programming** | Python, Java, JavaScript, TypeScript, C++, Go, Rust, SQL, HTML, CSS… |
| 📚 **Frameworks** | React, Angular, Django, Flask, Spring Boot, TensorFlow, PyTorch, Node.js… |
| 🔧 **Tools** | Git, Docker, Kubernetes, AWS, Azure, Jenkins, Terraform, Linux, Postman… |
| 🗄️ **Databases** | PostgreSQL, MongoDB, MySQL, Redis, Firebase, Elasticsearch, DynamoDB… |
| 🤝 **Soft Skills** | Leadership, Communication, Agile, Scrum, Project Management… |

> 📝 **Want to add more skills?** Edit the skill dictionaries at the top of `app/extractor.py`

---

## 🤝 Contributing

Contributions are welcome! Here are some ideas:

- 🌐 Add support for more file formats (`.txt`, `.rtf`)
- 🧠 Improve NLP extraction accuracy with custom spaCy models
- 📊 Add a dashboard with charts and analytics
- 🔐 Add user authentication
- 🐳 Add Docker support for easy deployment

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<div align="center">

**⭐ Star this repo if you found it useful!**

Made with ❤️ using Python, Flask & spaCy

</div>
