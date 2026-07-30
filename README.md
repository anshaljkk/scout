# Scout

Give it a URL. It crawls the site, finds every interactive element,
runs automated UI + API checks, catches JS console errors, screenshots
failures, and gets an LLM to summarize what broke and why.

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

