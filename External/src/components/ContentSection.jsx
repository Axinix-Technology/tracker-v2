import React from 'react';
import { SectionHeader } from './SectionHeader';

/**
 * ContentSection: Standardized page section container with cohesive, tight spacing.
 * Eliminates oversized empty vertical gaps and raw inline section markup.
 */
export function ContentSection({
  badge,
  title,
  subtitle,
  actionText,
  actionTo,
  centered = false,
  bg = 'default',
  className = '',
  containerClassName = '',
  children,
}) {
  const bgClasses = {
    default: 'bg-transparent',
    card: 'bg-white/[0.015] border-t border-b border-white/[0.06]',
    deep: 'bg-white/[0.025] border-t border-b border-white/[0.06]',
    starfield: 'brand-mesh-bg border-t border-b border-border/80 text-white',
    mesh: 'brand-mesh-bg border-t border-b border-border/80 text-white',
  };

  const selectedBg = bgClasses[bg] || bgClasses.default;

  return (
    <section className={`py-12 sm:py-16 px-4 sm:px-8 lg:px-12 xl:px-16 w-full ${selectedBg} ${className}`}>
      <div className={`max-w-[1600px] mx-auto ${containerClassName}`}>
        {(badge || title || subtitle) && (
          <SectionHeader
            badge={badge}
            title={title}
            subtitle={subtitle}
            actionText={actionText}
            actionTo={actionTo}
            centered={centered}
          />
        )}
        {children}
      </div>
    </section>
  );
}
