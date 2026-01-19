'use client';

import React, { useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { RouteVisualization, JourneySummary } from '@/components/RouteVisualization';
import { Button } from '@/components/ui/button';
import { EmptyState } from '@/components/EmptyState';
import { Journey } from '@/types';

export function JourneyDetailContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [journey, setJourney] = useState<Journey | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Try to get journey from session storage first
    const stored = sessionStorage.getItem('selectedJourney');
    if (stored) {
      try {
        setJourney(JSON.parse(stored));
        setIsLoading(false);
        return;
      } catch (e) {
        console.error('Failed to parse stored journey:', e);
      }
    }

    // If not in storage, try to fetch from API
    const journeyId = searchParams.get('id');
    if (journeyId) {
      fetchJourney(journeyId);
    } else {
      setIsLoading(false);
    }
  }, [searchParams]);

  const fetchJourney = async (id: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/journeys/${id}`);
      if (response.ok) {
        const data = await response.json();
        setJourney(data);
      }
    } catch (e) {
      console.error('Failed to fetch journey:', e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleBack = () => {
    router.back();
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
          description="The journey details you're looking for don't exist."
          action={{ label: 'Go Back', onClick: handleBack }}
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
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
              Back to Results
            </button>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-saffron-500 to-saffron-600 rounded-xl flex items-center justify-center text-white font-bold">
                🇮🇳
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Title */}
        <div className="mb-8">
          <h1 className="text-2xl md:text-3xl font-bold text-gray-900 mb-2">
            Journey Details
          </h1>
          <p className="text-gray-500">
            Complete route information with all transfers and timings
          </p>
        </div>

        {/* Summary Card */}
        <div className="mb-8">
          <JourneySummary
            totalCost={journey.total_cost}
            totalDuration={journey.total_duration_minutes}
            reliabilityScore={journey.reliability_score}
            legsCount={journey.legs.length}
          />
        </div>

        {/* Route Visualization */}
        <div className="bg-white rounded-2xl shadow-lg p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Route</h2>
          <RouteVisualization legs={journey.legs} />
        </div>

        {/* Warnings */}
        {journey.warnings && journey.warnings.length > 0 && (
          <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 mb-8">
            <div className="flex items-start gap-3">
              <span className="text-2xl">⚠️</span>
              <div>
                <h3 className="font-semibold text-amber-800 mb-1">Important Notes</h3>
                <ul className="text-sm text-amber-700 space-y-1">
                  {journey.warnings.map((warning, i) => (
                    <li key={i}>• {warning}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex flex-wrap gap-4">
          <Button variant="primary" onClick={handleBack}>
            View Other Options
          </Button>
          <Button variant="outline">
            Share Journey
          </Button>
          <Button variant="ghost">
            Download PDF
          </Button>
        </div>
      </main>
    </div>
  );
}
