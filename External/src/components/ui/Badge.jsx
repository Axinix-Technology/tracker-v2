import React from 'react';
import { cn } from '../../utils/cn';

export function Badge({
  children,
  variant = 'soft',
  size = 'md',
  className = '',
  ...props
}) {
  const variants = {
    soft: 'bg-soft/10 text-royal-light border border-royal/30',
    gold: 'bg-gold/15 text-gold border border-gold/30',
    royal: 'bg-royal/20 text-white border border-royal/40',
    success: 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30',
    neutral: 'bg-white/5 text-muted border border-border/60',
  };

  const sizes = {
    sm: 'text-[11px] px-2 py-0.5 rounded-full font-medium',
    md: 'text-xs px-2.5 py-1 rounded-full font-medium',
  };

  return (
    <span
      className={cn('inline-flex items-center gap-1 leading-none select-none', variants[variant], sizes[size], className)}
      {...props}
    >
      {children}
    </span>
  );
}

