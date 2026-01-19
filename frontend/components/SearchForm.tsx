'use client';

import React, { useState } from 'react';
import { LocationSearch } from './LocationSearch';
import { Select } from './ui/select';
import { Button } from './ui/button';
import { LocationSuggestion } from '@/types';

interface SearchFormProps {
  onSearch: (params: { from: string; to: string; preference: string }) => void;
  isLoading?: boolean;
  defaultFrom?: string;
  defaultTo?: string;
  defaultPreference?: string;
}

export function SearchForm({
  onSearch,
  isLoading = false,
  defaultFrom = '',
  defaultTo = '',
  defaultPreference = 'balanced',
}: SearchFormProps) {
  const [from, setFrom] = useState(defaultFrom);
  const [to, setTo] = useState(defaultTo);
  const [preference, setPreference] = useState(defaultPreference);
  const [fromLocation, setFromLocation] = useState<LocationSuggestion | null>(null);
  const [toLocation, setToLocation] = useState<LocationSuggestion | null>(null);

  const handleSwap = () => {
    const tempFrom = from;
    const tempTo = to;
    const tempFromLoc = fromLocation;
    const tempToLoc = toLocation;

    setFrom(tempTo);
    setTo(tempFrom);
    setFromLocation(tempToLoc);
    setToLocation(tempFromLoc);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch({ from, to, preference });
  };

  const isDisabled = isLoading || !from || !to;

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid md:grid-cols-2 gap-4">
        <LocationSearch
          label="From"
          placeholder="Enter city or station"
          value={from}
          onChange={setFrom}
          onSelect={setFromLocation}
          icon={<span className="text-xl">📍</span>}
        />

        <div className="relative md:pt-6">
          <LocationSearch
            label="To"
            placeholder="Enter city or station"
            value={to}
            onChange={setTo}
            onSelect={setToLocation}
            icon={<span className="text-xl">🎯</span>}
          />
          <button
            type="button"
            onClick={handleSwap}
            className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-10 md:left-auto md:right-4 md:translate-x-0 md:translate-y-0 md:top-8 w-10 h-10 bg-white border border-gray-200 rounded-full flex items-center justify-center hover:bg-gray-50 hover:border-saffron-300 transition-all shadow-sm"
            title="Swap locations"
          >
            <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
            </svg>
          </button>
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        <Select
          label="Preference"
          value={preference}
          onChange={(e) => setPreference(e.target.value)}
          options={[
            { value: 'fastest', label: '🚀 Fastest' },
            { value: 'cheapest', label: '💰 Cheapest' },
            { value: 'balanced', label: '⚖️ Balanced' },
          ]}
        />
        <div className="md:col-span-2 flex items-end">
          <Button
            type="submit"
            isLoading={isLoading}
            disabled={isDisabled}
            className="w-full"
          >
            Search Journeys
          </Button>
        </div>
      </div>
    </form>
  );
}
