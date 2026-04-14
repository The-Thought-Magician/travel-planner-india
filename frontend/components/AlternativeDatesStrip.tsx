'use client';

import { useEffect, useState } from 'react';
import { AlternativeDate, AlternativesResponse } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Props {
  journeyId: string;
}

function formatDay(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric', month: 'short' });
}

export function AlternativeDatesStrip({ journeyId }: Props) {
  const [alts, setAlts] = useState<AlternativeDate[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    fetch(`${API_BASE_URL}/api/v1/journeys/${journeyId}/alternatives?window=7`)
      .then((r) => (r.ok ? r.json() : null))
      .then((d: AlternativesResponse | null) => {
        if (cancelled || !d) return;
        setAlts(d.alternatives || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
    return () => {
      cancelled = true;
    };
  }, [journeyId]);

  if (loading) return null;
  if (alts.length === 0) return null;

  const cheapest = [...alts].sort((a, b) => a.cheapest_total - b.cheapest_total)[0];

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-3">
      <div className="flex items-baseline justify-between mb-2">
        <h3 className="text-sm font-semibold text-gray-900">Flexible dates?</h3>
        {cheapest && cheapest.delta_vs_selected < 0 && !cheapest.is_selected && (
          <span className="text-xs text-green-700">
            {formatDay(cheapest.date)} saves ₹
            {Math.abs(cheapest.delta_vs_selected).toLocaleString('en-IN')}
          </span>
        )}
      </div>
      <div className="grid grid-cols-7 gap-1.5">
        {alts.map((d) => {
          const delta = d.delta_vs_selected;
          const hue = d.is_selected
            ? 'border-saffron-500 bg-saffron-50'
            : delta < 0
            ? 'border-green-200 hover:border-green-400'
            : delta > 0
            ? 'border-gray-200 hover:border-gray-300'
            : 'border-gray-200';
          return (
            <div
              key={d.date}
              className={`rounded-md border px-2 py-1.5 text-center text-xs ${hue}`}
              title={`₹${d.cheapest_total.toLocaleString('en-IN')} cheapest`}
            >
              <div className="font-medium text-gray-900">{formatDay(d.date)}</div>
              <div className="tabular-nums text-gray-700">
                ₹{(d.cheapest_total / 1000).toFixed(1)}k
              </div>
              {!d.is_selected && delta !== 0 && (
                <div className={`text-[10px] ${delta < 0 ? 'text-green-700' : 'text-gray-400'}`}>
                  {delta < 0 ? '-' : '+'}₹{Math.abs(delta).toLocaleString('en-IN')}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
