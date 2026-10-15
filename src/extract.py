"""Text extraction and lookup for saved source files.

Used in Phase 2 (logging claims with page numbers) and Phase 5 (re-opening the
source for every number in the storyline).

Usage:
    python -m src.extract pages sources/raw/<file>.pdf            # page count + first lines
    python -m src.extract find  sources/raw/<file>.pdf "Turnover"  # page and line for each hit
    python -m src.extract find  sources/raw/<file>.html "Los Angeles"
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import pdfplumber
from bs4 import BeautifulSoup


def pdf_pages(path: Path) -> list[str]:
    """Text of each PDF page; index 0 is page 1."""
    with pdfplumber.open(path) as pdf:
        return [page.extract_text() or "" for page in pdf.pages]


def pdf_tables(path: Path, page_no: int) -> list[list[list[str | None]]]:
    """Tables on a 1-indexed PDF page."""
    with pdfplumber.open(path) as pdf:
        return pdf.pages[page_no - 1].extract_tables()


def html_text(path: Path) -> str:
    soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="replace"), "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return "\n".join(line.strip() for line in soup.get_text("\n").splitlines() if line.strip())


def pages(path: Path) -> list[str]:
    """Pages for a PDF; a single 'page' for HTML or text files."""
    if path.suffix.lower() == ".pdf":
        return pdf_pages(path)
    if path.suffix.lower() in (".html", ".htm"):
        return [html_text(path)]
    return [path.read_text(encoding="utf-8", errors="replace")]


def find(path: Path, pattern: str, flags: int = re.IGNORECASE) -> list[tuple[int, str]]:
    """(page number, matching line) for every line matching `pattern`."""
    rx = re.compile(pattern, flags)
    return [(i, line.strip())
            for i, text in enumerate(pages(path), start=1)
            for line in text.splitlines() if rx.search(line)]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("pages")
    p.add_argument("file", type=Path)
    f = sub.add_parser("find")
    f.add_argument("file", type=Path)
    f.add_argument("pattern")
    args = ap.parse_args(argv)

    if args.cmd == "pages":
        for i, text in enumerate(pages(args.file), start=1):
            first = next((l for l in text.splitlines() if l.strip()), "")
            print(f"p{i}: {first[:100]}")
    else:
        for page, line in find(args.file, args.pattern):
            print(f"p{page}: {line}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
