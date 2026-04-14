'use client';

import { ConnectionRisk } from '@/types';

interface Props {
  risk: ConnectionRisk;
  compact?: boolean;
}

const COLORS: Record<ConnectionRisk['risk'], string> = {
  safe: 'bg-green-50 text-green-800 border-green-200',
  tight: 'bg-amber-50 text-amber-800 border-amber-200',
  risky: 'bg-red-50 text-red-800 border-red-200',
};

const ICONS: Record<ConnectionRisk['risk'], string> = {
  safe: '✓',
  tight: '⚠️',
  risky: '⛔',
};

export function ConnectionRiskBadge({ risk, compact }: Props) {
  const color = COLORS[risk.risk];
  return (
    <div
      className={`flex ${compact ? 'items-center gap-2' : 'flex-col gap-0.5'} rounded-md border px-3 py-2 text-xs ${color}`}
      title={risk.reason}
    >
      <div className="flex items-center gap-2 font-semibold">
        <span>{ICONS[risk.risk]}</span>
        <span className="uppercase tracking-wide">{risk.risk} transfer</span>
        <span className="font-normal">
          @ {risk.hub_from} → {risk.hub_to}
        </span>
      </div>
      <div className="font-normal">
        {risk.actual_buffer_minutes}m gap vs {risk.recommended_buffer_minutes}m recommended
      </div>
      {!compact && <div className="mt-1 text-[11px] font-normal opacity-80">{risk.reason}</div>}
    </div>
  );
}
