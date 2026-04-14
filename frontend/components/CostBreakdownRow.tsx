'use client';

import { CostBreakdown } from '@/types';

interface Props {
  breakdown: CostBreakdown;
}

function inr(value: number): string {
  return '₹' + value.toLocaleString('en-IN');
}

export function CostBreakdownRow({ breakdown }: Props) {
  const rows: { label: string; value: number; note?: string }[] = [
    { label: 'Tickets', value: breakdown.tickets, note: 'Flight / train / bus fares' },
    { label: 'Last-mile (auto/cab/transfers)', value: breakdown.last_mile },
    { label: 'Booking fees', value: breakdown.booking_fees, note: '≈3% flights, 1% buses' },
    { label: 'Meals & incidentals', value: breakdown.meals_incidentals, note: '₹150/meal block over 6h' },
  ];
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-3">
      <div className="flex items-baseline justify-between mb-2">
        <h4 className="text-sm font-semibold text-gray-900">True door-to-door cost</h4>
        <span className="text-lg font-bold text-saffron-700">{inr(breakdown.total)}</span>
      </div>
      <ul className="space-y-1 text-sm">
        {rows.map((r) => (
          <li key={r.label} className="flex items-baseline justify-between">
            <span className="text-gray-700">
              {r.label}
              {r.note && <span className="ml-1 text-xs text-gray-400">({r.note})</span>}
            </span>
            <span className="tabular-nums text-gray-900">{inr(r.value)}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
