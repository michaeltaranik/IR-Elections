"""Flask application exposing search & clustering endpoints."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import logging

from flask import Flask, jsonify, request
from flask_cors import CORS
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from whoosh import index
from whoosh.qparser import MultifieldParser

BASE_DIR = Path(__file__).resolve().parents[1]
INDEX_DIR = BASE_DIR / "index"

app = Flask(__name__)
CORS(app)
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    year: int | None
    country: str | None
    cluster: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "year": self.year,
            "country": self.country,
            "cluster": self.cluster,
        }


def get_searcher():
    if not index.exists_in(INDEX_DIR):
        raise RuntimeError("Search index missing. Run src/indexer.py first.")
    return index.open_dir(INDEX_DIR).searcher()


def run_query(query: str, filters: dict[str, str]) -> list[SearchResult]:
    with get_searcher() as searcher:
        # Boost title matches via fieldboosts
        parser = MultifieldParser(
            ["title", "content"],
            schema=searcher.schema,
            fieldboosts={"title": 2.0, "content": 1.0},
        )
        parsed_query = parser.parse(query)
        results = searcher.search(parsed_query, limit=50, scored=True)

        payload: list[SearchResult] = []
        seen: set[tuple[str, str]] = set()
        
        for hit in results:
            country_filter = filters.get("country")
            if country_filter and country_filter != "All" and hit.get("country") != country_filter:
                continue

            year_filter = filters.get("year")
            if year_filter and year_filter != "All":
                hit_year = str(hit.get("year")) if hit.get("year") is not None else ""
                if hit_year != str(year_filter):
                    continue

            key = (hit.get("url"), hit.get("title"))
            if key in seen:
                continue
            seen.add(key)

            # Plain-text snippet from stored content (no HTML/highlights).
            full_content = (hit.get("content") or "").strip()
            if full_content:
                snippet = full_content[:40]

            payload.append(
                SearchResult(
                    title=hit["title"],
                    url=hit["url"],
                    snippet=hit.highlights("content"),
                    year=hit.get("year"),
                    country=hit.get("country"),
                )
            )
    return payload


def apply_clustering(results: list[SearchResult], k: int = 4) -> None:
    if not results:
        return

    # Use title + metadata as text for clustering instead of snippets.
    texts = [
        " ".join(
            [
                result.title or "",
                str(result.year or ""),
                result.country or "",
            ]
        ).strip()
        for result in results
    ]
    # Ensure we have enough non-empty texts to cluster.
    non_empty_texts = [t for t in texts if t]
    if len(non_empty_texts) < k:
        return

    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(texts)

    k = min(k, len(results))
    clusters = KMeans(n_clusters=k, n_init="auto", random_state=42)
    labels = clusters.fit_predict(matrix)

    for result, label in zip(results, labels, strict=False):
        result.cluster = int(label)


@app.post("/search")
def search():
    body = request.get_json(force=True) or {}
    query = body.get("query", "")
    filters = {
        "country": body.get("country"),
        "year": body.get("year"),
    }

    if not query:
        return jsonify({"error": "query is required"}), 400

    results = run_query(query, filters)
    apply_clustering(results)
    return jsonify({"results": [result.to_dict() for result in results]})


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True)