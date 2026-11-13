import React from 'react';
import { PROCESS_STEPS } from '../api/data';
import { cn } from '../utils/cn';

export function ProcessRoadmap({ steps = PROCESS_STEPS, className = '' }) {
  return (
    <div className={cn('grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 relative', className)}>
      {steps.map((step, idx) => (
        <div
          key={idx}
          className="bg-card border border-border/80 rounded-xl p-6 relative group hover:border-gold/60 transition-all"
        >
          <div className="text-3xl font-serif font-bold text-gold/80 mb-3">
            {step.number || `0${idx + 1}`}
          </div>
          <h3 className="text-lg font-serif font-semibold text-foreground mb-2">
            {step.title}
          </h3>
          <p className="text-xs text-muted leading-relaxed">
            {step.description || step.detail}
          </p>
        </div>
      ))}
    </div>
  );
}
