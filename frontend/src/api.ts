const API_BASE_URL = 'http://127.0.0.1:5000';

export interface SearchResult {
  title: string;
  url: string;
  snippet: string;
  year: number | null;
  country: string | null;
  cluster: number | null;
}

export interface SearchResponse {
  results: SearchResult[];
}

export interface SearchParams {
  query: string;
  country?: string | null;
  year?: number | null;
}

export async function searchElections(params: SearchParams): Promise<SearchResult[]> {
  const response = await fetch(`${API_BASE_URL}/search`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: params.query,
      country: params.country || null,
      year: params.year || null,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Unknown error' }));
    throw new Error(error.error || `HTTP error! status: ${response.status}`);
  }

  const data: SearchResponse = await response.json();
  return data.results;
}

