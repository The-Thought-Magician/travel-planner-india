'use client';

import React, { useState, useEffect, useRef, useMemo } from 'react';
import { Input } from './ui/input';
import { Location, LocationSuggestion } from '@/types';
import { searchLocations } from '@/lib/api';
import { debounce } from '@/lib/utils';

interface LocationSearchProps {
  label: string;
  placeholder: string;
  value: string;
  onChange: (value: string) => void;
  onSelect: (location: LocationSuggestion) => void;
  icon?: React.ReactNode;
}

export function LocationSearch({
  label,
  placeholder,
  value,
  onChange,
  onSelect,
  icon,
}: LocationSearchProps) {
  const [suggestions, setSuggestions] = useState<LocationSuggestion[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // Create debounced search function
  const debouncedSearch = useMemo(
    () =>
      debounce(async (query: string) => {
        if (query.length < 2) {
          setSuggestions([]);
          return;
        }

        setIsLoading(true);
        try {
          const results = await searchLocations(query);
          setSuggestions(
            results.map((loc) => ({
              id: loc.id,
              name: loc.name,
              code: loc.code,
              type: loc.type,
              state: loc.state,
            }))
          );
        } catch (error) {
          console.error('Search failed:', error);
          setSuggestions([]);
        } finally {
          setIsLoading(false);
        }
      }, 300),
    []
  );

  useEffect(() => {
    debouncedSearch(value);
  }, [value, debouncedSearch]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = (suggestion: LocationSuggestion) => {
    onChange(suggestion.name);
    onSelect(suggestion);
    setIsOpen(false);
    setSuggestions([]);
  };

  const getTypeIcon = (type: string) => {
    const icons: Record<string, string> = {
      city: '🏙️',
      station: '🚂',
      airport: '✈️',
    };
    return icons[type] || '📍';
  };

  return (
    <div ref={containerRef} className="relative">
      <Input
        label={label}
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onFocus={() => setIsOpen(true)}
        leftIcon={icon}
      />
      {isOpen && (suggestions.length > 0 || isLoading) && (
        <div className="absolute z-50 w-full mt-2 bg-white rounded-xl shadow-xl border border-gray-100 overflow-hidden">
          {isLoading ? (
            <div className="px-4 py-8 text-center text-gray-500">
              <div className="inline-block animate-spin rounded-full h-6 w-6 border-2 border-saffron-500 border-t-transparent" />
            </div>
          ) : suggestions.length > 0 ? (
            <ul className="max-h-60 overflow-y-auto py-2">
              {suggestions.map((suggestion) => (
                <li
                  key={suggestion.id}
                  className="px-4 py-3 hover:bg-saffron-50 cursor-pointer transition-colors"
                  onClick={() => handleSelect(suggestion)}
                >
                  <div className="flex items-center gap-3">
                    <span className="text-xl">{getTypeIcon(suggestion.type)}</span>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-gray-900 truncate">{suggestion.name}</p>
                      <p className="text-sm text-gray-500">
                        {suggestion.code}
                        {suggestion.state && ` • ${suggestion.state}`}
                      </p>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <div className="px-4 py-8 text-center text-gray-500">
              No locations found
            </div>
          )}
        </div>
      )}
    </div>
  );
}
