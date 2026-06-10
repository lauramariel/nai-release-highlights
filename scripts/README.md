# Script Usage

## Script: scripts/convert.py

Converts a Nutanix Enterprise AI release notes PDF into a structured markdown file
with YAML frontmatter, stored in `src/content/releases/`. The filename must contain
a version slug in the form `vX_Y` (e.g. `v2_8`).

### Setup

```bash
pip install -r scripts/requirements.txt
```

Create a `.env` file in the project root with your Anthropic API key:

```
ANTHROPIC_API_KEY=sk-ant-...
```

### Usage

```bash
python scripts/convert.py source_pdfs/Release-Notes-Nutanix-Enterprise-AI-v2_8.pdf
```

This will:
1. Extract all text from the PDF using PyMuPDF
2. Send the text to Claude (`claude-sonnet-4-6`) to extract structured data
3. Write the result to `src/content/releases/v2_8.md`

After running, rebuild the site to pick up the new file:

```bash
npm run build
```

### Running tests

```bash
cd scripts
pytest test_convert.py -v
```

The tests cover version slug extraction, PDF text extraction (using real in-memory PDFs),
the Claude API call (mocked), and file writing. No API key is required to run the tests.

---

## Script: scripts/generate_html.py

This script generates a pure HTML version of release notes for pasting into Simpplr.

### Single version → stdout (copy-paste directly)
python3 scripts/generate_html.py --version 2.7

### Single version → file
python3 scripts/generate_html.py --version 2.7 --output release_2.7.html

### All versions combined → file (newest first, separated by `<hr>`)
python3 scripts/generate_html.py --output release_notes_all.html

### All versions, concise
python3 scripts/generate_html.py --concise

### Single version, concise
python3 scripts/generate_html.py --concise --version 2.7