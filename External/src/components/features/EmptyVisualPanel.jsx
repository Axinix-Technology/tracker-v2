import React from 'react';
import { cn } from '../../utils/cn';

/**
 * EmptyVisualPanel
 * Reserves the visual area, dimensions, and responsive layout footprint
 * without rendering any inner content (no images, mockups, icons, or placeholders).
 * Fully prepared for future media injection while maintaining strict structural stability.
 *
 * @param {string} [aspectRatio='aspect-4/3'] - Geometric aspect ratio class
 * @param {string} [className] - Optional custom border / surface class overrides
 */
export function EmptyVisualPanel({
  aspectRatio = 'aspect-4/3',
  className = '',
  ...props
}) {
  return (
    <div
      aria-hidden="true"
      role="presentation"
      className={cn(
        'w-full rounded-2xl border border-border/70 bg-card/40 backdrop-blur-sm',
        'min-h-[280px] sm:min-h-[340px] lg:min-h-[400px]',
        aspectRatio,
        'transition-all duration-300',
        className
      )}
      {...props}
    />
  );
}

