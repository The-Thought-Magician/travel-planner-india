import React, { Suspense } from 'react';
import { HomePageContent } from '@/components/HomePageContent';
import { LoadingSpinner } from '@/components/LoadingSpinner';

export default function HomePage() {
  return (
    <Suspense fallback={<LoadingSpinner size="lg" />}>
      <HomePageContent />
    </Suspense>
  );
}
