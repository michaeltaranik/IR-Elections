import { useState } from 'react';
import { Search } from 'lucide-react';

interface SearchViewProps {
  onSearch: (query: string, country?: string | null, year?: number | null) => void;
  loading?: boolean;
}

export function SearchView({ onSearch, loading = false }: SearchViewProps) {
  const [query, setQuery] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !loading) {
      onSearch(query.trim());
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen px-4">
      <div className="w-full max-w-2xl">
        <div className="text-center mb-12">
          <h1 className="text-blue-600 mb-4">Election Results Search</h1>
          <p className="text-gray-600">Search for election results by state, candidate, or election type</p>
        </div>

        <form onSubmit={handleSubmit} className="relative">
          <div className="relative">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search election results..."
              className="w-full px-6 py-4 pr-14 border-2 border-gray-300 rounded-full focus:outline-none focus:border-blue-500 transition-colors"
            />
            <button
              type="submit"
              disabled={loading}
              className="absolute right-2 top-1/2 -translate-y-1/2 bg-blue-600 text-white p-3 rounded-full hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Search className="w-5 h-5" />
            </button>
          </div>
        </form>

        <div className="mt-8 grid grid-cols-2 gap-4">
          <button
            onClick={() => onSearch('election', 'France', null)}
            disabled={loading}
            className="px-4 py-3 bg-white border border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors disabled:opacity-50"
          >
            France Elections
          </button>
          <button
            onClick={() => onSearch('election', 'USA', null)}
            disabled={loading}
            className="px-4 py-3 bg-white border border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors disabled:opacity-50"
          >
            USA Elections
          </button>
          <button
            onClick={() => onSearch('election', null, 2024)}
            disabled={loading}
            className="px-4 py-3 bg-white border border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors disabled:opacity-50"
          >
            2024 Elections
          </button>
          <button
            onClick={() => onSearch('election', 'Switzerland', null)}
            disabled={loading}
            className="px-4 py-3 bg-white border border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors disabled:opacity-50"
          >
            Switzerland Elections
          </button>
        </div>
      </div>
    </div>
  );
}
