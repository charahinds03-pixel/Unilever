# Unilever liability analysis

Public-source storyline on Unilever's liability risk: where turnover sits, how liability regimes differ by region, and why the US drives severity.

## Layout

- `data/source_candidates.csv`: every candidate source found in Phase 1, with URL, publisher type, access and fetch mode
- `data/source_tracker.csv`: one row per sourced claim (filled in Phase 2)
- `data/gaps.csv`: everything looked for and not confirmed
- `src/fetch.py`: polite, cached downloader (robots.txt, User-Agent, 2 to 3 s sleep, manifest at `sources/raw/_manifest.csv`)
- `src/extract.py`: PDF and HTML text lookup with page numbers
- `sources/raw/`: downloaded files; `sources/manual/`: files added by hand
- `output/phase1_source_discovery.md`: Phase 1 checkpoint report

## Run

```
python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
export SCRAPER_CONTACT="you@example.com"   # SEC EDGAR requires a contact
python -m src.fetch --dry-run
python -m src.fetch
python -m src.extract find sources/raw/<file>.pdf "Turnover"
```
