import { useState } from 'react';
import { Search, SlidersHorizontal } from 'lucide-react';
import { ElectionResult } from '../App';
import { ResultCard } from './ResultCard';

interface ResultsViewProps {
  results: ElectionResult[];
  searchQuery: string;
  onNewSearch: () => void;
}

export function ResultsView({ results, searchQuery, onNewSearch }: ResultsViewProps) {
  const [newQuery, setNewQuery] = useState(searchQuery);
  const [selectedType, setSelectedType] = useState<string>('All');
  const [selectedParty, setSelectedParty] = useState<string>('All');
  const [selectedYear, setSelectedYear] = useState<string>('All');

  // Get unique values for filters
  const types = ['All', ...Array.from(new Set(results.map(r => r.type)))];
  const parties = ['All', ...Array.from(new Set(results.map(r => r.party)))];
  const years = ['All', ...Array.from(new Set(results.map(r => r.year.toString())))];

  // Apply filters
  const filteredResults = results.filter(result => {
    const typeMatch = selectedType === 'All' || result.type === selectedType;
    const partyMatch = selectedParty === 'All' || result.party === selectedParty;
    const yearMatch = selectedYear === 'All' || result.year.toString() === selectedYear;
    return typeMatch && partyMatch && yearMatch;
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (newQuery.trim()) {
      // Trigger a new search by calling parent
      window.location.reload(); // Simple way to reset - in production, you'd pass this up
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
                {/* Election Type Filter */}
                <div>
                  <label className="block text-gray-700 mb-2">Election Type</label>
                  <select
                    value={selectedType}
                    onChange={(e) => setSelectedType(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                  >
                    {types.map(type => (
                      <option key={type} value={type}>{type}</option>
                    ))}
                  </select>
                </div>

                {/* Party Filter */}
                <div>
                  <label className="block text-gray-700 mb-2">Party</label>
                  <select
                    value={selectedParty}
                    onChange={(e) => setSelectedParty(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                  >
                    {parties.map(party => (
                      <option key={party} value={party}>{party}</option>
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

                {/* Clear Filters */}
                {(selectedType !== 'All' || selectedParty !== 'All' || selectedYear !== 'All') && (
                  <button
                    onClick={() => {
                      setSelectedType('All');
                      setSelectedParty('All');
                      setSelectedYear('All');
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
              </p>
            </div>

            {filteredResults.length === 0 ? (
              <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
                <p className="text-gray-600">No results found. Try adjusting your filters.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {filteredResults.map(result => (
                  <ResultCard key={result.id} result={result} />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
