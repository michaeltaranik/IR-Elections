## IR-Elections Frontend

### Overview

This directory contains the React/TypeScript frontend for **IR-Elections**, a search interface for exploring international election results.  
The UI communicates with the Flask backend (`/search` endpoint) to display ranked and clustered election documents with filters for country, year, and cluster.

---

### Tech Stack

- **Framework**: React 18 + TypeScript
- **Bundler/Dev Server**: Vite
- **Styling**: Tailwind CSS
- **UI Components**: Radix UI–inspired components

Key files:

- `src/App.tsx`: Top-level application component and routing between search/results views
- `src/api.ts`: Client for the backend search API at `http://127.0.0.1:5000/search`
- `src/components/SearchView.tsx`: Initial search screen
- `src/components/ResultsView.tsx`: Results layout with Country/Year/Cluster filters
- `src/components/ResultCard.tsx`: Individual search result card

---

### Running the Frontend

From the project root (`IR-Elections/`):

```bash
cd frontend
npm install
npm run dev
```

Vite will print a local development URL.
Open this URL in your browser.

> **Important:** For full functionality, the backend must be running on `http://127.0.0.1:5000` (see the root `README.md` for backend setup).

---

### Development Notes

- The API base URL is configured in `src/api.ts` as `http://127.0.0.1:5000`.  
  If you change the backend host/port, update this constant accordingly.
- Filters (country, year, cluster) are derived from the search results returned by the backend, so they will reflect whatever data the crawler and indexer have produced.
- The UI is optimized for desktop but remains usable on smaller screens via responsive layout classes.
