'use client';

import React, { useState } from 'react';
import { SearchForm } from '@/components/SearchForm';
import { PopularRoutes } from '@/components/PopularRoutes';
import { useRouter, useSearchParams } from 'next/navigation';
import { Preference } from '@/types';

export function HomePageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [isSearching, setIsSearching] = useState(false);

  const handleSearch = (params: { from: string; to: string; preference: Preference; date?: string }) => {
    setIsSearching(true);
    const query = new URLSearchParams({
      from: params.from,
      to: params.to,
      preference: params.preference,
      ...(params.date ? { date: params.date } : {}),
    });
    router.push(`/results?${query.toString()}`);
  };

  const defaultFrom = searchParams.get('from') || '';
  const defaultTo = searchParams.get('to') || '';
  const defaultPreference = (searchParams.get('preference') || 'balanced') as Preference;
  const defaultDate = searchParams.get('date') || undefined;

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-saffron-500 to-saffron-600 rounded-xl flex items-center justify-center text-white font-bold text-lg shadow-lg">
                🇮🇳
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Travel Planner India</h1>
                <p className="text-xs text-gray-500">Multi-Modal Journey Planner</p>
              </div>
            </div>
            <nav className="hidden md:flex items-center gap-6">
              <a href="#" className="text-sm text-gray-600 hover:text-saffron-600 transition-colors">About</a>
              <a href="#" className="text-sm text-gray-600 hover:text-saffron-600 transition-colors">API</a>
              <a href="https://github.com" className="text-sm text-gray-600 hover:text-saffron-600 transition-colors">GitHub</a>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="relative overflow-hidden">
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-50 bg-[url('data:image/svg+xml,%3Csvg%20width%3D%2260%22%20height%3D%2260%22%20viewBox%3D%220%200%2060%2060%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%3Cg%20fill%3D%22none%22%20fill-rule%3D%22evenodd%22%3E%3Cg%20fill%3D%22%23f59e0b%22%20fill-opacity%3D%220.08%22%3E%3Cpath%20d%3D%22M36%2034v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6%2034v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6%204V0H4v4H0v2h4v4h2V6h4V4H6z%22%2F%3E%3C%2Fg%3E%3C%2Fg%3E%3C%2Fsvg%3E')]" />

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 md:py-24">
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-saffron-100 text-saffron-700 rounded-full text-sm font-medium mb-6">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-saffron-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-saffron-500"></span>
              </span>
              Powered by Real-Time Data
            </div>
            <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-4 tracking-tight">
              Plan Your Journey
              <span className="block text-transparent bg-clip-text bg-gradient-to-r from-saffron-500 to-saffron-600">
                Across India
              </span>
            </h1>
            <p className="text-lg md:text-xl text-gray-600 max-w-2xl mx-auto">
              One search combines flight + train + bus + auto into a complete door-to-door plan —
              with connection risk, real last-mile cost, and per-leg reliability baked in.
            </p>
          </div>

          {/* Search Card */}
          <div className="max-w-3xl mx-auto">
            <div className="bg-white rounded-2xl shadow-2xl p-6 md:p-8">
              <SearchForm
                onSearch={handleSearch}
                isLoading={isSearching}
                defaultFrom={defaultFrom}
                defaultTo={defaultTo}
                defaultPreference={defaultPreference}
                defaultDate={defaultDate}
              />
            </div>
          </div>

          {/* Features */}
          <div className="mt-16 grid md:grid-cols-3 gap-8">
            <FeatureCard
              icon="🧠"
              title="Multi-leg combinations"
              description="We combine flights, trains, and buses into a single journey — flight to BLR, train onward to Hampi — with the auto leg included."
            />
            <FeatureCard
              icon="⏱️"
              title="Connection intelligence"
              description="Per-city transfer buffers using historical on-time data flag tight or risky handoffs before you book."
            />
            <FeatureCard
              icon="💰"
              title="True door-to-door cost"
              description="Every fare plus last-mile auto plus booking fees plus meals — the real number, not the headline ticket."
            />
          </div>

          {/* Popular Routes — live from /api/v1/routes/popular */}
          <div className="mt-16">
            <PopularRoutes />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-sm text-gray-500">
              © 2026 Travel Planner India. Built with Next.js 16.
            </p>
            <div className="flex items-center gap-4">
              <span className="flex items-center gap-1 text-xs text-gray-400">
                <span className="w-2 h-2 bg-emerald-500 rounded-full"></span>
                API Online
              </span>
              <span className="flex items-center gap-1 text-xs text-gray-400">
                <span className="w-2 h-2 bg-saffron-500 rounded-full"></span>
                Real-time Data
              </span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

function FeatureCard({ icon, title, description }: { icon: string; title: string; description: string }) {
  return (
    <div className="bg-white rounded-xl p-6 shadow-md hover:shadow-lg transition-shadow">
      <div className="text-4xl mb-4">{icon}</div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-sm text-gray-600">{description}</p>
    </div>
  );
}

