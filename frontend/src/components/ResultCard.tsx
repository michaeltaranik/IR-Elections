import React from 'react';
import { SearchResult } from '../api';
import { MapPin, Calendar, ExternalLink } from 'lucide-react';

interface ResultCardProps {
  result: SearchResult;
}

export function ResultCard({ result }: ResultCardProps) {
  const countryColors: Record<string, string> = {
    France: 'bg-blue-100 text-blue-800 border-blue-200',
    USA: 'bg-red-100 text-red-800 border-red-200',
    Switzerland: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  };

  const countryColor = result.country ? countryColors[result.country] || 'bg-gray-100 text-gray-800 border-gray-200' : 'bg-gray-100 text-gray-800 border-gray-200';

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2 leading-tight">
            <a 
              href={result.url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="hover:text-blue-600 transition-colors inline-flex items-center gap-1"
            >
              {result.title}
              <ExternalLink className="w-4 h-4" />
            </a>
          </h3>
          <div className="flex flex-wrap items-center gap-4 text-gray-600 mb-3">
            {result.country && (
              <div className="flex items-center gap-1">
                <MapPin className="w-4 h-4" />
                <span>{result.country}</span>
              </div>
            )}
            {result.year && (
              <div className="flex items-center gap-1">
                <Calendar className="w-4 h-4" />
                <span>{result.year}</span>
              </div>
            )}
          </div>
          <div
            className="text-gray-700 leading-relaxed max-h-32 overflow-hidden"
            dangerouslySetInnerHTML={{ __html: result.snippet }}
          />
        </div>
        <div className="flex flex-col items-end gap-2 shrink-0">
          {typeof result.cluster === 'number' && (
            <span className="px-2 py-0.5 rounded-full bg-gray-100 text-gray-700 text-xs border border-gray-200">
              Cluster {result.cluster + 1}
            </span>
          )}
          {result.country && (
            <span className={`px-3 py-1 rounded-full border text-sm ${countryColor}`}>
              {result.country}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
