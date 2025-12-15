"""Crawler that downloads election data from three public sources.

Sources:
1) France (French Ministry of Interior archives)
2) USA (American Presidency Project statistics page)
3) Switzerland (Swiss Federal Statistical Office)

Each parser is intentionally conservative and extracts tabular text from a
small number of seed pages. Add more seeds as needed.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Callable
import json
import logging
import re
import hashlib

import requests
from bs4 import BeautifulSoup

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
CORPUS_PATH = DATA_DIR / "corpus.json"
MAX_CONTENT_LEN = 2000  # keep snippets reasonable for indexing

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Document:
    title: str
    content: str
    url: str
    year: int | None = None
    country: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "title": self.title,
            "content": self.content,
            "url": self.url,
            "year": self.year,
            "country": self.country,
        }


def fetch_html(url: str) -> str:
    logger.info("Fetching %s", url)
    headers = {
        "User-Agent": "IR-Elections Bot/1.0 (+https://github.com/)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": url,
    }
    response = requests.get(url, timeout=30, headers=headers)
    response.raise_for_status()
    return response.text


def extract_year_from_url(url: str) -> int | None:
    match = re.search(r"(19|20)\d{2}", url)
    return int(match.group()) if match else None


def normalize_text(text: str) -> str:
    return " ".join(text.split())


def body_document(soup: BeautifulSoup, url: str, country: str, title_prefix: str = "Page") -> Document:
    raw_title = soup.title.string if soup.title else f"{country} Elections"
    title = f"{title_prefix}: {normalize_text(raw_title)}"
    content = normalize_text(soup.get_text(" ", strip=True))[:MAX_CONTENT_LEN]
    anchor = re.sub(r"[^a-zA-Z0-9]+", "-", title.lower()).strip("-") or "page"
    url_with_anchor = f"{url}#{anchor}"
    return Document(
        title=title,
        content=content,
        url=url_with_anchor,
        year=extract_year_from_url(url),
        country=country,
    )


def parse_table_rows(
    soup: BeautifulSoup, url: str, country: str
) -> list[Document]:
    documents: list[Document] = []
    tables = soup.find_all("table")
    for table in tables:
        rows = table.find_all("tr")
        # skip header row if it looks like one
        data_rows = rows[1:] if rows and rows[0].find_all(["th", "strong"]) else rows
        for idx, row in enumerate(data_rows):
            cells = [normalize_text(td.get_text(" ", strip=True)) for td in row.find_all(["td", "th"])]
            if not cells:
                continue
            title = cells[0]
            content = normalize_text(" | ".join(cells))
            if not content:
                continue
            anchor_base = re.sub(r"[^a-zA-Z0-9]+", "-", (title or content).lower()).strip("-") or f"row-{idx}"
            url_with_anchor = f"{url}#{anchor_base}-{idx}"
            documents.append(
                Document(
                    title=title or "Untitled",
                    content=content[:MAX_CONTENT_LEN],
                    url=url_with_anchor,
                    year=extract_year_from_url(url),
                    country=country,
                )
            )
    return documents


def parse_france(html: str, url: str) -> list[Document]:
    soup = BeautifulSoup(html, "html.parser")
    docs = parse_table_rows(soup, url, country="France")
    docs.append(body_document(soup, url, "France", title_prefix="Full page"))
    return docs


def parse_usa(html: str, url: str) -> list[Document]:
    soup = BeautifulSoup(html, "html.parser")
    docs = parse_table_rows(soup, url, country="USA")
    docs.append(body_document(soup, url, "USA", title_prefix="Full page"))
    return docs


def parse_switzerland(html: str, url: str) -> list[Document]:
    soup = BeautifulSoup(html, "html.parser")
    docs = parse_table_rows(soup, url, country="Switzerland")
    docs.append(body_document(soup, url, "Switzerland", title_prefix="Full page"))
    return docs


def discover_links(soup: BeautifulSoup, base_url: str, max_links: int = 10) -> list[str]:
    """Discover election-related links from a page."""
    links: list[str] = []
    base_domain = "/".join(base_url.split("/")[:3])
    
    for anchor in soup.find_all("a", href=True):
        href = anchor.get("href", "")
        text = normalize_text(anchor.get_text())
        
        # Look for election-related links
        election_keywords = ["election", "presidential", "parliamentary", "federal", "vote", "candidate", "result"]
        if any(keyword in text.lower() or keyword in href.lower() for keyword in election_keywords):
            # Resolve relative URLs
            if href.startswith("/"):
                full_url = base_domain + href
            elif href.startswith("http"):
                full_url = href
            else:
                continue
            
            if full_url not in links:
                links.append(full_url)
                if len(links) >= max_links:
                    break
    
    return links


def persist_documents(documents: Iterable[Document]) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    payload = [doc.to_dict() for doc in documents]
    logger.info("Writing %d documents to %s", len(payload), CORPUS_PATH)
    with CORPUS_PATH.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)


def crawl() -> None:
    # Seed URLs: picked for accessibility; adjust/expand as needed.
    sources: list[tuple[str, Callable[[str, str], list[Document]]]] = [
        (
            "https://en.wikipedia.org/wiki/2022_French_presidential_election",
            parse_france,
        ),
        (
            "https://en.wikipedia.org/wiki/2024_United_States_presidential_election",
            parse_usa,
        ),
        (
            "https://en.wikipedia.org/wiki/2023_Swiss_federal_election",
            parse_switzerland,
        ),
        # Additional seeds (non-Wikipedia) to diversify sources
        (
            "https://www.presidency.ucsb.edu/statistics/data",
            parse_usa,
        ),
        (
            "https://www.bfs.admin.ch/bfs/en/home/statistics/politics/elections.html",
            parse_switzerland,
        ),
    ]

    all_docs: list[Document] = []
    # Deduplicate primarily by base URL (without fragment) + title, and also by content hash.
    seen: set[tuple[str, str]] = set()
    seen_hashes: set[str] = set()
    urls_to_crawl: list[tuple[str, Callable[[str, str], list[Document]]]] = sources.copy()
    crawled_urls: set[str] = set()
    max_depth = 2  # Limit crawling depth
    current_depth = 0

    while urls_to_crawl and current_depth < max_depth:
        current_batch = urls_to_crawl.copy()
        urls_to_crawl.clear()
        current_depth += 1

        for url, parser in current_batch:
            if url in crawled_urls:
                continue
            crawled_urls.add(url)

            try:
                html = fetch_html(url)
                soup = BeautifulSoup(html, "html.parser")
                docs = parser(html, url)
                
                for doc in docs:
                    base_url = doc.url.split("#", 1)[0]
                    key = (base_url, doc.title)
                    content_hash = hashlib.sha1(f"{doc.title}|{doc.content}".encode("utf-8", errors="ignore")).hexdigest()
                    if key in seen or content_hash in seen_hashes:
                        continue
                    seen.add(key)
                    seen_hashes.add(content_hash)
                    all_docs.append(doc)
                
                # Discover links for next depth level
                if current_depth < max_depth:
                    discovered_links = discover_links(soup, url, max_links=20)
                    for link in discovered_links:
                        if link not in crawled_urls:
                            # Determine parser based on URL patterns
                            if "france" in link.lower() or "french" in link.lower():
                                urls_to_crawl.append((link, parse_france))
                            elif "usa" in link.lower() or "united_states" in link.lower() or "american" in link.lower():
                                urls_to_crawl.append((link, parse_usa))
                            elif "swiss" in link.lower() or "switzerland" in link.lower():
                                urls_to_crawl.append((link, parse_switzerland))
                            else:
                                # Default parser based on first source parser
                                urls_to_crawl.append((link, parser))
                
            except Exception as exc:  # pragma: no cover - runtime protection
                logger.warning("Failed to process %s: %s", url, exc)
                continue

    logger.info("Crawled %d URLs, extracted %d documents", len(crawled_urls), len(all_docs))
    persist_documents(all_docs)


if __name__ == "__main__":
    crawl()
