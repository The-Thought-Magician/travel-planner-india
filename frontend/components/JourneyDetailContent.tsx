'use client';

import React, { useEffect, useState } from 'react';
import { useParams, useSearchParams, useRouter } from 'next/navigation';
import { RouteVisualization, JourneySummary } from '@/components/RouteVisualization';
import { Button } from '@/components/ui/button';
import { EmptyState } from '@/components/EmptyState';
import { CostBreakdownRow } from '@/components/CostBreakdownRow';
import { ConnectionRiskBadge } from '@/components/ConnectionRiskBadge';
import { AlternativeDatesStrip } from '@/components/AlternativeDatesStrip';
import { DisruptionReplan } from '@/components/DisruptionReplan';
import { Journey } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export function JourneyDetailContent() {
  const searchParams = useSearchParams();
  const routeParams = useParams();
  const router = useRouter();
  const [journey, setJourney] = useState<Journey | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [copied, setCopied] = useState(false);
  const [replanResults, setReplanResults] = useState<Journey[] | null>(null);

  useEffect(() => {
    // Dynamic route /journey/[id] wins; fall back to ?id= for legacy links.
    const dynamicId = typeof routeParams?.id === 'string' ? routeParams.id : Array.isArray(routeParams?.id) ? routeParams.id[0] : undefined;
    const journeyId = dynamicId || searchParams.get('id') || undefined;

    // Session storage is the fast path when navigating from the results list.
    const stored = sessionStorage.getItem('selectedJourney');
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        if (!journeyId || parsed.journey_id === journeyId) {
          setJourney(parsed);
          setIsLoading(false);
          return;
        }
      } catch (e) {
        console.error('Failed to parse stored journey:', e);
      }
    }

    if (journeyId) {
      fetchJourney(journeyId);
    } else {
      setIsLoading(false);
    }
  }, [searchParams, routeParams]);

  const fetchJourney = async (id: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/journeys/${id}`);
      if (response.ok) {
        const data = await response.json();
        setJourney(data.journey || data);
      }
    } catch (e) {
      console.error('Failed to fetch journey:', e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleBack = () => router.back();

  const handleShare = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      /* ignore */
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block w-12 h-12 animate-spin rounded-full border-4 border-saffron-200 border-t-saffron-600" />
          <p className="mt-4 text-gray-600">Loading journey details...</p>
        </div>
      </div>
    );
  }

  if (!journey) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <EmptyState
          icon="📋"
          title="Journey not found"
          description="The journey may have expired (30-min cache). Run a new search."
          action={{ label: 'Go back', onClick: handleBack }}
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <button
              onClick={handleBack}
              className="flex items-center gap-2 text-gray-600 hover:text-saffron-600 transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Back to results
            </button>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-saffron-500 to-saffron-600 rounded-xl flex items-center justify-center text-white font-bold">
                🇮🇳
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-gray-900 mb-1">
            Journey details
          </h1>
          <p className="text-gray-500 text-sm">
            Complete route with all transfers, timings, connection risk and cost breakdown.
          </p>
        </div>

        <JourneySummary
          totalCost={journey.total_cost}
          totalDuration={journey.total_duration_minutes}
          reliabilityScore={journey.reliability_score}
          legsCount={journey.transfers != null ? journey.transfers + 1 : journey.legs.length}
        />

        <AlternativeDatesStrip journeyId={journey.journey_id} />

        {/* Non-safe connection risks surfaced up top */}
        {journey.connection_risks && journey.connection_risks.filter(r => r.risk !== 'safe').length > 0 && (
          <div className="space-y-2">
            <h3 className="text-sm font-semibold text-gray-900">Connection risk</h3>
            {journey.connection_risks.filter(r => r.risk !== 'safe').map((r, i) => (
              <ConnectionRiskBadge key={i} risk={r} />
            ))}
          </div>
        )}

        <div className="bg-white rounded-2xl shadow-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Route</h2>
          <RouteVisualization legs={journey.legs} connectionRisks={journey.connection_risks} />
        </div>

        {journey.cost_breakdown && (
          <CostBreakdownRow breakdown={journey.cost_breakdown} />
        )}

        {journey.booking_links?.per_leg && journey.booking_links.per_leg.length > 0 && (
          <div className="rounded-xl border border-gray-200 bg-white p-4">
            <h3 className="text-sm font-semibold text-gray-900 mb-2">Book each leg</h3>
            <ul className="space-y-2 text-sm">
              {journey.booking_links.per_leg.map((l, i) => (
                <li key={i} className="flex flex-wrap items-center gap-3">
                  <a
                    href={l.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-saffron-700 hover:underline"
                  >
                    {l.mode} {l.vehicle_id} ↗
                  </a>
                  <DisruptionReplan
                    journeyId={journey.journey_id}
                    vehicleId={l.vehicle_id}
                    mode={l.mode}
                    onReplanned={setReplanResults}
                  />
                </li>
              ))}
            </ul>
          </div>
        )}

        {replanResults && replanResults.length > 0 && (
          <div className="rounded-xl border border-amber-200 bg-amber-50 p-4">
            <div className="flex items-baseline justify-between mb-2">
              <h3 className="text-sm font-semibold text-amber-900">Alternate journeys (disrupted leg excluded)</h3>
              <button
                onClick={() => setReplanResults(null)}
                className="text-xs text-amber-700 hover:underline"
              >
                Dismiss
              </button>
            </div>
            <ul className="space-y-2">
              {replanResults.slice(0, 3).map((j) => (
                <li key={j.journey_id}>
                  <a
                    href={`/journey/${j.journey_id}`}
                    className="flex items-baseline justify-between rounded-md bg-white border border-amber-200 px-3 py-2 hover:border-amber-400"
                  >
                    <span className="text-sm text-gray-900">
                      {j.legs
                        .filter((l) => l.mode !== 'auto' && l.mode !== 'transfer')
                        .map((l) => `${l.mode} ${l.flight_train_bus_no || ''}`)
                        .join(' → ')}
                    </span>
                    <span className="text-sm font-semibold text-saffron-700">
                      ₹{j.total_cost.toLocaleString('en-IN')}
                    </span>
                  </a>
                </li>
              ))}
            </ul>
          </div>
        )}

        {journey.warnings && journey.warnings.length > 0 && (
          <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
            <div className="flex items-start gap-3">
              <span className="text-2xl">⚠️</span>
              <div>
                <h3 className="font-semibold text-amber-800 mb-1">Notes</h3>
                <ul className="text-sm text-amber-700 space-y-1">
                  {journey.warnings.map((w, i) => (
                    <li key={i}>{w}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}

        <div className="flex flex-wrap gap-4 pt-2">
          <Button variant="primary" onClick={handleBack}>
            View other options
          </Button>
          <Button variant="outline" onClick={handleShare}>
            {copied ? 'Link copied ✓' : 'Share this journey'}
          </Button>
        </div>
      </main>
    </div>
  );
}
