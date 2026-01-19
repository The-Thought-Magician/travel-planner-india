'use client';

import React from 'react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  text?: string;
}

export function LoadingSpinner({ size = 'md', text }: LoadingSpinnerProps) {
  const sizes = {
    sm: 'w-6 h-6',
    md: 'w-12 h-12',
    lg: 'w-16 h-16',
  };

  return (
    <div className="flex flex-col items-center justify-center p-8">
      <div className={`${sizes[size]} animate-spin rounded-full border-4 border-saffron-200 border-t-saffron-600`} />
      {text && <p className="mt-4 text-gray-600">{text}</p>}
    </div>
  );
}
