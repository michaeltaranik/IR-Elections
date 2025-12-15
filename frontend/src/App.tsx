import { useState } from 'react';
import { SearchView } from './components/SearchView';
import { ResultsView } from './components/ResultsView';
import { searchElections, SearchResult } from './api';

export default function App() {
  const [view, setView] = useState<'search' | 'results'>('search');
  const [searchQuery, setSearchQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (query: string, country?: string | null, year?: number | null) => {
    setSearchQuery(query);
    setLoading(true);
    setError(null);
    
    try {
      const searchResults = await searchElections({ query, country, year });
      setResults(searchResults);
    setView('results');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to search. Make sure the backend is running.');
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleNewSearch = () => {
    setView('search');
    setSearchQuery('');
    setResults([]);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {view === 'search' ? (
        <SearchView onSearch={handleSearch} loading={loading} />
      ) : (
        <ResultsView 
          results={results} 
          searchQuery={searchQuery}
          onNewSearch={handleNewSearch}
          onSearch={handleSearch}
          loading={loading}
          error={error}
        />
      )}
    </div>
  );
}
