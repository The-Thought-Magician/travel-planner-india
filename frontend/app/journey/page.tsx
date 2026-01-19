import React, { Suspense } from 'react';
import { JourneyDetailContent } from '@/components/JourneyDetailContent';
import { LoadingSpinner } from '@/components/LoadingSpinner';

export default function JourneyDetailPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    }>
      <JourneyDetailContent />
    </Suspense>
  );
}
