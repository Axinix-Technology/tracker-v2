import React from 'react';
import { Breadcrumbs } from './ui/Breadcrumbs';
import { Badge } from './ui/Badge';
import { cn } from '../utils/cn';

export function PageBanner({
  title,
  subtitle,
  breadcrumbs = [],
  badge,
  badgeVariant = 'gold',
  initials,
  actions,
  children,
  className = '',
}) {
  return (
    <section className={cn(
      'py-9 sm:py-12 px-4 sm:px-8 lg:px-12 xl:px-16 border-b border-border/60 w-full text-foreground relative overflow-hidden',
      'bg-gradient-to-b from-[#1CC7F4]/10 via-[#0E77C6]/5 to-transparent dark:from-[#0E77C6]/18 dark:via-[#123E87]/12 dark:to-transparent',
      className
    )}>
      {/* Relative atmospheric highlight glow positioned behind the title & actions */}
      <div className="absolute top-0 left-1/4 w-[600px] h-[280px] rounded-full bg-gradient-to-br from-[#1CC7F4]/12 via-[#0E77C6]/8 to-transparent blur-3xl pointer-events-none -z-0 opacity-60 dark:opacity-100"></div>
      <div className="absolute -top-10 right-10 w-[450px] h-[240px] rounded-full bg-gradient-to-bl from-[#05B292]/10 via-[#1CC7F4]/8 to-transparent blur-3xl pointer-events-none -z-0 opacity-60 dark:opacity-100"></div>

      <div className="max-w-[1600px] mx-auto relative z-10">
        {breadcrumbs.length > 0 && <Breadcrumbs items={breadcrumbs} className="text-slate-600 dark:text-slate-300" />}

        <div className="mt-3 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-start sm:items-center gap-4">
            {initials && (
              <div className="w-14 h-14 rounded-xl bg-white/80 border border-slate-200 shadow-xs dark:bg-white/10 dark:border-transparent text-gold flex items-center justify-center font-bold font-serif text-2xl border-b-2 border-gold shrink-0 mt-1 sm:mt-0">
                {initials}
              </div>
            )}
            <div>
              {badge && (
                <div className="flex items-center gap-2 mb-1">
                  <Badge variant={badgeVariant} size="sm">{badge}</Badge>
                </div>
              )}
              <h1 className="text-3xl sm:text-4xl lg:text-5xl font-serif font-bold text-slate-900 dark:text-white tracking-tight leading-tight">
                {title}
              </h1>
            </div>
          </div>

          {actions && (
            <div className="flex items-center gap-3 shrink-0 self-start sm:self-auto pt-2 sm:pt-0">
              {actions}
            </div>
          )}
        </div>

        {subtitle && (
          <p className="text-sm sm:text-base text-slate-600 dark:text-slate-200/90 max-w-3xl mt-4 leading-relaxed">
            {subtitle}
          </p>
        )}

        {children}
      </div>
    </section>
  );
}
