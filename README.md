# Scout

Give it a URL. It crawls the site, finds every interactive element,
runs automated UI + API checks, catches JS console errors, screenshots
failures, and gets an LLM to summarize what broke and why.

Built to replace the first hour of manual QA click-testing on any web app.

## Status

🚧 Work in progress. Currently built:

- [x] `crawler.py` — same-domain crawl, discovers links/buttons/forms/inputs
- [ ] `ui_tests.py` — click/interact + catch JS errors
- [ ] `api_tests.py` — replay + validate API calls
- [ ] `db.py` — SQLite storage
- [ ] `ai_analyzer.py` — LLM failure summary
- [ ] `report.py` — HTML dashboard
- [ ] CLI + GitHub Actions

## Setup

```bash
git clone <your-repo-url>
cd scout
python -m venv venv
source venv/bin/activate      # venv\Scripts\activate on Windows
pip install -r requirements.txt
playwright install chromium
```

## Usage (crawler only, for now)

```bash
python scout/crawler.py https://example.com
```

Dumps discovered pages + elements to `crawl_output.json`.

## Why this exists

Most "testing" college projects are a pytest folder with 5 asserts.
This one actually crawls a live site, discovers its structure, and finds
real problems (broken links, console errors, slow pages) without anyone
writing test cases by hand.

## Architecture

```
crawler → finds pages + elements
    ↓
ui_tests / api_tests → runs checks
    ↓
db (SQLite) → stores runs, issues, screenshots
    ↓
ai_analyzer → LLM reads failures, suggests root cause
    ↓
report → renders HTML dashboard
```

One process, one SQLite file. No microservices — not needed at this scale.

## License

MIT
