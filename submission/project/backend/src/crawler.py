"""Crawler that downloads election data from three public sources.

Sources:
1) France (French Ministry of Interior archives)
2) USA (American Presidency Project statistics page)
3) Switzerland (Swiss Federal Statistical Office)
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Callable
from urllib.parse import quote
import json
import logging
import re
import hashlib
import time

import requests
from bs4 import BeautifulSoup

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
CORPUS_PATH = DATA_DIR / "corpus.json"
MAX_CONTENT_LEN = 5000

# Crawl/runtime controls
MAX_RUNTIME_SECONDS = 300
CHECKPOINT_EVERY_URLS = 1

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
        "Referer": url,
    }
    response = requests.get(url, timeout=30, headers=headers)
    response.raise_for_status()
    return response.text


def extract_year(text: str) -> int | None:
    """Helper to find a 4-digit year (19xx or 20xx) in any string."""
    if not text:
        return None
    match = re.search(r"\b(19|20)\d{2}\b", text)
    return int(match.group()) if match else None


def normalize_text(text: str) -> str:
    return " ".join(text.split())


def normalize_table(table: BeautifulSoup) -> list[list[str]]:
    """Converts a complex HTML table (rowspan/colspan) into a simple 2D grid."""
    rows = table.find_all("tr")
    if not rows:
        return []

    grid = []
    for _ in rows:
        grid.append([""] * 100)

    max_cols = 0
    
    for r_idx, row in enumerate(rows):
        c_idx = 0
        cells = row.find_all(["td", "th"])
        
        for cell in cells:
            while grid[r_idx][c_idx]:
                c_idx += 1
            
            text = normalize_text(cell.get_text(" ", strip=True))
            rowspan = int(cell.get("rowspan", 1))
            colspan = int(cell.get("colspan", 1))

            for r in range(rowspan):
                for c in range(colspan):
                    if r_idx + r < len(grid):
                        grid[r_idx + r][c_idx + c] = text
            
            c_idx += colspan
        max_cols = max(max_cols, c_idx)

    # Trim grid to actual size
    return [row[:max_cols] for row in grid]


def body_document(soup: BeautifulSoup, url: str, country: str, title_prefix: str = "Page") -> Document:
    raw_title = soup.title.string if soup.title else f"{country} Elections"
    title = f"{title_prefix}: {normalize_text(raw_title)}"
    content = normalize_text(soup.get_text(" ", strip=True))[:MAX_CONTENT_LEN]
    
    # Try multiple signals to infer year for full-page docs
    year = extract_year(url) or extract_year(title) or extract_year(content[:400])

    return Document(
        title=title,
        content=content,
        url=url,
        year=year,
        country=country,
    )


def parse_table_rows(soup: BeautifulSoup, url: str, country: str) -> list[Document]:
    documents: list[Document] = []
    tables = soup.find_all("table")
    
    for table in tables:
        grid = normalize_table(table)
        if not grid or len(grid) < 2:
            continue
            
        headers = grid[0]
        
        heading_text = ""
        heading_anchor = None
        prev = table.find_previous(["h1", "h2", "h3", "h4"])
        if prev:
            heading_text = normalize_text(prev.get_text(" ", strip=True))
            if prev.has_attr("id"):
                heading_anchor = prev["id"]

        for row in grid[1:]:
            # Skip empty rows or rows that replicate headers
            if not any(row) or row == headers:
                continue
                
            # Filter empty cells to find data
            non_empty_cells = [c for c in row if c]
            if not non_empty_cells:
                continue

            primary_key = non_empty_cells[0]
            
            parts = []
            for i, cell_value in enumerate(row):
                if i < len(headers) and headers[i] and cell_value:
                    parts.append(f"{headers[i]}: {cell_value}")
                elif cell_value:
                    parts.append(cell_value)
            
            content = " | ".join(parts)
            
            url_with_anchor = url
            
            if len(non_empty_cells) >= 2:
                first = quote(non_empty_cells[0])
                second = quote(non_empty_cells[1])
                url_with_anchor = f"{url}#:~:text={first},{second}"
            elif len(non_empty_cells) == 1 and len(non_empty_cells[0]) > 3:
                # Fallback for single-column rows
                url_with_anchor = f"{url}#:~:text={quote(non_empty_cells[0])}"
            elif heading_anchor:
                # Fallback to section header
                url_with_anchor = f"{url}#{heading_anchor}"

            documents.append(
                Document(
                    title=f"{country}: {heading_text} - {primary_key}",
                    content=content[:MAX_CONTENT_LEN],
                    url=url_with_anchor,
                    year=(
                        extract_year(url)
                        or extract_year(heading_text)
                        or extract_year(primary_key)
                    ),
                    country=country,
                )
            )
    return documents


# --- Country Parsers (Wrapper Functions) ---

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

def parse_germany(html: str, url: str) -> list[Document]:
    soup = BeautifulSoup(html, "html.parser")
    docs = parse_table_rows(soup, url, country="Germany")
    docs.append(body_document(soup, url, "Germany", title_prefix="Full page"))
    return docs

def parse_canada(html: str, url: str) -> list[Document]:
    soup = BeautifulSoup(html, "html.parser")
    docs = parse_table_rows(soup, url, country="Canada")
    docs.append(body_document(soup, url, "Canada", title_prefix="Full page"))
    return docs


def discover_links(soup: BeautifulSoup, base_url: str, max_links: int = 10) -> list[str]:
    links: list[str] = []
    parts = base_url.split("/")
    base_domain = f"{parts[0]}//{parts[2]}" 
    
    for anchor in soup.find_all("a", href=True):
        href = anchor.get("href", "")
        text = normalize_text(anchor.get_text())
        
        election_keywords = [
            "election", "presidential", "parliamentary", "federal",
            "vote", "voting", "candidate", "result", "results",
            "turnout", "referendum", "ballot", "runoff"
        ]
        if any(keyword in text.lower() or keyword in href.lower() for keyword in election_keywords):
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
    # Seed URLs
    sources: list[tuple[str, Callable[[str, str], list[Document]]]] = [
        ("https://en.wikipedia.org/wiki/French_presidential_election", parse_france),
        ("https://en.wikipedia.org/wiki/United_States_presidential_election", parse_usa),
        ("https://en.wikipedia.org/wiki/Swiss_federal_election", parse_switzerland),
        ("https://www.presidency.ucsb.edu/statistics/data", parse_usa),
        ("https://www.bundeswahlleiter.de/en/bundestagswahlen/2021/ergebnisse/bund-99.html", parse_germany),
        ("https://www.elections.ca/content.aspx?section=ele&dir=pas/41ge&document=index&lang=e", parse_canada),
    ]

    all_docs: list[Document] = []
    seen: set[tuple[str, str]] = set()
    seen_hashes: set[str] = set()
    
    urls_to_crawl = sources.copy()
    crawled_urls: set[str] = set()
    
    max_depth = 3 
    current_depth = 0

    # Timing + checkpoint tracking
    start_time = time.time()
    urls_processed = 0

    while urls_to_crawl and current_depth < max_depth:
        current_batch = urls_to_crawl.copy()
        urls_to_crawl.clear()
        current_depth += 1

        for url, parser in current_batch:
            # Respect overall runtime budget before starting a new URL
            elapsed = time.time() - start_time
            if elapsed > MAX_RUNTIME_SECONDS:
                logger.info(
                    "Time budget of %s seconds exceeded (%.2f s elapsed). "
                    "Stopping crawl early with %d URLs and %d documents.",
                    MAX_RUNTIME_SECONDS,
                    elapsed,
                    len(crawled_urls),
                    len(all_docs),
                )
                persist_documents(all_docs)
                logger.info("Final checkpoint written before early stop.")
                return

            if url in crawled_urls:
                continue
            crawled_urls.add(url)

            try:
                html = fetch_html(url)
                soup = BeautifulSoup(html, "html.parser")
                docs = parser(html, url)
                
                for doc in docs:
                    # Deduplicate based on URL base (ignoring anchor) and Title
                    base_url = doc.url.split("#", 1)[0]
                    key = (base_url, doc.title)
                    content_hash = hashlib.sha1(
                        f"{doc.title}|{doc.content}".encode("utf-8", errors="ignore")
                    ).hexdigest()
                    
                    if key in seen or content_hash in seen_hashes:
                        continue
                    seen.add(key)
                    seen_hashes.add(content_hash)
                    all_docs.append(doc)
                
                urls_processed += 1

                # Periodically checkpoint partial results so the user can stop
                # the process at any time and still keep most of the progress.
                if urls_processed % CHECKPOINT_EVERY_URLS == 0:
                    logger.info(
                        "Checkpointing after %d processed URLs: %d documents so far.",
                        urls_processed,
                        len(all_docs),
                    )
                    persist_documents(all_docs)
                
                # Discovery for next depth
                if current_depth < max_depth:
                    discovered_links = discover_links(soup, url, max_links=15)
                    for link in discovered_links:
                        if link not in crawled_urls:
                            link_lower = link.lower()
                            # Select parser based on simple keyword matching
                            if "france" in link_lower or "french" in link_lower:
                                next_parser = parse_france
                            elif "usa" in link_lower or "united_states" in link_lower or "american" in link_lower:
                                next_parser = parse_usa
                            elif "swiss" in link_lower or "switzerland" in link_lower:
                                next_parser = parse_switzerland
                            elif "germany" in link_lower or "bundeswahlleiter" in link_lower:
                                next_parser = parse_germany
                            elif "canada" in link_lower or "elections.ca" in link_lower:
                                next_parser = parse_canada
                            else:
                                next_parser = parser
                            
                            urls_to_crawl.append((link, next_parser))
                
            except Exception as exc:
                logger.warning("Failed to process %s: %s", url, exc)
                continue

    logger.info("Crawled %d URLs, extracted %d documents", len(crawled_urls), len(all_docs))
    persist_documents(all_docs)


if __name__ == "__main__":
    crawl()