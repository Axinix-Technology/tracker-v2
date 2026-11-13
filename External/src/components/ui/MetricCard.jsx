import React from 'react';
import { cn } from '../../utils/cn';

export function MetricCard({
  value,
  label,
  sublabel,
  icon: Icon,
  trend,
  className = '',
}) {
  return (
    <div className={cn('bg-card border border-border/80 rounded-lg p-5 flex flex-col justify-between transition-all hover:border-gold/50', className)}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-semibold text-muted tracking-wider uppercase">{label}</span>
        {Icon && (
          <div className="p-2 rounded bg-royal/10 text-royal-light border border-royal/20">
            <Icon size={16} />
          </div>
        )}
      </div>
      <div className="flex items-baseline gap-2">
        <span className="text-3xl font-serif font-bold text-foreground tracking-tight">{value}</span>
        {trend && (
          <span className="text-xs font-medium text-gold bg-gold/10 px-2 py-0.5 rounded">
            {trend}
          </span>
        )}
      </div>
      {sublabel && (
        <p className="text-xs text-muted mt-2">{sublabel}</p>
      )}
    </div>
  );
}
