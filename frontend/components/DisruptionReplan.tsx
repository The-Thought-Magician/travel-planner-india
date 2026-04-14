'use client';

import { useState } from 'react';
import { Journey } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Props {
  journeyId: string;
  vehicleId: string;
  mode: string;
  onReplanned: (journeys: Journey[]) => void;
}

/** "If this leg is disrupted, re-plan around it" inline button. */
export function DisruptionReplan({ journeyId, vehicleId, mode, onReplanned }: Props) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const click = async () => {
    setBusy(true);
    setError(null);
    try {
      const url = `${API_BASE_URL}/api/v1/journeys/${journeyId}/replan?exclude_vehicle_id=${encodeURIComponent(vehicleId)}`;
      const r = await fetch(url, { method: 'POST' });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const data = await r.json();
      onReplanned(data.journeys || []);
    } catch (e: any) {
      setError(e?.message || 'Replan failed');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="inline-flex items-center gap-2">
      <button
        onClick={click}
        disabled={busy}
        title={`Get alternatives without ${mode} ${vehicleId}`}
        className="text-xs text-gray-600 hover:text-red-700 underline decoration-dotted underline-offset-2 disabled:opacity-50"
      >
        {busy ? 'Re-planning…' : `If ${mode} ${vehicleId} is disrupted, re-plan`}
      </button>
      {error && <span className="text-xs text-red-600">{error}</span>}
    </div>
  );
}
