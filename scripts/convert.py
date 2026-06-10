#!/usr/bin/env python3
import re
import sys
from pathlib import Path
import fitz  # pymupdf
import anthropic
from dotenv import load_dotenv


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
IMPORTANT: do NOT wrap output in a code fence or backticks. Start your response with --- directly.
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
    content = message.content[0].text.lstrip()
    # Claude occasionally wraps output in a ```yaml code fence — strip it
    content = re.sub(r'^```ya?ml?\n', '', content)
    content = re.sub(r'^---\n```\n', '---\n', content, flags=re.MULTILINE)
    return content


def write_release_notes(slug: str, content: str, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{slug}.md"
    output_path.write_text(content, encoding="utf-8")
    return output_path


def main() -> None:
    load_dotenv()
    if len(sys.argv) != 2:
        print("Usage: python convert.py <path-to-pdf>", file=sys.stderr)
        sys.exit(1)

    pdf_path = Path(sys.argv[1])
    if not pdf_path.exists():
        print(f"Error: file not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    slug = extract_version_slug(pdf_path.name)
    print(f"Processing {pdf_path.name} → {slug}.md")

    print("Extracting text from PDF...")
    text = extract_pdf_text(pdf_path)

    print("Calling Claude API...")
    client = anthropic.Anthropic()
    content = call_claude(text, client)

    output_dir = Path(__file__).parent.parent / "src" / "content" / "releases"
    output_path = write_release_notes(slug, content, output_dir)
    print(f"Written to {output_path}")


if __name__ == "__main__":
    main()
