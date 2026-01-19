import React from 'react';
import { cn } from '@/lib/utils';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'default' | 'outlined' | 'elevated';
  hover?: boolean;
  onClick?: () => void;
}

export function Card({
  children,
  className,
  variant = 'default',
  hover = false,
  onClick,
}: CardProps) {
  const variants = {
    default: 'bg-white border border-gray-100',
    outlined: 'bg-white border-2 border-gray-200',
    elevated: 'bg-white shadow-xl border-0',
  };

  return (
    <div
      className={cn(
        'rounded-2xl overflow-hidden transition-all duration-200',
        variants[variant],
        hover && 'hover:shadow-lg hover:border-saffron-200 cursor-pointer',
        className
      )}
      onClick={onClick}
    >
      {children}
    </div>
  );
}

interface CardHeaderProps {
  children: React.ReactNode;
  className?: string;
}

export function CardHeader({ children, className }: CardHeaderProps) {
  return (
    <div className={cn('px-6 py-4 border-b border-gray-100', className)}>
      {children}
    </div>
  );
}

interface CardBodyProps {
  children: React.ReactNode;
  className?: string;
}

export function CardBody({ children, className }: CardBodyProps) {
  return (
    <div className={cn('p-6', className)}>
      {children}
    </div>
  );
}

interface CardFooterProps {
  children: React.ReactNode;
  className?: string;
}

export function CardFooter({ children, className }: CardFooterProps) {
  return (
    <div className={cn('px-6 py-4 bg-gray-50 border-t border-gray-100', className)}>
      {children}
    </div>
  );
}
