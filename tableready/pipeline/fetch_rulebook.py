#!/usr/bin/env python3
"""Fetch a rulebook PDF and turn it into text for writing an entry.

    python3 pipeline/fetch_rulebook.py <slug> <url> [<fallback url> ...]

Tries each URL in order and keeps the first real PDF. The PDF and its text go
to .cache/rulebooks/ (not committed: rulebooks are the publishers' work; the
database stores only facts restated in our own words, plus the link).

Needs `curl` and poppler's `pdftotext` / `pdfinfo` on the PATH.
"""
import re
import subprocess
import sys
from pathlib import Path

CACHE = Path(__file__).resolve().parent.parent / ".cache" / "rulebooks"
AGENT = "Mozilla/5.0 (compatible; rulebook-reader)"


def fetch(slug, urls):
    CACHE.mkdir(parents=True, exist_ok=True)
    pdf = CACHE / f"{slug}.pdf"
    for url in urls:
        done = subprocess.run(
            ["curl", "-sSL", "--max-time", "60", "-A", AGENT, "-o", str(pdf), "-w", "%{http_code}", url],
            capture_output=True, text=True,
        )
        if pdf.exists() and pdf.read_bytes()[:4] == b"%PDF":
            return pdf, url
        print(f"not a PDF (http {done.stdout.strip() or '?'}): {url}")
    return None, None


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    slug, urls = sys.argv[1], sys.argv[2:]
    pdf, url = fetch(slug, urls)
    if pdf is None:
        print("No usable PDF. Try another source.")
        return 1
    text_path = pdf.with_suffix(".txt")
    subprocess.run(["pdftotext", str(pdf), str(text_path)], check=True)  # reading order, not page layout
    text = text_path.read_text(encoding="utf-8", errors="ignore")
    info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
    pages = re.search(r"Pages:\s+(\d+)", info)
    words = re.findall(r"[A-Za-z]{4,}", text)
    shouting = sum(1 for w in words if w.isupper()) / len(words) if words else 1.0

    print(f"source   {url}")
    print(f"pages    {pages.group(1) if pages else '?'}")
    print(f"text     {len(text)} characters -> {text_path}")
    if len(text) < 1500:
        print("WARNING  very little text: this may be a packaging sheet or a scanned image, not the rules.")
    if shouting > 0.5:
        print(f"WARNING  {shouting:.0%} of words are all capitals: the text layer is probably broken; read the PDF as images.")
    print("\nLines that mention player counts (a starting point, not the entry):")
    seen = 0
    for line in re.sub(r"[ \t]+", " ", text).splitlines():
        if re.search(r"\b\d\s*(-|–|or|to)?\s*\d?\s*-?\s*players?\b|\bplayer game\b", line, re.I) and len(line) > 12:
            print("  " + line.strip()[:150])
            seen += 1
            if seen == 12:
                break
    print("\nCheck the edition before writing: the first hit is often a variant or an older printing.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
