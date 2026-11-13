import React from 'react';
import { COMPANY_STATS } from '../api/data';
import { cn } from '../utils/cn';
import { StaggerContainer, StaggerItem } from './motion';

export function StatsSection({
  stats = COMPANY_STATS,
  className = '',
}) {
  return (
    <section className={cn('py-10 sm:py-14 px-4 sm:px-6 lg:px-8 border-b border-white/10 w-full relative z-10', className)}>
      <div className="max-w-[1600px] mx-auto px-4 sm:px-8 lg:px-12 xl:px-16">
        <StaggerContainer
          staggerDelay={0.09}
          className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6 sm:gap-10 items-center justify-between text-center divide-y lg:divide-y-0 lg:divide-x divide-white/10"
        >
          {stats.map((stat, idx) => (
            <StaggerItem key={idx} direction="pop" className="pt-4 lg:pt-0 lg:px-4 space-y-1">
              <div className="text-3xl sm:text-4xl font-serif font-bold text-slate-900 dark:text-white tracking-tight">
                {stat.value}
              </div>
              <div className="text-xs font-semibold uppercase tracking-wider text-gold">
                {stat.label}
              </div>
              {stat.change && (
                <div className="text-[11px] text-slate-500 dark:text-slate-400">
                  {stat.change}
                </div>
              )}
            </StaggerItem>
          ))}
        </StaggerContainer>
      </div>
    </section>
  );
}

export default StatsSection;
