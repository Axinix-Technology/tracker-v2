import React from 'react';
import { cn } from '../../utils/cn';

/**
 * FeaturePageHeader
 * Renders a centered eyebrow label and prominent headline.
 * Implements accessible heading structure and neutral, token-driven styling.
 *
 * @param {string} eyebrow - Centered eyebrow badge or category label
 * @param {string} title - Primary prominent headline
 * @param {string} [description] - Optional supporting contextual narrative
 * @param {string} [className] - Additional wrapper class overrides
 * @param {'h1' | 'h2' | 'h3'} [as='h2'] - Semantic heading tag to maintain document hierarchy
 */
export function FeaturePageHeader({
  eyebrow,
  title,
  description,
  className = '',
  as: HeadingTag = 'h2',
}) {
  return (
    <header className={cn('text-center max-w-3xl mx-auto space-y-3 mb-12 sm:mb-16 px-4', className)}>
      {eyebrow && (
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider border border-current/15 text-muted bg-card/60 backdrop-blur-xs select-none">
          <span className="w-1.5 h-1.5 rounded-full bg-current opacity-70" aria-hidden="true" />
          <span>{eyebrow}</span>
        </div>
      )}

      {title && (
        <HeadingTag className="text-2xl sm:text-4xl lg:text-5xl font-serif font-bold text-foreground tracking-tight leading-[1.15]">
          {title}
        </HeadingTag>
      )}

      {description && (
        <p className="text-sm sm:text-base text-muted max-w-2xl mx-auto leading-relaxed">
          {description}
        </p>
      )}
    </header>
  );
}

