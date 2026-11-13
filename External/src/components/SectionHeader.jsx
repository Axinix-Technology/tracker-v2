import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';
import { Badge } from './ui/Badge';
import { Button } from './ui/Button';
import { cn } from '../utils/cn';

export function SectionHeader({
  badge,
  badgeVariant = 'gold',
  title,
  subtitle,
  actionText,
  actionTo,
  centered = false,
  className = '',
}) {
  if (centered) {
    return (
      <div className={cn('text-center max-w-2xl mx-auto mb-6 sm:mb-8', className)}>
        {badge && <Badge variant={badgeVariant} className="mb-2">{badge}</Badge>}
        <h2 className="text-2xl sm:text-3xl lg:text-4xl font-serif font-semibold text-foreground">
          {title}
        </h2>
        {subtitle && (
          <p className="text-xs sm:text-sm text-muted mt-2 leading-relaxed">
            {subtitle}
          </p>
        )}
      </div>
    );
  }

  return (
    <div className={cn('flex flex-col md:flex-row md:items-end justify-between mb-6 sm:mb-8 gap-4', className)}>
      <div>
        {badge && <Badge variant={badgeVariant} className="mb-2">{badge}</Badge>}
        <h2 className="text-2xl sm:text-3xl lg:text-4xl font-serif font-semibold text-foreground">
          {title}
        </h2>
        {subtitle && (
          <p className="text-xs sm:text-sm text-muted mt-1.5 max-w-xl leading-relaxed">
            {subtitle}
          </p>
        )}
      </div>
      {actionText && actionTo && (
        <Link to={actionTo} className="shrink-0">
          <Button variant="outline" size="sm">
            <span>{actionText}</span>
            <ArrowRight size={14} />
          </Button>
        </Link>
      )}
    </div>
  );
}

