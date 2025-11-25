import { useState } from 'react';
import { SearchView } from './components/SearchView';
import { ResultsView } from './components/ResultsView';

export type ElectionResult = {
  id: string;
  title: string;
  year: number;
  state: string;
  type: 'Presidential' | 'Congressional' | 'Gubernatorial' | 'Local';
  winner: string;
  party: 'Democrat' | 'Republican' | 'Independent' | 'Other';
  votesReceived: number;
  totalVotes: number;
  percentage: number;
};

// Mock election data
const mockElectionData: ElectionResult[] = [
  {
    id: '1',
    title: '2024 Presidential Election - California',
    year: 2024,
    state: 'California',
    type: 'Presidential',
    winner: 'Jane Smith',
    party: 'Democrat',
    votesReceived: 8234567,
    totalVotes: 15234890,
    percentage: 54.1
  },
  {
    id: '2',
    title: '2024 Presidential Election - Texas',
    year: 2024,
    state: 'Texas',
    type: 'Presidential',
    winner: 'John Doe',
    party: 'Republican',
    votesReceived: 5678901,
    totalVotes: 10234567,
    percentage: 55.5
  },
  {
    id: '3',
    title: '2024 Gubernatorial Election - Florida',
    year: 2024,
    state: 'Florida',
    type: 'Gubernatorial',
    winner: 'Mike Johnson',
    party: 'Republican',
    votesReceived: 4567890,
    totalVotes: 8234567,
    percentage: 55.5
  },
  {
    id: '4',
    title: '2024 Congressional Election - New York District 12',
    year: 2024,
    state: 'New York',
    type: 'Congressional',
    winner: 'Sarah Williams',
    party: 'Democrat',
    votesReceived: 234567,
    totalVotes: 456789,
    percentage: 51.3
  },
  {
    id: '5',
    title: '2022 Presidential Election - Pennsylvania',
    year: 2022,
    state: 'Pennsylvania',
    type: 'Presidential',
    winner: 'Robert Brown',
    party: 'Democrat',
    votesReceived: 3456789,
    totalVotes: 6789012,
    percentage: 50.9
  },
  {
    id: '6',
    title: '2024 Gubernatorial Election - Michigan',
    year: 2024,
    state: 'Michigan',
    type: 'Gubernatorial',
    winner: 'Lisa Davis',
    party: 'Democrat',
    votesReceived: 2345678,
    totalVotes: 4567890,
    percentage: 51.4
  },
  {
    id: '7',
    title: '2024 Presidential Election - Arizona',
    year: 2024,
    state: 'Arizona',
    type: 'Presidential',
    winner: 'John Doe',
    party: 'Republican',
    votesReceived: 1789012,
    totalVotes: 3456789,
    percentage: 51.8
  },
  {
    id: '8',
    title: '2024 Local Election - Seattle Mayor',
    year: 2024,
    state: 'Washington',
    type: 'Local',
    winner: 'Emily Chen',
    party: 'Independent',
    votesReceived: 234567,
    totalVotes: 456789,
    percentage: 51.3
  },
  {
    id: '9',
    title: '2024 Congressional Election - Georgia District 5',
    year: 2024,
    state: 'Georgia',
    type: 'Congressional',
    winner: 'David Martinez',
    party: 'Democrat',
    votesReceived: 178901,
    totalVotes: 345678,
    percentage: 51.8
  },
  {
    id: '10',
    title: '2024 Gubernatorial Election - Ohio',
    year: 2024,
    state: 'Ohio',
    type: 'Gubernatorial',
    winner: 'Tom Wilson',
    party: 'Republican',
    votesReceived: 2890123,
    totalVotes: 5678901,
    percentage: 50.9
  }
];

export default function App() {
  const [view, setView] = useState<'search' | 'results'>('search');
  const [searchQuery, setSearchQuery] = useState('');
  const [results, setResults] = useState<ElectionResult[]>([]);

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    // Filter results based on search query
    const filtered = mockElectionData.filter(result => 
      result.title.toLowerCase().includes(query.toLowerCase()) ||
      result.state.toLowerCase().includes(query.toLowerCase()) ||
      result.winner.toLowerCase().includes(query.toLowerCase())
    );
    setResults(filtered);
    setView('results');
  };

  const handleNewSearch = () => {
    setView('search');
    setSearchQuery('');
    setResults([]);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {view === 'search' ? (
        <SearchView onSearch={handleSearch} />
      ) : (
        <ResultsView 
          results={results} 
          searchQuery={searchQuery}
          onNewSearch={handleNewSearch}
        />
      )}
    </div>
  );
}
