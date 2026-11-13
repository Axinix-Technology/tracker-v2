import React, { useId } from 'react';
import { Check } from 'lucide-react';
import { SectionLink } from './SectionLink';
import { ScrollReveal } from '../motion';
import { cn } from '../../utils/cn';

/**
 * AlternatingFeatureSection
 * Unified single-card layout housing both Content and Visual panel in a 2-column split.
 * Automatically alternates desktop sides (Odd: Content Left / Visual Right, Even: Visual Left / Content Right).
 *
 * @param {string} [id] - Section anchor ID for smooth scrolling targets
 * @param {boolean} [reverse=false] - When true, swaps desktop sides (Visual Left, Content Right)
 * @param {Object} [feature] - Feature data object (title, description, benefits, cta, eyebrow)
 * @param {React.ReactNode} [contentCard] - Custom content override element
 * @param {React.ReactNode} [visualPanel] - Custom visual panel override element
 * @param {string} [className] - Optional custom section wrapper styling
 * @param {string} [cardClassName] - Optional class passed to the unified card container
 * @param {string} [panelClassName] - Optional class passed to the visual panel side
 */
export function AlternatingFeatureSection({
  id,
  reverse = false,
  feature,
  contentCard,
  visualPanel,
  className = '',
  cardClassName = '',
  panelClassName = '',
  ...props
}) {
  const headingId = useId();
  const title = feature?.title;
  const eyebrow = feature?.eyebrow;
  const description = feature?.description;
  const benefits = feature?.benefits || [];
  const cta = feature?.cta;

  return (
    <section
      id={id}
      className={cn(
        'w-full max-w-full overflow-hidden scroll-mt-24 sm:scroll-mt-28 py-4 sm:py-6 lg:py-8',
        className
      )}
      {...props}
    >
      <ScrollReveal
        direction={reverse ? 'right' : 'left'}
        distance={20}
        duration={0.45}
        className="w-full"
      >
        {/* Single Unified Card Container */}
        <article
          aria-labelledby={headingId}
          className={cn(
            'w-full rounded-2xl sm:rounded-3xl border border-border/80 bg-card/90 backdrop-blur-md',
            'shadow-xl shadow-black/5 dark:shadow-white/5 transition-all duration-300',
            'hover:border-border hover:shadow-2xl overflow-hidden',
            cardClassName
          )}
        >
          <div className="grid grid-cols-1 md:grid-cols-2 items-stretch">
            {/* Content Column */}
            <div
              className={cn(
                'flex flex-col justify-between p-6 sm:p-8 lg:p-10 xl:p-12',
                reverse ? 'md:order-2' : 'md:order-1'
              )}
            >
              {contentCard || (
                <>
                  <div className="space-y-4 sm:space-y-6">
                    {/* Eyebrow */}
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

                    {/* Description */}
                    {description && (
                      <p className="text-sm sm:text-base text-muted leading-relaxed">
                        {description}
                      </p>
                    )}

                    {/* Benefits List */}
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

                  {/* Call-to-Action Link */}
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
                </>
              )}
            </div>

            {/* Visual Panel Column with Sample Image */}
            <div
              className={cn(
                'w-full h-full min-h-[280px] sm:min-h-[340px] md:min-h-[420px] bg-slate-900/[0.04] dark:bg-black/30 relative flex items-center justify-center overflow-hidden p-4 sm:p-6 lg:p-8',
                reverse
                  ? 'md:order-1 border-t md:border-t-0 md:border-r border-border/60'
                  : 'md:order-2 border-t md:border-t-0 md:border-l border-border/60',
                panelClassName
              )}
            >
              {visualPanel || (
                <div className="w-full h-full min-h-[240px] sm:min-h-[300px] flex items-center justify-center relative rounded-xl sm:rounded-2xl overflow-hidden shadow-lg border border-white/10 group">
                  <img
                    src={feature?.image || (reverse ? '/hero_concept_1.jpg' : '/hero_concept_2.jpg')}
                    alt={feature?.title || 'Feature preview'}
                    className="w-full h-full object-cover rounded-xl sm:rounded-2xl transition-transform duration-700 ease-out group-hover:scale-105"
                    loading="lazy"
                  />
                  {/* Atmospheric gradient overlay */}
                  <div className="absolute inset-0 bg-gradient-to-t from-[#061126]/60 via-transparent to-transparent pointer-events-none" />

                  {/* Corner Accent Badge */}
                  <div className="absolute top-3 right-3 px-2.5 py-1 rounded-full bg-black/60 backdrop-blur-md border border-white/15 text-[10px] font-mono text-white/90">
                    {feature?.eyebrow || 'Preview'}
                  </div>
                </div>
              )}
            </div>
          </div>
        </article>
      </ScrollReveal>
    </section>
  );
}
