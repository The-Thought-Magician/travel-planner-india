'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { PopularRoute, PopularRoutesResponse } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export function PopularRoutes() {
  const [routes, setRoutes] = useState<PopularRoute[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    let cancelled = false;
    fetch(`${API_BASE_URL}/api/v1/routes/popular?limit=12`)
      .then((r) => r.json() as Promise<PopularRoutesResponse>)
      .then((d) => {
        if (!cancelled) {
          setRoutes(d.routes || []);
          setLoading(false);
        }
      })
      .catch(() => setLoading(false));
    return () => {
      cancelled = true;
    };
  }, []);

  if (loading) {
    return (
      <section className="max-w-6xl mx-auto px-4 py-8">
        <div className="text-center text-sm text-gray-500">Loading popular routes…</div>
      </section>
    );
  }

  if (routes.length === 0) return null;

  return (
    <section className="max-w-6xl mx-auto px-4 py-8">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Popular journeys</h2>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
        {routes.map((r) => (
          <button
            key={`${r.from}-${r.to}`}
            onClick={() => {
              const params = new URLSearchParams({
                from: r.from,
                to: r.to,
                preference: 'balanced',
              });
              router.push(`/results?${params.toString()}`);
            }}
            className="text-left rounded-lg border border-gray-200 bg-white p-3 hover:border-saffron-400 hover:shadow-sm transition-all group"
          >
            <div className="text-sm font-semibold text-gray-900 flex items-center gap-1.5">
              {r.from}
              <svg className="w-3.5 h-3.5 text-gray-400 group-hover:text-saffron-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
              {r.to}
            </div>
            {r.tagline && <div className="mt-1 text-xs text-gray-500 line-clamp-2">{r.tagline}</div>}
            <div className="mt-2 flex items-baseline gap-2 text-xs text-gray-600">
              {r.typical_cost != null && <span>₹{r.typical_cost.toLocaleString('en-IN')}</span>}
              {r.typical_duration_hours != null && (
                <span className="text-gray-400">• ~{r.typical_duration_hours}h</span>
              )}
            </div>
          </button>
        ))}
      </div>
    </section>
  );
}
