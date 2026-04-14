'use client';

import React, { useState } from 'react';
import { LocationSearch } from './LocationSearch';
import { Button } from './ui/button';
import { LocationSuggestion, Preference } from '@/types';

type PrefOption = { value: Preference; label: string; emoji: string; hint: string };

const PREFERENCES: PrefOption[] = [
  { value: 'fastest', label: 'Fastest', emoji: '🚀', hint: 'Shortest total time' },
  { value: 'cheapest', label: 'Cheapest', emoji: '💰', hint: 'Lowest total cost' },
  { value: 'balanced', label: 'Balanced', emoji: '⚖️', hint: 'Cost × time × reliability' },
  { value: 'reliable', label: 'Most reliable', emoji: '🛡️', hint: 'Highest on-time probability' },
];

interface SearchFormProps {
  onSearch: (params: { from: string; to: string; preference: Preference; date?: string }) => void;
  isLoading?: boolean;
  defaultFrom?: string;
  defaultTo?: string;
  defaultPreference?: Preference;
  defaultDate?: string;
}

function todayIso(): string {
  return new Date().toISOString().slice(0, 10);
}

export function SearchForm({
  onSearch,
  isLoading = false,
  defaultFrom = '',
  defaultTo = '',
  defaultPreference = 'balanced',
  defaultDate,
}: SearchFormProps) {
  const [from, setFrom] = useState(defaultFrom);
  const [to, setTo] = useState(defaultTo);
  const [preference, setPreference] = useState<Preference>(defaultPreference);
  const [date, setDate] = useState(defaultDate || todayIso());
  const [, setFromLocation] = useState<LocationSuggestion | null>(null);
  const [, setToLocation] = useState<LocationSuggestion | null>(null);

  const handleSwap = () => {
    setFrom(to);
    setTo(from);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch({ from, to, preference, date });
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

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Travel date</label>
        <input
          type="date"
          value={date}
          min={todayIso()}
          onChange={(e) => setDate(e.target.value)}
          className="w-full md:w-60 rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-saffron-400 focus:border-transparent"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Optimize for</label>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2" role="tablist">
          {PREFERENCES.map((p) => {
            const active = preference === p.value;
            return (
              <button
                type="button"
                key={p.value}
                onClick={() => setPreference(p.value)}
                aria-pressed={active}
                className={
                  'flex flex-col items-start gap-0.5 rounded-lg border px-3 py-2 text-left transition-all ' +
                  (active
                    ? 'border-saffron-500 bg-saffron-50 shadow-sm'
                    : 'border-gray-200 bg-white hover:border-gray-300')
                }
              >
                <span className="text-sm font-medium text-gray-900">
                  <span className="mr-1.5">{p.emoji}</span>
                  {p.label}
                </span>
                <span className="text-xs text-gray-500">{p.hint}</span>
              </button>
            );
          })}
        </div>
      </div>

      <Button type="submit" isLoading={isLoading} disabled={isDisabled} className="w-full">
        Search journeys
      </Button>
    </form>
  );
}
