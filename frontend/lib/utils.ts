import { type ClassValue, clsx } from 'clsx';

/**
 * Merge Tailwind CSS classes
 */
export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

/**
 * Format currency in INR
 */
export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount);
}

/**
 * Format duration in minutes to readable string
 */
export function formatDuration(minutes: number): string {
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;

  if (hours === 0) return `${mins}m`;
  if (mins === 0) return `${hours}h`;
  return `${hours}h ${mins}m`;
}

/**
 * Format time string (HH:MM) to readable format
 */
export function formatTime(time: string): string {
  if (!time) return '--:--';

  const [hours, minutes] = time.split(':').map(Number);
  const period = hours >= 12 ? 'PM' : 'AM';
  const displayHours = hours % 12 || 12;

  return `${displayHours}:${minutes.toString().padStart(2, '0')} ${period}`;
}

/**
 * Get transport icon and color
 */
export function getTransportInfo(mode: string) {
  const info: Record<string, { icon: string; label: string; color: string; bg: string }> = {
    flight: {
      icon: '✈️',
      label: 'Flight',
      color: 'text-sky-600',
      bg: 'bg-sky-50',
    },
    train: {
      icon: '🚂',
      label: 'Train',
      color: 'text-emerald-600',
      bg: 'bg-emerald-50',
    },
    bus: {
      icon: '🚌',
      label: 'Bus',
      color: 'text-amber-600',
      bg: 'bg-amber-50',
    },
    auto: {
      icon: '🚗',
      label: 'Cab',
      color: 'text-purple-600',
      bg: 'bg-purple-50',
    },
  };

  return info[mode] || info.auto;
}

/**
 * Calculate reliability score color
 */
export function getReliabilityColor(score: number): string {
  if (score >= 0.8) return 'text-emerald-600';
  if (score >= 0.6) return 'text-amber-600';
  return 'text-red-600';
}

/**
 * Calculate reliability score background
 */
export function getReliabilityBg(score: number): string {
  if (score >= 0.8) return 'bg-emerald-100';
  if (score >= 0.6) return 'bg-amber-100';
  return 'bg-red-100';
}

/**
 * Debounce function
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null;

  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

/**
 * Generate a unique ID
 */
export function generateId(): string {
  return Math.random().toString(36).substring(2, 9);
}
