'use client';

import React from 'react';
import { Card, CardBody } from './ui/card';
import { Journey } from '@/types';
import { formatCurrency, formatDuration, getTransportInfo } from '@/lib/utils';

interface JourneyCardProps {
  journey: Journey;
  index: number;
  onClick: () => void;
}

export function JourneyCard({ journey, index, onClick }: JourneyCardProps) {
  const { legs } = journey;
  const isBest = index === 0;

  return (
    <Card
      variant={isBest ? 'elevated' : 'default'}
      hover
      onClick={onClick}
      className={isBest ? 'ring-2 ring-saffron-500' : ''}
    >
      {isBest && (
        <div className="bg-gradient-to-r from-saffron-500 to-saffron-600 text-white px-4 py-1.5 text-sm font-medium text-center">
          ⭐ Best Option
        </div>
      )}
      <CardBody className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {legs.slice(0, 3).map((leg, i) => (
              <span key={i} className="text-xl">{getTransportInfo(leg.mode).icon}</span>
            ))}
            {legs.length > 3 && (
              <span className="text-gray-400 text-sm">+{legs.length - 3}</span>
            )}
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className="text-xs text-gray-500">Duration</p>
              <p className="font-semibold text-gray-900">{formatDuration(journey.total_duration_minutes)}</p>
            </div>
            <div className="text-right">
              <p className="text-xs text-gray-500">Price</p>
              <p className="text-xl font-bold text-saffron-600">{formatCurrency(journey.total_cost)}</p>
            </div>
          </div>
        </div>

        {/* Route Summary */}
        <div className="space-y-2">
          {legs.map((leg, i) => {
            const info = getTransportInfo(leg.mode);
            const isLast = i === legs.length - 1;

            return (
              <div key={i} className="flex items-center gap-3">
                <div className={`w-10 h-10 rounded-full ${info.bg} flex items-center justify-center text-lg`}>
                  {info.icon}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-gray-900">{leg.from_name}</span>
                    <span className="text-gray-400">→</span>
                    <span className="font-medium text-gray-900">{leg.to_name}</span>
                  </div>
                  <div className="flex items-center gap-3 text-xs text-gray-500">
                    <span className={info.color}>{info.label}</span>
                    <span>{formatDuration(leg.duration_minutes)}</span>
                    {leg.service_number && <span>• {leg.service_number}</span>}
                  </div>
                </div>
                <div className="text-sm font-semibold text-gray-700">
                  {formatCurrency(leg.cost)}
                </div>
              </div>
            );
          })}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between pt-3 border-t border-gray-100">
          <div className="flex items-center gap-2">
            <div className={`px-2 py-1 rounded-full text-xs font-medium ${
              journey.reliability_score >= 0.8
                ? 'bg-emerald-100 text-emerald-700'
                : journey.reliability_score >= 0.6
                ? 'bg-amber-100 text-amber-700'
                : 'bg-red-100 text-red-700'
            }`}>
              {Math.round(journey.reliability_score * 100)}% Reliable
            </div>
            {legs.length > 1 && (
              <span className="text-sm text-gray-500">{legs.length - 1} transfer</span>
            )}
          </div>
          <span className="text-saffron-600 font-medium text-sm">View Details →</span>
        </div>

        {journey.warnings && journey.warnings.length > 0 && (
          <div className="flex items-start gap-2 p-3 bg-amber-50 rounded-lg">
            <span className="text-amber-500">⚠️</span>
            <p className="text-sm text-amber-700">{journey.warnings.join(', ')}</p>
          </div>
        )}
      </CardBody>
    </Card>
  );
}
