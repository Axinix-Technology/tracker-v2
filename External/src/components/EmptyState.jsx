import React from 'react';
import { Button } from './ui/Button';

export function EmptyState({
  title = 'No items found',
  description = 'Try adjusting your search criteria or reset active filters.',
  onReset,
  resetLabel = 'Reset Filters',
  action,
}) {
  return (
    <div className="text-center py-16 bg-card border border-border/80 rounded-xl space-y-4">
      <h3 className="text-base font-serif font-semibold text-foreground">{title}</h3>
      {description && <p className="text-xs sm:text-sm text-muted max-w-sm mx-auto">{description}</p>}
      {onReset && (
        <Button variant="outline" size="sm" onClick={onReset} className="mt-2">
          {resetLabel}
        </Button>
      )}
      {action && <div className="pt-2">{action}</div>}
    </div>
  );
}

