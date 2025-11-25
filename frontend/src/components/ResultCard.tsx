import { ElectionResult } from '../App';
import { MapPin, Calendar, Award } from 'lucide-react';

interface ResultCardProps {
  result: ElectionResult;
}

export function ResultCard({ result }: ResultCardProps) {
  const partyColors = {
    Democrat: 'bg-blue-100 text-blue-800 border-blue-200',
    Republican: 'bg-red-100 text-red-800 border-red-200',
    Independent: 'bg-purple-100 text-purple-800 border-purple-200',
    Other: 'bg-gray-100 text-gray-800 border-gray-200'
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-gray-900 mb-2">{result.title}</h3>
          <div className="flex flex-wrap items-center gap-4 text-gray-600">
            <div className="flex items-center gap-1">
              <MapPin className="w-4 h-4" />
              <span>{result.state}</span>
            </div>
            <div className="flex items-center gap-1">
              <Calendar className="w-4 h-4" />
              <span>{result.year}</span>
            </div>
          </div>
        </div>
        <span className={`px-3 py-1 rounded-full border ${partyColors[result.party]}`}>
          {result.party}
        </span>
      </div>

      <div className="border-t border-gray-100 pt-4">
        <div className="flex items-center gap-2 mb-3">
          <Award className="w-5 h-5 text-yellow-500" />
          <span className="text-gray-900">{result.winner}</span>
        </div>
        
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-gray-600">Votes Received</span>
            <span className="text-gray-900">{result.votesReceived.toLocaleString()}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-gray-600">Total Votes</span>
            <span className="text-gray-900">{result.totalVotes.toLocaleString()}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-gray-600">Percentage</span>
            <span className="text-gray-900">{result.percentage}%</span>
          </div>
        </div>

        {/* Progress bar */}
        <div className="mt-4 w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-green-600 h-2 rounded-full transition-all"
            style={{ width: `${result.percentage}%` }}
          />
        </div>
      </div>
    </div>
  );
}
