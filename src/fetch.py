"""Polite, cached downloader for the source candidates in data/source_candidates.csv.

Rules this module enforces (from the project brief):
- check robots.txt before every fetch and skip disallowed URLs
- send a descriptive User-Agent
- sleep 2 to 3 seconds between requests
- cache everything: a URL already saved with HTTP 200 is never refetched
- save every raw file to sources/raw/ with publisher and date in the filename
- log every attempt (success or failure) to sources/raw/_manifest.csv

Rows are driven by the `fetch_mode` column:
- auto     fetch `url` and save it
- resolve  fetch `url` (a landing page), save it, then follow the first link whose
           href matches the regex in `link_pattern` and save that too
- manual   skipped; the file must be added by hand to sources/manual/
- pending  skipped; source not yet published
- none     skipped; no candidate found (see data/gaps.csv)

Usage:
    python -m src.fetch                 # fetch all auto/resolve rows
    python -m src.fetch --only C001,C014
    python -m src.fetch --dry-run       # show what would be fetched

Set SCRAPER_CONTACT to an email or URL to include in the User-Agent. SEC EDGAR
requires a contact in the User-Agent and will refuse requests without one.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import mimetypes
import os
import random
import re
import sys
import time
import urllib.robotparser
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / "data" / "source_candidates.csv"
RAW_DIR = ROOT / "sources" / "raw"
ROBOTS_DIR = RAW_DIR / "_robots"
MANIFEST = RAW_DIR / "_manifest.csv"

MANIFEST_FIELDS = [
    "cand_id", "role", "url", "final_url", "local_file", "http_status",
    "content_type", "bytes", "sha256", "fetched_at_utc", "note",
]

SLEEP_RANGE = (2.0, 3.0)
TIMEOUT = 60


def user_agent() -> str:
    contact = os.environ.get("SCRAPER_CONTACT", "").strip()
    base = "UnileverLiabilityResearch/0.1 (public-source actuarial research; polite, cached; python-requests)"
    return f"{base} contact: {contact}" if contact else base


def slug(text: str, maxlen: int = 40) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "-", text or "").strip("-").lower()
    return s[:maxlen].rstrip("-") or "x"


def polite_sleep() -> None:
    time.sleep(random.uniform(*SLEEP_RANGE))


class Fetcher:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.session = requests.Session()
        self.session.headers["User-Agent"] = user_agent()
        self.robots: dict[str, urllib.robotparser.RobotFileParser | None] = {}
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        ROBOTS_DIR.mkdir(parents=True, exist_ok=True)
        self.cache = self._load_manifest()

    # ---------- manifest / cache ----------
    def _load_manifest(self) -> dict[str, dict]:
        cache: dict[str, dict] = {}
        if MANIFEST.exists():
            with MANIFEST.open(newline="", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    if row["http_status"] == "200" and row["local_file"] and (ROOT / row["local_file"]).exists():
                        cache[row["url"]] = row
        return cache

    def _log(self, row: dict) -> None:
        new = not MANIFEST.exists()
        with MANIFEST.open("a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=MANIFEST_FIELDS)
            if new:
                w.writeheader()
            w.writerow({k: row.get(k, "") for k in MANIFEST_FIELDS})

    # ---------- robots.txt ----------
    def allowed(self, url: str) -> tuple[bool, str]:
        host = urlparse(url).netloc
        if host not in self.robots:
            robots_url = f"{urlparse(url).scheme}://{host}/robots.txt"
            rp = urllib.robotparser.RobotFileParser()
            try:
                resp = self.session.get(robots_url, timeout=TIMEOUT)
                polite_sleep()
                (ROBOTS_DIR / f"{slug(host, 80)}.txt").write_text(resp.text, encoding="utf-8")
                if resp.status_code in (401, 403):
                    rp.disallow_all = True
                elif resp.status_code >= 400:
                    rp.allow_all = True  # no robots.txt: standard convention is allow
                else:
                    rp.parse(resp.text.splitlines())
                self.robots[host] = rp
            except requests.RequestException as e:
                self.robots[host] = None
                return False, f"robots.txt unreachable: {type(e).__name__}: {e}"
        rp = self.robots[host]
        if rp is None:
            return False, "robots.txt unreachable earlier in this run"
        ok = rp.can_fetch(self.session.headers["User-Agent"], url)
        return ok, "" if ok else "disallowed by robots.txt"

    # ---------- download ----------
    def _filename(self, cand: dict, role: str, url: str, content_type: str) -> str:
        date = cand.get("pub_date") or f"accessed-{dt.date.today().isoformat()}"
        ext = Path(urlparse(url).path).suffix.lower()
        if not ext or len(ext) > 6:
            ext = mimetypes.guess_extension((content_type or "").split(";")[0].strip()) or ".bin"
        if ext in (".htm", ".xhtml"):
            ext = ".html"
        suffix = "" if role == "primary" else f"_{role}"
        return f"{slug(cand['publisher'], 30)}_{date}_{cand['cand_id']}_{slug(cand['title'], 50)}{suffix}{ext}"

    def get(self, cand: dict, url: str, role: str) -> dict | None:
        if url in self.cache:
            print(f"  cached  {url}")
            return self.cache[url]
        if self.dry_run:
            print(f"  would fetch [{role}] {url}")
            return None
        ok, why = self.allowed(url)
        base = {"cand_id": cand["cand_id"], "role": role, "url": url,
                "fetched_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
        if not ok:
            print(f"  SKIP    {url} ({why})")
            self._log({**base, "http_status": "skipped", "note": why})
            return None
        try:
            resp = self.session.get(url, timeout=TIMEOUT, allow_redirects=True)
        except requests.RequestException as e:
            print(f"  ERROR   {url} ({type(e).__name__})")
            self._log({**base, "http_status": "error", "note": f"{type(e).__name__}: {e}"[:300]})
            polite_sleep()
            return None
        polite_sleep()
        ctype = resp.headers.get("Content-Type", "")
        if resp.status_code != 200:
            print(f"  HTTP {resp.status_code} {url}")
            self._log({**base, "final_url": resp.url, "http_status": resp.status_code, "content_type": ctype})
            return None
        name = self._filename(cand, role, resp.url, ctype)
        path = RAW_DIR / name
        path.write_bytes(resp.content)
        row = {**base, "final_url": resp.url, "local_file": str(path.relative_to(ROOT)),
               "http_status": 200, "content_type": ctype, "bytes": len(resp.content),
               "sha256": hashlib.sha256(resp.content).hexdigest()}
        self._log(row)
        self.cache[url] = {k: str(v) for k, v in row.items()}
        print(f"  saved   {path.relative_to(ROOT)} ({len(resp.content):,} bytes)")
        return row

    def resolve(self, cand: dict) -> None:
        landing = self.get(cand, cand["url"], "landing")
        if not landing or self.dry_run:
            return
        html = (ROOT / landing["local_file"]).read_text(encoding="utf-8", errors="replace")
        pattern = re.compile(cand["link_pattern"])
        for a in BeautifulSoup(html, "html.parser").find_all("a", href=True):
            href = urljoin(landing.get("final_url") or cand["url"], a["href"])
            if pattern.search(href):
                self.get(cand, href, "primary")
                return
        print(f"  NO LINK matching /{cand['link_pattern']}/ on {cand['url']}")
        self._log({"cand_id": cand["cand_id"], "role": "primary", "url": cand["url"],
                   "http_status": "no-link", "note": f"no href matching {cand['link_pattern']}",
                   "fetched_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")})


def load_candidates() -> list[dict]:
    with CANDIDATES.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", help="comma-separated candidate ids")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    only = set(args.only.split(",")) if args.only else None
    fetcher = Fetcher(dry_run=args.dry_run)
    for cand in load_candidates():
        if only and cand["cand_id"] not in only:
            continue
        mode = cand["fetch_mode"]
        if mode not in ("auto", "resolve"):
            continue
        print(f"{cand['cand_id']} [{mode}] {cand['title']}")
        if mode == "auto":
            fetcher.get(cand, cand["url"], "primary")
        else:
            fetcher.resolve(cand)
    return 0


if __name__ == "__main__":
    sys.exit(main())
