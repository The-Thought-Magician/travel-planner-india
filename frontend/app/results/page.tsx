'use client';

import React, { Suspense, useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { JourneyCard } from '@/components/JourneyCard';
import { LoadingSpinner } from '@/components/LoadingSpinner';
import { EmptyState } from '@/components/EmptyState';
import { AlternativeDatesStrip } from '@/components/AlternativeDatesStrip';
import { SearchResponse, Journey } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

function ResultsContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [results, setResults] = useState<SearchResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const from = searchParams.get('from') || '';
  const to = searchParams.get('to') || '';
  const preference = searchParams.get('preference') || 'balanced';
  const date = searchParams.get('date') || undefined;

  useEffect(() => {
    async function fetchResults() {
      setIsLoading(true);
      setError(null);

      try {
        const params = new URLSearchParams({
          from,
          to,
          preference,
          max_transfers: '3',
          max_journeys: '10',
          ...(date ? { date } : {}),
        });

        const response = await fetch(`${API_BASE_URL}/api/v1/search?${params}`);

        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }

        const data: SearchResponse = await response.json();
        setResults(data);
      } catch (err) {
        console.error('Search failed:', err);
        setError('Failed to fetch results. Please try again.');
      } finally {
        setIsLoading(false);
      }
    }

    if (from && to) {
      fetchResults();
    }
  }, [from, to, preference, date]);

  const handleJourneyClick = (journey: Journey) => {
    sessionStorage.setItem('selectedJourney', JSON.stringify(journey));
    router.push(`/journey/${journey.journey_id}`);
  };

  const handleNewSearch = () => {
    router.push(`/?from=${encodeURIComponent(from)}&to=${encodeURIComponent(to)}&preference=${preference}`);
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <LoadingSpinner size="lg" text="Searching for the best journeys..." />
      </div>
    );
  }

  if (error || !results) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <EmptyState
          icon="😔"
          title="Something went wrong"
          description={error || 'Unable to load results'}
          action={{ label: 'Try Again', onClick: handleNewSearch }}
        />
      </div>
    );
  }

  const journeys = results.journeys || [];

  if (journeys.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <EmptyState
          icon="🔍"
          title="No journeys found"
          description={`We couldn't find any routes from ${results.metadata.from_location?.name || from} to ${results.metadata.to_location?.name || to}. Try different locations.`}
          action={{ label: 'New Search', onClick: handleNewSearch }}
        />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <button
          onClick={handleNewSearch}
          className="flex items-center gap-2 text-gray-600 hover:text-saffron-600 transition-colors mb-4"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Modify Search
        </button>

        <div className="flex items-center justify-between flex-wrap gap-4">
          <div>
            <h1 className="text-2xl md:text-3xl font-bold text-gray-900">
              {results.metadata.from_location?.name || from} → {results.metadata.to_location?.name || to}
            </h1>
            <p className="text-gray-500 mt-1">
              {journeys.length} journey{journeys.length !== 1 ? 's' : ''} found
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="px-3 py-1 bg-saffron-100 text-saffron-700 rounded-full text-sm font-medium">
              {preference === 'fastest' ? '🚀 Fastest' : preference === 'cheapest' ? '💰 Cheapest' : '⚖️ Balanced'}
            </span>
          </div>
        </div>
      </div>

      {/* Alternative dates strip for the top journey */}
      {journeys[0]?.journey_id && (
        <div className="mb-6">
          <AlternativeDatesStrip journeyId={journeys[0].journey_id} />
        </div>
      )}

      {/* Results */}
      <div className="space-y-4">
        {journeys.map((journey, index) => (
          <JourneyCard
            key={journey.journey_id}
            journey={journey}
            index={index}
            onClick={() => handleJourneyClick(journey)}
          />
        ))}
      </div>
    </div>
  );
}

export default function ResultsPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <a href="/" className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-saffron-500 to-saffron-600 rounded-xl flex items-center justify-center text-white font-bold text-lg">
              🇮🇳
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">Travel Planner India</h1>
            </div>
          </a>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Suspense fallback={<LoadingSpinner size="lg" />}>
          <ResultsContent />
        </Suspense>
      </main>
    </div>
  );
}
