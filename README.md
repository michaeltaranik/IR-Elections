# IR Project 20: Election Results Search Engine

## Team Members

- Kameniev Danylo
- Taranik Mykhailo

## Project Overview

This project is an Information Retrieval system designed to index, search, and cluster election results from multiple international sources. The system allows users to search for candidates, parties, and election events, filtering results by specific attributes and viewing them in clustered topics.

## Data Sources

We have selected three distinct sources covering different political systems (Presidential, Federal, etc.):

1.  **French Ministry of Interior (France)**

    - _URL:_ `https://www.archives-resultats-elections.interieur.gouv.fr`
    - _Content:_ Official results for French Presidential, Legislative, and Regional elections.
    - _Format:_ Hierarchical HTML (Year > Election Type > Round > Department).

2.  **The American Presidency Project (USA)**

    - _URL:_ `https://www.presidency.ucsb.edu/statistics/data`
    - _Content:_ Detailed data on US Presidential elections, approval ratings, and historical records.
    - _Format:_ HTML Tables and textual descriptions.

3.  **Swiss Federal Statistical Office (Switzerland)**
    - _URL:_ `https://www.elections.admin.ch/en/ch/`
    - _Content:_ Federal election results, mandate allocations, and candidate lists by Canton.
    - _Format:_ Structured HTML tables.

## Features

### 1. Simple Feature: Advanced Filtering

- **Description:** Users can refine their search results based on structured attributes extracted during crawling.
- **Filters Chosen:**
  - `Country` (e.g., France, USA, Switzerland)
  - `Year` (e.g., 2022, 2020)
  - `Type` (e.g., Presidential, Parliamentary)

### 2. Complex Feature: Results Clustering

- **Description:** The search engine dynamically groups search results into "topics" to help users explore related concepts.
- **Implementation:** \* We will apply **K-Means Clustering** (or similar) on the search result snippets.
  - Results will be displayed in groups (e.g., a search for "Green" might cluster into "Green Party Candidates" vs "Environmental Referendums").

## Technical Architecture

### Implementation Plan

#### Phase 1: The Crawler (`crawler.py`)

- [ ] **Setup:** Create a `BeautifulSoup` script to fetch pages.
- [ ] **Extraction:**
  - Identify "Container" elements (e.g., `<div>` or `<table>` rows).
  - Extract `Title`, `Full Text`, and `URL`.
  - **Crucial:** Extract Metadata (`Year`, `Country`) from the URL structure or page breadcrumbs.
- [ ] **Storage:** Save parsed documents into a structured JSON file (e.g., `data/corpus.json`) to decouple crawling from indexing.

#### Phase 2: The Indexer (`indexer.py`)

- [ ] **Schema Design:** Define the Whoosh schema:
  ```python
  schema = Schema(title=TEXT(stored=True),
                  content=TEXT,
                  url=ID(stored=True),
                  year=NUMERIC(stored=True),
                  country=ID(stored=True))
  ```
- [ ] **Build Index:** Iterate through `corpus.json` and add documents to the index directory.

#### Phase 3: The Search Engine (`app.py`)

- [ ] **Query Parsing:** Implement a MultifieldParser to search both Title and Content.
- [ ] **Filtering Logic:** Add filter clauses to the query based on user selection.
- [ ] **Clustering Logic:**
  1.  Retrieve Top N results (e.g., 50).
  2.  Extract snippets.
  3.  Vectorize snippets using TF-IDF.
  4.  Run K-Means (k=4).
  5.  Assign cluster labels to results before sending to frontend.

#### Phase 4: Integration

- [ ] Connect the Python Flask backend to the Frontend interface.
- [ ] Render "Google-style" snippets with highlighted query terms.

## How to Run

1.  Install dependencies: `pip install -r requirements.txt`
2.  Run the crawler: `python src/crawler.py`
3.  Build the index: `python src/indexer.py`
4.  Start the server: `python src/app.py`
5.  Open browser at `http://localhost:8000`
