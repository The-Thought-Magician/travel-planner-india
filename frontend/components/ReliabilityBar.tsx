'use client';

interface Props {
  score: number; // 0-1
  label?: string;
  compact?: boolean;
}

export function ReliabilityBar({ score, label, compact }: Props) {
  const pct = Math.max(0, Math.min(1, score));
  const color =
    pct >= 0.85 ? 'bg-green-500' : pct >= 0.7 ? 'bg-amber-500' : 'bg-red-500';
  const width = (pct * 100).toFixed(0) + '%';
  return (
    <div className={compact ? 'flex items-center gap-2' : 'space-y-1'}>
      {label && !compact && (
        <div className="flex items-baseline justify-between text-xs">
          <span className="text-gray-600">{label}</span>
          <span className="tabular-nums text-gray-800">{(pct * 100).toFixed(0)}%</span>
        </div>
      )}
      <div className={`relative overflow-hidden rounded-full bg-gray-100 ${compact ? 'h-1.5 w-16' : 'h-2'}`}>
        <div className={`h-full ${color} transition-all`} style={{ width }} />
      </div>
      {compact && <span className="tabular-nums text-xs text-gray-600">{(pct * 100).toFixed(0)}%</span>}
    </div>
  );
}
