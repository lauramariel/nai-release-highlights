#!/usr/bin/env python3
import re
import sys
from pathlib import Path
import fitz  # pymupdf
import anthropic


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


SYSTEM_PROMPT = """You are a technical writer. Extract structured information from Nutanix Enterprise AI release notes and return ONLY a markdown document with YAML frontmatter.

The frontmatter MUST follow this exact schema:
---
version: "X.Y"
release_date: YYYY-MM-DD
summary: "One or two sentence overview of this release."
features:
  - title: "Feature Title"
    description: "What the feature does."
    category: "Category (e.g. Performance, API, Security, MLOps, Platform, Core)"
---

IMPORTANT: version MUST be a quoted string (e.g. version: "2.8"), never a bare number.
IMPORTANT: omit the workaround field entirely for known_issues entries that have no workaround.
After the closing ---, include the full release notes as markdown prose. Output nothing before the opening ---."""


def call_claude(text: str, client: anthropic.Anthropic) -> str:
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Extract structured release notes from this document:\n\n{text}",
            }
        ],
    )
    return message.content[0].text.lstrip()


def write_release_notes(slug: str, content: str, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{slug}.md"
    output_path.write_text(content, encoding="utf-8")
    return output_path
