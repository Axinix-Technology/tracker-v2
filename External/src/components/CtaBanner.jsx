import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from './ui/Button';
import { Badge } from './ui/Badge';
import { cn } from '../utils/cn';
import { ScrollReveal } from './motion';

export function CtaBanner({
  badge,
  title = "Let's Build Something Powerful Together.",
  subtitle = "Tell us about your business goals and operational challenges. Our technology architects will demonstrate the exact software solution built for you.",
  primaryText,
  primaryTo,
  secondaryText,
  secondaryTo,
  primaryAction,
  secondaryAction,
  className = '',
}) {
  const pText = primaryAction?.label || primaryText || 'Contact Our Specialists';
  const pTo = primaryAction?.to || primaryTo || '/contact';
  const sText = secondaryAction?.label || secondaryText || 'Explore Solutions';
  const sTo = secondaryAction?.to || secondaryTo || '/solutions';

  return (
    <section className={cn(
      'py-12 sm:py-16 px-4 sm:px-6 lg:px-8 text-center border-t border-b border-border/60 w-full text-foreground relative overflow-hidden',
      'bg-gradient-to-b from-transparent via-[#0E77C6]/5 to-[#1CC7F4]/10 dark:via-[#123E87]/15 dark:to-[#0E77C6]/20',
      className
    )}>
      {/* Relative atmospheric glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[650px] h-[300px] rounded-full bg-gradient-to-r from-[#123E87]/15 via-[#1CC7F4]/10 to-[#05B292]/12 blur-3xl pointer-events-none -z-0 opacity-60 dark:opacity-100" />
      <ScrollReveal direction="pop" className="max-w-4xl mx-auto space-y-4 relative z-10">
        {badge && (
          <div className="inline-block">
            <Badge variant="gold" size="sm">
              {badge}
            </Badge>
          </div>
        )}
        <h2 className="text-2xl sm:text-3xl lg:text-4xl font-serif font-bold text-slate-900 dark:text-white">
          {title}
        </h2>
        <p className="text-base sm:text-lg text-slate-600 dark:text-slate-200/90 max-w-2xl mx-auto leading-relaxed">
          {subtitle}
        </p>
        <div className="pt-2 flex flex-col sm:flex-row items-center justify-center gap-3">
          <Link to={pTo} className="w-full sm:w-auto">
            <Button size="md" variant="gold" className="w-full sm:w-auto shadow-xl shadow-gold/25 font-semibold">
              {pText}
            </Button>
          </Link>
          <Link to={sTo} className="w-full sm:w-auto">
            <Button size="md" variant="outline" className="w-full sm:w-auto text-slate-800 border-slate-300 hover:bg-slate-100 hover:border-gold dark:text-white dark:border-white/40 dark:hover:bg-white/10 dark:hover:border-gold">
              {sText}
            </Button>
          </Link>
        </div>
      </ScrollReveal>
    </section>
  );
}

export default CtaBanner;
