"""Indexer that builds a Whoosh index from the crawled corpus."""
from __future__ import annotations

from pathlib import Path
import shutil
import json
import logging

from whoosh import index
from whoosh.fields import ID, NUMERIC, TEXT, Schema

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
INDEX_DIR = BASE_DIR / "index"
CORPUS_PATH = DATA_DIR / "corpus.json"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def build_schema() -> Schema:
    return Schema(
        title=TEXT(stored=True),
        content=TEXT(stored=True),
        url=ID(stored=True),
        year=NUMERIC(stored=True),
        country=ID(stored=True),
    )


def load_corpus() -> list[dict]:
    if not CORPUS_PATH.exists():
        logger.warning("Corpus file %s not found", CORPUS_PATH)
        return []

    with CORPUS_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)


def build_index() -> None:
    # Rebuild from scratch to avoid stale indexes/locks.
    if INDEX_DIR.exists():
        shutil.rmtree(INDEX_DIR)
    INDEX_DIR.mkdir(exist_ok=True)

    schema = build_schema()
        idx = index.create_in(INDEX_DIR, schema)

    writer = idx.writer()
    documents = load_corpus()
    logger.info("Indexing %d documents", len(documents))

    for doc in documents:
        writer.update_document(
            title=doc.get("title", "Untitled"),
            content=doc.get("content", ""),
            url=doc.get("url", ""),
            year=doc.get("year"),
            country=doc.get("country"),
        )

    writer.commit()
    logger.info("Index build complete: %s", INDEX_DIR)


if __name__ == "__main__":
    build_index()
