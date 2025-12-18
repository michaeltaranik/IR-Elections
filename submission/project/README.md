## IR-Elections: Election Results Search Engine

### Team Members

- **Kameniev Danylo**
- **Taranik Mykhailo**

---

### Project Overview

**IR-Elections** is a full-stack information retrieval system that indexes, searches, and clusters election results from multiple international sources.  
Users can search for candidates, parties, and election events across countries, apply advanced filters (country, year, cluster), and explore results grouped into topics.

---

### Data Sources

The crawler focuses on public election-related pages, including:

- **France**

  - Examples: French presidential election pages, French Ministry of Interior archives
  - Content: Presidential, legislative, and regional election data (tables + page text)

- **USA**

  - Examples: American Presidency Project statistics pages, US election overviews
  - Content: Presidential election results, vote statistics, historical data

- **Switzerland, Germany, Canada**
  - Examples: Swiss federal election pages, Bundeswahlleiter (Germany), Elections Canada
  - Content: Federal election results, turnout, party and candidate information

The crawler discovers additional relevant links starting from a set of seed URLs and saves a normalized corpus to `backend/data/corpus.json`.

---

### Features

- **Advanced Filtering (Simple Feature)**

  - Filter search results by **Country** (e.g., France, USA, Switzerland, Germany, Canada)
  - Filter by **Year** (detected from URLs, titles, or page content)
  - Combine filters with free-text search over titles and content

- **Results Clustering (Complex Feature)**
  - Uses **TF‑IDF** vectorization + **K-Means** clustering on search results
  - Assigns a cluster label to each result (e.g., `Cluster 1`, `Cluster 2`, …)
  - Frontend groups and filters results by cluster to help users explore topics (e.g., “Green Party candidates” vs. “environmental referendums”)

---

### Architecture Overview

- **Backend (`backend/`, Python + Flask)**

  - `src/crawler.py`: Multi-country crawler that:
    - Fetches HTML pages from seed URLs and discovered links
    - Extracts structured table rows and full-page text into `Document` objects
    - Infers `year` and `country` metadata
    - Writes the normalized corpus to `data/corpus.json`
  - `src/indexer.py`: Whoosh indexer that:
    - Defines a schema with `title`, `content`, `url`, `year`, `country`
    - Reads `corpus.json` and builds the search index in `backend/index/`
  - `src/app.py`: Flask API that:
    - Exposes `POST /search` (query + filters → ranked results + clusters)
    - Uses Whoosh for full-text search (title + content)
    - Applies K-Means clustering over result metadata
    - Exposes `GET /health` for simple health checks
  - `run.sh`: Helper script to (re)build the index and start the Flask app.

- **Frontend (`frontend/`, React + TypeScript + Vite)**
  - `src/api.ts`: Calls the backend at `http://127.0.0.1:5000/search`
  - `App.tsx`, `SearchView`, `ResultsView`, `ResultCard`:
    - Modern, responsive search interface
    - Filters for Country, Year, and Cluster
    - Results grouped visually by cluster label

---

### Getting Started

#### 1. Prerequisites

- **Python**: 3.11+
- **Node.js**: 18+ (LTS recommended)
- Git (optional, for version control)

All commands below assume the project root is `IR-Elections/`.

---

#### 2. Backend Setup and Run

From the project root:

```bash
cd backend

# (Optional) create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

Then:

```bash
# 1) Crawl election data (writes to data/corpus.json)
python src/crawler.py

# 2) Build the Whoosh index into backend/index/
python src/indexer.py

# 3) Start the Flask server
python src/app.py
```

The backend will listen on `http://127.0.0.1:5000`.

You can also use the helper script:

```bash
cd backend
bash run.sh
```

> **Note:** The crawler hits public web pages and may take several minutes depending on network conditions and the runtime limit configured in `crawler.py`.

---

#### 3. Frontend Setup and Run

In a new terminal, from the project root:

```bash
cd frontend
npm install
npm run dev
```

Vite will print a local development URL.
Open it in a browser while the backend is running to use the full search experience.

---

### Data Flow

1. **Crawling** (`backend/src/crawler.py`)  
   Public election pages → parsed into normalized `Document` objects → saved to `backend/data/corpus.json`
2. **Indexing** (`backend/src/indexer.py`)  
   `corpus.json` → Whoosh index in `backend/index/`
3. **Search & Clustering** (`backend/src/app.py`)  
   User query + filters → Whoosh search → filtered results → TF‑IDF + K-Means → JSON response
4. **Presentation** (`frontend/`)  
   React app calls `/search` → displays results with filters and cluster grouping.

---

### Limitations and Notes

- The crawler focuses on a curated set of election-related pages and discovered links; it is not a full web-scale crawler.
- Year and country extraction rely on heuristics (URLs, headings, and content) and may occasionally be missing or approximate.
- The clustering is unsupervised and intended for topic exploration rather than strict, labeled topics.
