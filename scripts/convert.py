#!/usr/bin/env python3
import re
import sys
from pathlib import Path
import fitz  # pymupdf


def extract_version_slug(filename: str) -> str:
    match = re.search(r'v\d+_\d+', filename)
    if not match:
        raise ValueError(f"Could not extract version from filename: {filename}")
    return match.group()


def extract_pdf_text(pdf_path: Path) -> str:
    doc = fitz.open(str(pdf_path))
    pages = [page.get_text() for page in doc]
    doc.close()
    return "\n\n".join(pages)
