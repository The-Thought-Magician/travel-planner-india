'use client';

import React from 'react';
import { JourneyLeg } from '@/types';
import { formatDuration, formatTime, getTransportInfo } from '@/lib/utils';

interface RouteVisualizationProps {
  legs: JourneyLeg[];
}

export function RouteVisualization({ legs }: RouteVisualizationProps) {
  return (
    <div className="relative">
      {/* Vertical Line */}
      <div className="absolute left-[27px] top-8 bottom-8 w-0.5 bg-gray-200" />

      {/* Route Steps */}
      <div className="space-y-1">
        {legs.map((leg, index) => {
          const info = getTransportInfo(leg.mode);
          const isLast = index === legs.length - 1;

          return (
            <div key={index} className="relative">
              {/* Step */}
              <div className="relative flex items-start gap-4 p-4 rounded-xl hover:bg-gray-50 transition-colors">
                {/* Icon */}
                <div className={`relative z-10 w-14 h-14 rounded-full ${info.bg} flex items-center justify-center text-2xl shadow-sm`}>
                  {info.icon}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  {/* Route */}
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-semibold text-gray-900">{leg.from_name}</span>
                    <span className="text-gray-400">→</span>
                    <span className="font-semibold text-gray-900">{leg.to_name}</span>
                  </div>

                  {/* Details */}
                  <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-gray-600">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${info.bg} ${info.color}`}>
                      {info.label}
                    </span>
                    <span className="flex items-center gap-1">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      {formatDuration(leg.duration_minutes)}
                    </span>
                    {leg.departure_time && (
                      <span className="flex items-center gap-1">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                        </svg>
                        {formatTime(leg.departure_time)}
                      </span>
                    )}
                    {leg.arrival_time && (
                      <span className="flex items-center gap-1">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12l4 4l4 -4" />
                        </svg>
                        {formatTime(leg.arrival_time)}
                      </span>
                    )}
                    {leg.provider && (
                      <span className="text-gray-500">{leg.provider}</span>
                    )}
                    {leg.service_number && (
                      <span className="font-mono text-gray-500">#{leg.service_number}</span>
                    )}
                  </div>

                  {/* Warnings */}
                  {leg.warnings && leg.warnings.length > 0 && (
                    <div className="mt-2 flex items-center gap-2 text-sm text-amber-600">
                      <span>⚠️</span>
                      <span>{leg.warnings.join(', ')}</span>
                    </div>
                  )}
                </div>

                {/* Price */}
                <div className="text-right">
                  <p className="text-lg font-bold text-saffron-600">
                    ₹{leg.cost.toLocaleString('en-IN')}
                  </p>
                </div>
              </div>

              {/* Transfer Connector */}
              {!isLast && (
                <div className="ml-[60px] mt-1 mb-1 flex items-center gap-2 text-xs text-gray-500">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                  </svg>
                  Transfer
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

interface JourneySummaryProps {
  totalCost: number;
  totalDuration: number;
  reliabilityScore: number;
  legsCount: number;
}

export function JourneySummary({
  totalCost,
  totalDuration,
  reliabilityScore,
  legsCount,
}: JourneySummaryProps) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 bg-gray-50 rounded-xl">
      <div className="text-center">
        <p className="text-sm text-gray-500 mb-1">Total Cost</p>
        <p className="text-2xl font-bold text-saffron-600">
          ₹{totalCost.toLocaleString('en-IN')}
        </p>
      </div>
      <div className="text-center">
        <p className="text-sm text-gray-500 mb-1">Duration</p>
        <p className="text-2xl font-bold text-gray-900">
          {formatDuration(totalDuration)}
        </p>
      </div>
      <div className="text-center">
        <p className="text-sm text-gray-500 mb-1">Reliability</p>
        <p className={`text-2xl font-bold ${
          reliabilityScore >= 0.8 ? 'text-emerald-600' : reliabilityScore >= 0.6 ? 'text-amber-600' : 'text-red-600'
        }`}>
          {Math.round(reliabilityScore * 100)}%
        </p>
      </div>
      <div className="text-center">
        <p className="text-sm text-gray-500 mb-1">Transfers</p>
        <p className="text-2xl font-bold text-gray-900">
          {Math.max(0, legsCount - 1)}
        </p>
      </div>
    </div>
  );
}
