// API Response Types

export interface Location {
  id: string;
  name: string;
  type: 'city' | 'station' | 'airport';
  code: string;
  state?: string;
  latitude?: number;
  longitude?: number;
}

export interface JourneyLeg {
  mode: 'flight' | 'train' | 'bus' | 'auto';
  from_name: string;
  from_code: string;
  to_name: string;
  to_code: string;
  cost: number;
  duration_minutes: number;
  departure_time?: string;
  arrival_time?: string;
  reliability_score: number;
  provider?: string;
  service_number?: string;
  warnings?: string[];
}

export interface Journey {
  journey_id: string;
  total_cost: number;
  total_duration_minutes: number;
  legs: JourneyLeg[];
  reliability_score: number;
  warnings?: string[];
}

export interface SearchMetadata {
  from_location: Location;
  to_location: Location;
  query: {
    from?: string;
    to?: string;
    preference?: 'fastest' | 'cheapest' | 'balanced';
    max_transfers?: number;
    max_journeys?: number;
  };
  results?: {
    total_found: number;
    filtered: {
      by_budget: boolean;
      by_reliability: boolean;
      by_time: boolean;
    };
  };
  error?: string;
}

export interface SearchResponse {
  journeys: Journey[];
  metadata: SearchMetadata;
}

export interface SearchParams {
  from: string;
  to: string;
  preference?: 'fastest' | 'cheapest' | 'balanced';
  max_transfers?: number;
  max_journeys?: number;
}

// UI State Types

export interface SearchFormState {
  from: string;
  to: string;
  preference: 'fastest' | 'cheapest' | 'balanced';
  date?: string;
  passengers: number;
}

export interface LocationSuggestion {
  id: string;
  name: string;
  code: string;
  type: 'city' | 'station' | 'airport';
  state?: string;
}
