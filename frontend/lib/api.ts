import { SearchParams, SearchResponse, Location } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Fetch journeys between two locations
 */
export async function searchJourneys(params: SearchParams): Promise<SearchResponse> {
  const searchParams = new URLSearchParams();

  if (params.from) searchParams.set('from', params.from);
  if (params.to) searchParams.set('to', params.to);
  if (params.preference) searchParams.set('preference', params.preference);
  if (params.max_transfers) searchParams.set('max_transfers', params.max_transfers.toString());
  if (params.max_journeys) searchParams.set('max_journeys', params.max_journeys.toString());

  const response = await fetch(`${API_BASE_URL}/api/v1/search?${searchParams.toString()}`);

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

/**
 * Search for locations by name
 */
export async function searchLocations(query: string): Promise<Location[]> {
  if (!query || query.length < 2) return [];

  const searchParams = new URLSearchParams();
  searchParams.set('q', query);
  searchParams.set('limit', '10');

  const response = await fetch(
    `${API_BASE_URL}/api/v1/locations?${searchParams.toString()}`
  );

  if (!response.ok) {
    console.error('Location search failed:', response.statusText);
    return [];
  }

  const data = await response.json();
  return data.locations || [];
}

/**
 * Get journey details by ID
 */
export async function getJourneyDetails(journeyId: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/v1/journeys/${journeyId}`);

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

/**
 * Get popular routes
 */
export async function getPopularRoutes(): Promise<any[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/routes/popular`);

  if (!response.ok) {
    return [];
  }

  const data = await response.json();
  return data.routes || [];
}
