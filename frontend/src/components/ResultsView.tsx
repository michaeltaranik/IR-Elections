import React, { useState, useEffect } from 'react';
import { Search, SlidersHorizontal, Loader2 } from 'lucide-react';
import { SearchResult } from '../api';
import { ResultCard } from './ResultCard';

interface ResultsViewProps {
  results: SearchResult[];
  searchQuery: string;
  onNewSearch: () => void;
  onSearch: (query: string, country?: string | null, year?: number | null) => void;
  loading?: boolean;
  error?: string | null;
}

export function ResultsView({ results, searchQuery, onNewSearch, onSearch, loading = false, error }: ResultsViewProps) {
  const [newQuery, setNewQuery] = useState(searchQuery);
  const [selectedCountry, setSelectedCountry] = useState<string>('All');
  const [selectedYear, setSelectedYear] = useState<string>('All');
  const [selectedCluster, setSelectedCluster] = useState<string>('All');

  // Keep the local input in sync with parent search query
  useEffect(() => {
    setNewQuery(searchQuery);
  }, [searchQuery]);

  // Get unique values for filters
  const countries = ['All', ...Array.from(new Set(results.map(r => r.country).filter(Boolean) as string[]))];
  const years = ['All', ...Array.from(new Set(results.map(r => r.year?.toString()).filter(Boolean) as string[]))];
  const clusters = ['All', ...Array.from(
    new Set(
      results
        .map(r => (typeof r.cluster === 'number' ? `Cluster ${r.cluster + 1}` : null))
        .filter(Boolean) as string[]
    )
  )];

  // Apply filters
  const filteredResults = results.filter(result => {
    const countryMatch = selectedCountry === 'All' || result.country === selectedCountry;
    const yearMatch = selectedYear === 'All' || result.year?.toString() === selectedYear;
    const clusterLabel = typeof result.cluster === 'number' ? `Cluster ${result.cluster + 1}` : 'Unclustered';
    const clusterMatch = selectedCluster === 'All' || clusterLabel === selectedCluster;
    return countryMatch && yearMatch && clusterMatch;
  });

  // Group by cluster
  const groupedByCluster = filteredResults.reduce((acc, result) => {
    const clusterKey = result.cluster !== null ? `Cluster ${result.cluster + 1}` : 'Unclustered';
    if (!acc[clusterKey]) {
      acc[clusterKey] = [];
    }
    acc[clusterKey].push(result);
    return acc;
  }, {} as Record<string, SearchResult[]>);

  const handleSearch = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (newQuery.trim() && !loading) {
      const country = selectedCountry !== 'All' ? selectedCountry : null;
      const year = selectedYear !== 'All' ? parseInt(selectedYear) : null;
      onSearch(newQuery.trim(), country, year);
    }
  };

  return (
    <div className="min-h-screen">
      {/* Header with search */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center gap-4">
            <button
              onClick={onNewSearch}
              className="text-blue-600 hover:text-blue-700 shrink-0"
            >
              ← Back
            </button>
            <form onSubmit={handleSearch} className="flex-1">
              <div className="relative">
                <input
                  type="text"
                  value={newQuery}
                  onChange={(e) => setNewQuery(e.target.value)}
                  placeholder="Search election results..."
                  className="w-full px-4 py-2 pr-10 border border-gray-300 rounded-full focus:outline-none focus:border-blue-500"
                />
                <button
                  type="submit"
                  className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-blue-600"
                >
                  <Search className="w-5 h-5" />
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex flex-col md:flex-row gap-8">
          {/* Filters Sidebar */}
          <div className="w-full md:w-64 shrink-0">
            <div className="bg-white rounded-lg border border-gray-200 p-6 sticky top-24">
              <div className="flex items-center gap-2 mb-6">
                <SlidersHorizontal className="w-5 h-5 text-gray-600" />
                <h2>Filters</h2>
              </div>

              <div className="space-y-6">
                {/* Country Filter */}
                <div>
                  <label className="block text-gray-700 mb-2">Country</label>
                  <select
                    value={selectedCountry}
                    onChange={(e) => setSelectedCountry(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                  >
                    {countries.map(country => (
                      <option key={country} value={country}>{country}</option>
                    ))}
                  </select>
                </div>

                {/* Year Filter */}
                <div>
                  <label className="block text-gray-700 mb-2">Year</label>
                  <select
                    value={selectedYear}
                    onChange={(e) => setSelectedYear(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                  >
                    {years.map(year => (
                      <option key={year} value={year}>{year}</option>
                    ))}
                  </select>
                </div>

                {/* Cluster Filter */}
                <div>
                  <label className="block text-gray-700 mb-2">Cluster</label>
                  <select
                    value={selectedCluster}
                    onChange={(e) => setSelectedCluster(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                  >
                    {clusters.map(cluster => (
                      <option key={cluster} value={cluster}>{cluster}</option>
                    ))}
                  </select>
                </div>

                {/* Clear Filters */}
                {(selectedCountry !== 'All' || selectedYear !== 'All' || selectedCluster !== 'All') && (
                  <button
                    onClick={() => {
                      setSelectedCountry('All');
                      setSelectedYear('All');
                      setSelectedCluster('All');
                    }}
                    className="w-full px-4 py-2 text-blue-600 border border-blue-600 rounded-lg hover:bg-blue-50 transition-colors"
                  >
                    Clear Filters
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Results List */}
          <div className="flex-1">
            <div className="mb-4">
              <p className="text-gray-600">
                {filteredResults.length} result{filteredResults.length !== 1 ? 's' : ''} for "{searchQuery}"
                {(selectedCountry !== 'All' || selectedYear !== 'All' || selectedCluster !== 'All') && (
                  <span className="text-gray-500 text-sm ml-2">
                    (filtered by
                    {selectedCountry !== 'All' && <> country: {selectedCountry}</>}
                    {selectedYear !== 'All' && <> year: {selectedYear}</>}
                    {selectedCluster !== 'All' && <> cluster: {selectedCluster}</>}
                    )
                  </span>
                )}
              </p>
            </div>

            {loading ? (
              <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
                <Loader2 className="w-8 h-8 animate-spin mx-auto text-blue-600 mb-4" />
                <p className="text-gray-600">Searching...</p>
              </div>
            ) : error ? (
              <div className="bg-red-50 rounded-lg border border-red-200 p-6">
                <p className="text-red-800 font-medium mb-2">Error</p>
                <p className="text-red-600">{error}</p>
              </div>
            ) : filteredResults.length === 0 ? (
              <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
                <p className="text-gray-600">No results found. Try adjusting your filters or search query.</p>
              </div>
            ) : (
              <div className="space-y-8">
                {Object.entries(groupedByCluster).map(([clusterName, clusterResults]) => (
                  <div key={clusterName}>
                    <h3 className="text-lg font-semibold text-gray-800 mb-4 pb-2 border-b border-gray-200">
                      {clusterName} ({clusterResults.length} result{clusterResults.length !== 1 ? 's' : ''})
                    </h3>
                    <div className="space-y-4">
                      {clusterResults.map((result, idx) => (
                        <div key={`${result.url}-${idx}`}>
                          <ResultCard result={result} />
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
