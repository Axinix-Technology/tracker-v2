import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';
import { cn } from '../../utils/cn';

/**
 * SectionLink
 * Accessible interactive call-to-action control that supports either:
 * 1. Smooth scrolling to a matching section anchor on the current page (`targetId`), or
 * 2. Route navigation to a dedicated destination page (`to`).
 *
 * Implements full keyboard navigation (Tab/Enter/Space), min 44px touch targets,
 * focus-visible rings, and active press feedback.
 *
 * @param {string} label - Text label for the CTA
 * @param {string} [targetId] - DOM element ID to smooth-scroll toward
 * @param {string} [to] - Route pathname for page navigation
 * @param {string} [className] - Additional class overrides
 * @param {() => void} [onClick] - Optional click handler callback
 */
export function SectionLink({
  label,
  targetId,
  to,
  className = '',
  onClick,
  children,
  ...props
}) {
  const handleAnchorScroll = (e) => {
    if (onClick) onClick(e);

    if (targetId) {
      const cleanId = targetId.replace(/^#/, '');
      const element = document.getElementById(cleanId);
      if (element) {
        e.preventDefault();
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
        // Update URL hash without hard jump
        if (window.history.pushState) {
          window.history.pushState(null, '', `#${cleanId}`);
        }
      }
    }
  };

  const baseStyles = cn(
    'inline-flex items-center gap-2 text-sm font-semibold transition-all duration-200',
    'rounded-lg px-4 py-2.5 min-h-[44px]',
    'text-foreground hover:text-foreground/80 hover:translate-x-0.5',
    'focus:outline-none focus-visible:ring-2 focus-visible:ring-current/40 focus-visible:ring-offset-2 focus-visible:ring-offset-background',
    'active:scale-[0.98] select-none cursor-pointer',
    className
  );

  const content = (
    <>
      <span>{label || children}</span>
      <ArrowRight size={16} className="shrink-0 transition-transform group-hover:translate-x-1" aria-hidden="true" />
    </>
  );

  // If a route navigation path is specified
  if (to) {
    return (
      <Link
        to={to}
        onClick={onClick}
        className={cn(baseStyles, 'group')}
        {...props}
      >
        {content}
      </Link>
    );
  }

  // Anchor smooth-scroll link or interactive button
  const href = targetId ? `#${targetId.replace(/^#/, '')}` : '#';

  return (
    <a
      href={href}
      onClick={handleAnchorScroll}
      className={cn(baseStyles, 'group')}
      {...props}
    >
      {content}
    </a>
  );
}

