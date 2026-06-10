#!/usr/bin/env python3
import re
import sys
from pathlib import Path


def extract_version_slug(filename: str) -> str:
    match = re.search(r'v\d+_\d+', filename)
    if not match:
        raise ValueError(f"Could not extract version from filename: {filename}")
    return match.group()
