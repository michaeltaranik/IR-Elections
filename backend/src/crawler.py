"""Crawler responsible for downloading election data from configured sources."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
import json
import logging

import requests
from bs4 import BeautifulSoup

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
CORPUS_PATH = DATA_DIR / "corpus.json"

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
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.text


def parse_documents(html: str) -> Iterable[Document]:
    """Placeholder parser extracting dummy data until real logic is added."""
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string if soup.title else "Untitled"
    body_text = soup.get_text(separator="\n")[:1000]
    yield Document(title=title, content=body_text, url="about:blank")


def persist_documents(documents: Iterable[Document]) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    payload = [doc.to_dict() for doc in documents]
    logger.info("Writing %d documents to %s", len(payload), CORPUS_PATH)
    with CORPUS_PATH.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)


def crawl() -> None:
    logger.info("Crawler bootstrap - add source URLs to begin crawling")
    sources: list[str] = []
    all_docs: list[Document] = []

    for url in sources:
        html = fetch_html(url)
        all_docs.extend(parse_documents(html))

    persist_documents(all_docs)


if __name__ == "__main__":
    crawl()
