"""
crawler.py
Milestone 1: Crawl a site, same-domain only, depth-limited.
For every page found -> grab links, buttons, forms, inputs.

Design choice: sync Playwright API, not async.
For a crawler this size, async buys you nothing but complexity.
If you're crawling 500+ pages in parallel later, switch to async. Not today.
"""

from playwright.sync_api import sync_playwright
from urllib.parse import urljoin, urlparse
import time


class Crawler:
    def __init__(self, start_url, max_depth=2, max_pages=25):
        self.start_url = start_url
        self.domain = urlparse(start_url).netloc
        self.max_depth = max_depth
        self.max_pages = max_pages

        self.visited = set()
        self.queue = [(start_url, 0)]  # (url, depth)
        self.results = []  # list of page dicts

    def is_same_domain(self, url):
        return urlparse(url).netloc == self.domain

    def normalize(self, url):
        # strip fragments (#section) so we don't treat anchor jumps as new pages
        parsed = urlparse(url)
        return parsed._replace(fragment="").geturl()

    def extract_elements(self, page):
        """Pull interactive elements off the current page. Cheap, no clicking yet."""

        links = page.eval_on_selector_all(
            "a[href]", "els => els.map(e => e.href)"
        )

        buttons = page.eval_on_selector_all(
            "button, [role='button'], input[type=submit]",
            "els => els.map(e => e.innerText || e.value || '[no label]')"
        )

        forms = page.eval_on_selector_all(
            "form",
            """els => els.map(f => ({
                action: f.action,
                method: f.method,
                inputs: Array.from(f.querySelectorAll('input, textarea, select'))
                    .map(i => ({name: i.name, type: i.type || i.tagName.toLowerCase()}))
            }))"""
        )

        inputs = page.eval_on_selector_all(
            "input:not([type=submit]), textarea, select",
            "els => els.map(e => ({name: e.name, type: e.type || e.tagName.toLowerCase()}))"
        )

        return {
            "links": links,
            "buttons": buttons,
            "forms": forms,
            "inputs": inputs,
        }

    def crawl(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            while self.queue and len(self.visited) < self.max_pages:
                url, depth = self.queue.pop(0)
                url = self.normalize(url)

                if url in self.visited or depth > self.max_depth:
                    continue

                self.visited.add(url)
                page_data = {"url": url, "depth": depth, "status": None, "error": None}

                try:
                    start = time.time()
                    response = page.goto(url, wait_until="domcontentloaded", timeout=15000)
                    page_data["load_time_ms"] = round((time.time() - start) * 1000, 2)
                    page_data["status"] = response.status if response else None

                    elements = self.extract_elements(page)
                    page_data.update(elements)

                    # queue up same-domain links found on this page
                    if depth < self.max_depth:
                        for link in elements["links"]:
                            link = self.normalize(link)
                            if self.is_same_domain(link) and link not in self.visited:
                                self.queue.append((link, depth + 1))

                except Exception as e:
                    page_data["error"] = str(e)

                self.results.append(page_data)

            browser.close()

        return self.results


if __name__ == "__main__":
    import sys
    import json

    target = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"
    c = Crawler(target, max_depth=2, max_pages=15)
    data = c.crawl()

    print(f"\nCrawled {len(data)} pages from {target}\n")
    for pg in data:
        print(f"[{pg['status']}] {pg['url']}  "
              f"(links={len(pg.get('links', []))}, "
              f"buttons={len(pg.get('buttons', []))}, "
              f"forms={len(pg.get('forms', []))})")

    with open("crawl_output.json", "w") as f:
        json.dump(data, f, indent=2)
    print("\nFull data dumped to crawl_output.json")
