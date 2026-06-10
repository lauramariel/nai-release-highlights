#!/usr/bin/env python3
"""Generate a pure HTML version of release notes for pasting into Simpplr."""
import argparse
import sys
from html import escape
from pathlib import Path

import yaml


RELEASES_DIR = Path(__file__).parent.parent / "src" / "content" / "releases"


def parse_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError(f"{path}: missing frontmatter")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"{path}: malformed frontmatter")
    data = yaml.safe_load(parts[1])
    data["_body"] = parts[2].strip()
    return data


def format_date(d) -> str:
    if hasattr(d, "strftime"):
        return d.strftime("%B %-d, %Y")
    return str(d)


def category_badge(category: str) -> str:
    cat = escape(category)
    return (
        f'<span style="display:inline-block;font-size:11px;font-weight:600;'
        f"padding:2px 8px;border-radius:10px;background:#eef0ff;"
        f'color:#4a5568;margin-left:8px;">{cat}</span>'
    )


def build_html(data: dict, concise: bool = False) -> str:
    version = escape(str(data.get("version", "")))
    date_str = format_date(data.get("release_date", ""))
    summary = escape(data.get("summary", ""))
    features = data.get("features") or []
    fixed_issues = data.get("fixed_issues") or []
    known_issues = data.get("known_issues") or []
    body = data.get("_body", "")

    parts = []

    # Header
    anchor = f"v{version}".replace(".", "-")
    parts.append(
        f'<h2 id="{anchor}" style="font-size:20px;font-weight:700;margin:0 0 4px 0;">'
        f'<a href="#{anchor}" style="color:inherit;text-decoration:none;">Nutanix Enterprise AI v{version}</a>'
        f"</h2>"
    )
    parts.append(
        f'<p style="font-size:13px;color:#718096;margin:0 0 12px 0;">{escape(date_str)}</p>'
    )

    if concise:
        if features:
            parts.append('<ul style="margin:0 0 20px 0;padding-left:20px;">')
            for f in features:
                title = escape(f.get("title", ""))
                parts.append(f'<li style="margin-bottom:4px;">{title}</li>')
            parts.append("</ul>")
        return "\n".join(parts)

    parts.append(f'<p style="margin:0 0 20px 0;">{summary}</p>')

    # Features
    if features:
        parts.append(
            '<h3 style="font-size:15px;font-weight:600;margin:0 0 8px 0;'
            'border-bottom:1px solid #e2e8f0;padding-bottom:6px;">New Features</h3>'
        )
        parts.append('<ul style="margin:0 0 20px 0;padding-left:20px;">')
        for f in features:
            title = escape(f.get("title", ""))
            desc = escape(f.get("description", ""))
            cat = f.get("category", "")
            badge = category_badge(cat) if cat else ""
            parts.append(
                f"<li style=\"margin-bottom:10px;\">"
                f'<strong>{title}</strong>{badge}'
                f'<br><span style="color:#4a5568;font-size:14px;">{desc}</span>'
                f"</li>"
            )
        parts.append("</ul>")

    # Fixed Issues
    if fixed_issues:
        parts.append(
            '<h3 style="font-size:15px;font-weight:600;margin:0 0 8px 0;'
            'border-bottom:1px solid #e2e8f0;padding-bottom:6px;">Fixed Issues</h3>'
        )
        parts.append('<ul style="margin:0 0 20px 0;padding-left:20px;">')
        for issue in fixed_issues:
            title = escape(issue.get("title", ""))
            desc = escape(issue.get("description", ""))
            parts.append(
                f"<li style=\"margin-bottom:10px;\">"
                f"<strong>{title}</strong>"
                f'<br><span style="color:#4a5568;font-size:14px;">{desc}</span>'
                f"</li>"
            )
        parts.append("</ul>")

    # Known Issues
    if known_issues:
        parts.append(
            '<h3 style="font-size:15px;font-weight:600;margin:0 0 8px 0;'
            'border-bottom:1px solid #e2e8f0;padding-bottom:6px;">Known Issues</h3>'
        )
        parts.append('<ul style="margin:0 0 20px 0;padding-left:20px;">')
        for issue in known_issues:
            title = escape(issue.get("title", ""))
            desc = escape(issue.get("description", ""))
            workaround = issue.get("workaround", "")
            parts.append(
                f"<li style=\"margin-bottom:10px;\">"
                f"<strong>{title}</strong>"
                f'<br><span style="color:#4a5568;font-size:14px;">{desc}</span>'
            )
            if workaround:
                parts.append(
                    f'<br><span style="color:#4a5568;font-size:14px;">'
                    f"<em>Workaround:</em> {escape(workaround)}</span>"
                )
            parts.append("</li>")
        parts.append("</ul>")

    # Body prose (plain text — newlines become <br> pairs)
    if body:
        body_html = escape(body).replace("\n\n", "</p><p>").replace("\n", "<br>")
        parts.append(f'<p style="margin:0 0 20px 0;">{body_html}</p>')

    return "\n".join(parts)


def load_all_releases() -> list[tuple[str, dict]]:
    releases = []
    for path in sorted(RELEASES_DIR.glob("*.md")):
        data = parse_frontmatter(path)
        releases.append((path.stem, data))
    # Sort descending by version number
    releases.sort(key=lambda x: [int(n) for n in str(x[1]["version"]).split(".")], reverse=True)
    return releases


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate HTML release notes for Simpplr")
    parser.add_argument(
        "--version", "-v",
        help="Version to export (e.g. 2.7). Omit to export all versions.",
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path. Defaults to stdout.",
    )
    parser.add_argument(
        "--concise", "-c",
        action="store_true",
        help="Output only version, date, and feature titles.",
    )
    args = parser.parse_args()

    if args.version:
        slug = "v" + args.version.replace(".", "_")
        path = RELEASES_DIR / f"{slug}.md"
        if not path.exists():
            print(f"Error: no release found for version {args.version}", file=sys.stderr)
            sys.exit(1)
        data = parse_frontmatter(path)
        html = build_html(data, concise=args.concise)
    else:
        releases = load_all_releases()
        if not releases:
            print("Error: no release files found", file=sys.stderr)
            sys.exit(1)
        blocks = []
        for _, data in releases:
            blocks.append(build_html(data, concise=args.concise))
        divider = '\n<hr style="border:none;border-top:2px solid #e2e8f0;margin:32px 0;">\n'
        html = divider.join(blocks)

    if args.output:
        Path(args.output).write_text(html, encoding="utf-8")
        print(f"Written to {args.output}")
    else:
        print(html)


if __name__ == "__main__":
    main()
