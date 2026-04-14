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

export type Preference = 'fastest' | 'cheapest' | 'balanced' | 'reliable' | 'most_reliable';

export type LegMode = 'flight' | 'train' | 'bus' | 'auto' | 'transfer' | 'multi-modal';

export interface JourneyLeg {
  mode: LegMode;
  from_name: string;
  from_code?: string;
  to_name: string;
  to_code?: string;
  cost: number;
  duration_minutes: number;
  distance_km?: number;
  departure_time?: string | null;
  arrival_time?: string | null;
  reliability_score?: number;
  flight_train_bus_no?: string;
  provider?: string;
  service_number?: string;
  notes?: string;
  warnings?: string[];
}

export interface CostBreakdown {
  tickets: number;
  last_mile: number;
  booking_fees: number;
  meals_incidentals: number;
  total: number;
}

export interface ConnectionRisk {
  between_legs: [number, number];
  actual_buffer_minutes: number;
  recommended_buffer_minutes: number;
  risk: 'safe' | 'tight' | 'risky';
  reason: string;
  hub_from: string;
  hub_to: string;
}

export interface BookingLink {
  mode: string;
  vehicle_id: string;
  url: string;
}

export interface Journey {
  journey_id: string;
  rank?: number;
  total_cost: number;
  total_duration_minutes: number;
  legs: JourneyLeg[];
  reliability_score: number;
  transfers?: number;
  cost_breakdown?: CostBreakdown;
  connection_risks?: ConnectionRisk[];
  warnings?: string[];
  booking_links?: {
    flights?: string;
    trains?: string;
    buses?: string;
    per_leg?: BookingLink[];
  };
}

export interface HubSummary {
  type: string;
  code: string;
  name: string;
}

export interface SearchMetadata {
  from_location?: Location;
  to_location?: Location;
  query?: {
    from?: string;
    to?: string;
    date?: string;
    preference?: Preference;
    max_transfers?: number;
    max_journeys?: number;
  };
  origin_hubs?: HubSummary[];
  destination_hubs?: HubSummary[];
  transit_hubs_considered?: string[];
  connection_pool_size?: number;
  error?: string;
  distance_km?: number;
}

export interface SearchResponse {
  journeys: Journey[];
  metadata: SearchMetadata;
}

export interface SearchParams {
  from: string;
  to: string;
  date?: string;
  preference?: Preference;
  max_transfers?: number;
  max_journeys?: number;
}

export interface AlternativeDate {
  date: string;
  cheapest_total: number;
  delta_vs_selected: number;
  is_selected: boolean;
}

export interface AlternativesResponse {
  alternatives: AlternativeDate[];
  base_date: string;
  original_total: number | null;
}

export interface PopularRoute {
  from: string;
  to: string;
  tagline?: string;
  typical_cost?: number;
  typical_duration_hours?: number;
}

export interface PopularRoutesResponse {
  routes: PopularRoute[];
  count: number;
}

// UI State Types

export interface SearchFormState {
  from: string;
  to: string;
  preference: Preference;
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
