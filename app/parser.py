"""
parser.py - Resume File Reader

This module handles the first step of resume parsing:
reading the actual file (PDF or DOCX) and converting it to plain text.

The extracted text is then passed to extractor.py for NLP analysis.

Libraries used:
    - pdfplumber: Reads text from PDF files (handles tables, columns, etc.)
    - python-docx: Reads text from Microsoft Word (.docx) files
"""

import pdfplumber
from docx import Document


def extract_text_from_pdf(file_path: str) -> str:
    """
    Read a PDF file and return all its text as a single string.

    How it works:
        1. Open the PDF file
        2. Loop through each page
        3. Extract text from each page
        4. Join all pages with newlines
    """
    text_parts = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()  # Get text from this page
            if page_text:  # Skip blank pages
                text_parts.append(page_text)
    return "\n".join(text_parts)


def extract_text_from_docx(file_path: str) -> str:
    """
    Read a DOCX (Word) file and return all its text as a single string.

    How it works:
        1. Open the .docx file
        2. Loop through each paragraph
        3. Skip empty paragraphs
        4. Join all paragraphs with newlines
    """
    doc = Document(file_path)
    return "\n".join(para.text for para in doc.paragraphs if para.text.strip())


def extract_text(file_path: str) -> str:
    """
    Main function: detect the file type and extract text accordingly.

    Args:
        file_path: Path to the uploaded resume file

    Returns:
        The full text content of the resume as a string

    Raises:
        ValueError: If the file is not a PDF or DOCX
    """
    lower = file_path.lower()
    if lower.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif lower.endswith(".docx"):
        return extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_path}")
