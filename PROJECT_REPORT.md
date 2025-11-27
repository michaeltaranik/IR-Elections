# IR-Elections: Election Results Search Engine
## Project Report

**Team Members:** Kameniev Danylo, Taranik Mykhailo  
**Project Type:** Information Retrieval System

---

## Executive Summary

IR-Elections is a full-stack information retrieval system designed to index, search, and cluster election results from multiple international sources. The system provides users with an intuitive interface to search for candidates, parties, and election events across different countries, with advanced filtering capabilities and dynamic result clustering.

---

## Architecture Overview

### Backend (Python/Flask)
- **Crawler (`crawler.py`)**: Web scraping module using BeautifulSoup4 to extract election data from three sources:
  - French Ministry of Interior (Presidential, Legislative, Regional elections)
  - The American Presidency Project (US Presidential data)
  - Swiss Federal Statistical Office (Federal election results)
- **Indexer (`indexer.py`)**: Builds a Whoosh full-text search index with schema supporting:
  - Title and content fields (TEXT)
  - URL, country (ID)
  - Year (NUMERIC)
- **Search API (`app.py`)**: Flask REST API providing:
  - `/search` endpoint with query processing
  - Multifield search (title + content)
  - Filtering by country and year
  - K-Means clustering (k=4) using TF-IDF vectorization on result snippets

### Frontend (React/TypeScript)
- **Technology Stack**: React 18, Vite, Tailwind CSS, Radix UI components
- **Components**:
  - `SearchView`: Main search interface with quick filter buttons
  - `ResultsView`: Results display with sidebar filters (Type, Party, Year)
  - `ResultCard`: Individual result card component
- **Current State**: Uses mock election data; backend integration pending

---

## Key Features

### 1. Advanced Filtering (Simple Feature)
- Filter by Country (France, USA, Switzerland)
- Filter by Year (e.g., 2022, 2020)
- Filter by Election Type (Presidential, Parliamentary, etc.)
- Real-time filter application with result count updates

### 2. Results Clustering (Complex Feature)
- **Algorithm**: K-Means clustering with TF-IDF vectorization
- **Implementation**: 
  - Retrieves top 50 search results
  - Extracts snippets from each result
  - Vectorizes using scikit-learn's TfidfVectorizer (English stop words)
  - Applies K-Means (k=4, random_state=42) for topic grouping
  - Assigns cluster labels to results for frontend display
- **Use Case**: Groups related results (e.g., "Green Party Candidates" vs "Environmental Referendums")

---

## Technical Stack

| Component | Technology |
|-----------|-----------|
| **Backend Framework** | Flask 3.0.3 |
| **Search Engine** | Whoosh 2.7.4 |
| **Clustering** | scikit-learn 1.5.2 |
| **Web Scraping** | BeautifulSoup4 4.12.3, requests 2.32.3 |
| **Frontend Framework** | React 18.3.1, TypeScript |
| **Build Tool** | Vite 6.3.5 |
| **UI Components** | Radix UI, Tailwind CSS |

---

## Project Status

### Completed
- Backend architecture (Flask app, indexer, crawler skeleton)
- Whoosh index schema design and implementation
- Search API with filtering and clustering logic
- Frontend UI components (SearchView, ResultsView, ResultCard)
- Modern, responsive UI with filtering capabilities

### In Progress / Pending
- Crawler implementation (currently placeholder)
- Corpus data collection (corpus.json is empty)
- Frontend-backend integration (frontend uses mock data)
- Real-time search API connection
- Clustering visualization in frontend

---

## Data Flow

1. **Crawling Phase**: `crawler.py` → Fetches HTML from election sources → Parses documents → Saves to `data/corpus.json`
2. **Indexing Phase**: `indexer.py` → Reads `corpus.json` → Builds Whoosh index in `index/` directory
3. **Search Phase**: User query → Flask API → Whoosh search → Filtering → Clustering → JSON response
4. **Display Phase**: Frontend receives results → Applies UI filters → Renders clustered results

---

## File Structure

```
IR-Elections/
├── backend/
│   ├── src/
│   │   ├── app.py          # Flask API with search & clustering
│   │   ├── indexer.py      # Whoosh index builder
│   │   └── crawler.py      # Web scraper (placeholder)
│   ├── data/
│   │   └── corpus.json     # Crawled documents (empty)
│   ├── index/              # Whoosh search index
│   └── requirements.txt    # Python dependencies
└── frontend/
    ├── src/
    │   ├── App.tsx         # Main React component
    │   └── components/     # UI components
    └── package.json        # Node dependencies
```

---

## Next Steps

1. **Complete Crawler**: Implement source-specific parsers for France, USA, and Switzerland
2. **Data Collection**: Populate `corpus.json` with real election data
3. **Integration**: Connect frontend to Flask API endpoints
4. **Clustering UI**: Display cluster labels/groups in ResultsView
5. **Testing**: Validate search accuracy and clustering quality
6. **Deployment**: Prepare for production deployment
