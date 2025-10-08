# spidur 🕷️

[![PyPI version](https://img.shields.io/pypi/v/spidur.svg)](https://pypi.org/project/spidur/)
[![License](https://img.shields.io/github/license/ra0x3/spidur)](LICENSE)
[![Tests](https://github.com/ra0x3/spidur/actions/workflows/ci.yaml/badge.svg)](https://github.com/ra0x3/spidur/actions)

**spidur** is a lightweight, hackable framework for running **multiple custom scrapers in parallel** — even on the same domain.  
It helps you coordinate different scrapers, ensure valid URLs (no wasted work), and collect all results at once.

---

## ✨ Core ideas

- **Multiple scrapers per domain** — handle different content types (articles, images, comments, etc.) simultaneously.
- **Parallel execution** — utilizes all CPU cores.
- **Async + multiprocessing safe** — works across async methods and process pools.
- **No opinions** — you control discovery, validation, and scraping logic.
- **Results collected automatically** — each scraper contributes to a single aggregated result set.

---

## 📦 Install

```bash
pip install spidur
```

or with Poetry:

```bash
poetry add spidur
```

---

## ⚡ Example

```python
from spidur.core import Target, Scraper
from spidur.factory import ScraperFactory
from spidur.runner import Runner


# --- define your base scrapers ---

class ArticleScraper(Scraper):
    async def is_valid_url(self, url):
        return url.startswith("https://example.com/articles/")

    async def discover_urls(self, page, known):
        return [
            "https://example.com/articles/1",
            "https://example.com/articles/2",
        ]

    async def scrape_page(self, page, url):
        return {"type": "article", "url": url, "data": f"Content of {url}"}

    async def fetch_page(self, known):
        urls = await self.discover_urls(None, known)
        urls = [u for u in urls if await self.is_valid_url(u)]
        return [await self.scrape_page(None, u) for u in urls]


class CommentScraper(Scraper):
    async def is_valid_url(self, url):
        return url.startswith("https://example.com/comments/")

    async def discover_urls(self, page, known):
        return [
            "https://example.com/comments/1",
            "https://example.com/comments/2",
        ]

    async def scrape_page(self, page, url):
        return {"type": "comment", "url": url, "data": f"Comments from {url}"}

    async def fetch_page(self, known):
        urls = await self.discover_urls(None, known)
        urls = [u for u in urls if await self.is_valid_url(u)]
        return [await self.scrape_page(None, u) for u in urls]


# --- register both scrapers for the same domain ---

ScraperFactory.register("articles", ArticleScraper)
ScraperFactory.register("comments", CommentScraper)


# --- define your scrape targets ---

targets = [
    Target(name="articles", start_url="https://example.com/articles"),
    Target(name="comments", start_url="https://example.com/comments"),
]


# --- run them all in parallel ---

results = Runner.run(targets, seen=set())

for name, items in results.items():
    print(f"Results from {name}:")
    for item in items:
        print("  →", item)
```

---

## 🧠 How it works

1. Each `Scraper` subclass defines:
    - `is_valid_url(url)` — ensures no invalid or duplicate URLs are processed.
    - `discover_urls()` — finds new pages to scrape.
    - `scrape_page()` — extracts structured data.
    - `fetch_page()` — orchestrates the above.

2. You register scrapers in `ScraperFactory`.

3. The `Runner`:
    - Spawns multiple processes.
    - Executes all scrapers concurrently.
    - Aggregates their results into a single dictionary keyed by scraper name.

---

## 🧪 Running tests

```bash
poetry install
poetry run pytest
```

or with plain `pip`:

```bash
pip install -e .
pytest
```

## 🧩 Why “spidur”?

Because it crawls the web — but cleanly, predictably, and in parallel. 🕸️
