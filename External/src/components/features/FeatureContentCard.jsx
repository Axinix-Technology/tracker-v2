import React, { useId } from 'react';
import { Check } from 'lucide-react';
import { SectionLink } from './SectionLink';
import { cn } from '../../utils/cn';

/**
 * FeatureContentCard
 * Displays a feature domain's title, description, three benefit bullets, and CTA link.
 * Implements accessible semantic markup, tactile interactions, and token-driven neutral styling.
 *
 * @param {string} title - Section title (e.g. "Plan", "Automate", "Report")
 * @param {string} [eyebrow] - Optional domain tag/eyebrow
 * @param {string} description - Short overview description
 * @param {string[]} benefits - Array of benefit bullet points (ideally 3 items)
 * @param {{ label: string, targetId?: string, to?: string }} cta - Call-to-action link config
 * @param {string} [className] - Optional custom styling overrides
 */
export function FeatureContentCard({
  title,
  eyebrow,
  description,
  benefits = [],
  cta,
  className = '',
  ...props
}) {
  const headingId = useId();

  return (
    <article
      aria-labelledby={headingId}
      className={cn(
        'w-full flex flex-col justify-between rounded-2xl',
        'border border-border/80 bg-card/90 backdrop-blur-md',
        'p-6 sm:p-8 lg:p-10 transition-all duration-300',
        'hover:border-border hover:shadow-lg hover:shadow-black/5 dark:hover:shadow-white/5',
        'focus-within:ring-2 focus-within:ring-current/20',
        className
      )}
      {...props}
    >
      <div className="space-y-4 sm:space-y-6">
        {/* Optional Eyebrow */}
        {eyebrow && (
          <div className="text-xs font-semibold tracking-wider uppercase text-muted">
            {eyebrow}
          </div>
        )}

        {/* Title */}
        <h3
          id={headingId}
          className="text-2xl sm:text-3xl font-serif font-bold text-foreground tracking-tight leading-snug"
        >
          {title}
        </h3>

        {/* Short Description */}
        {description && (
          <p className="text-sm sm:text-base text-muted leading-relaxed">
            {description}
          </p>
        )}

        {/* Three Benefit Bullets */}
        {Array.isArray(benefits) && benefits.length > 0 && (
          <ul
            role="list"
            className="space-y-2.5 sm:space-y-3 pt-2 text-sm text-foreground/90"
          >
            {benefits.map((benefit, idx) => (
              <li
                key={idx}
                className="flex items-start gap-2.5 sm:gap-3 leading-snug"
              >
                <div
                  className="mt-0.5 w-5 h-5 rounded-full flex items-center justify-center shrink-0 border border-current/20 bg-card text-foreground"
                  aria-hidden="true"
                >
                  <Check size={12} strokeWidth={2.5} />
                </div>
                <span>{benefit}</span>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Relevant Call-to-Action Link */}
      {cta && (
        <div className="pt-6 sm:pt-8 mt-4 border-t border-border/50">
          <SectionLink
            label={cta.label}
            targetId={cta.targetId}
            to={cta.to}
            className="w-full sm:w-auto justify-between sm:justify-start bg-foreground/5 hover:bg-foreground/10 border border-border/60"
          />
        </div>
      )}
    </article>
  );
}

