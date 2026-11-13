import React from 'react';
import { Search } from 'lucide-react';

export function SearchFilterBar({
  search = '',
  onSearchChange,
  searchPlaceholder = 'Search items...',
  categories = [],
  selectedCategory,
  onCategoryChange,
  count,
  countLabel = 'results',
}) {
  return (
    <div className="space-y-6 mb-10">
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="relative w-full sm:max-w-md">
          <input
            type="text"
            placeholder={searchPlaceholder}
            value={search}
            onChange={(e) => onSearchChange?.(e.target.value)}
            className="w-full bg-card/90 backdrop-blur-md border border-border/80 rounded-xl py-2.5 pl-10 pr-4 text-xs sm:text-sm text-foreground focus:outline-none focus:border-gold focus:ring-1 focus:ring-gold transition-all shadow-sm"
          />
          <Search size={16} className="absolute left-3.5 top-3 text-muted" />
        </div>

        {typeof count === 'number' && (
          <div className="text-xs text-muted">
            Showing <b className="text-gold">{count}</b> {countLabel}
          </div>
        )}
      </div>

      {categories.length > 0 && onCategoryChange && (
        <div className="flex flex-wrap gap-2">
          {categories.map((cat, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => onCategoryChange(cat)}
              className={`px-3.5 py-1.5 rounded-full text-xs font-medium transition-all ${
                selectedCategory === cat
                  ? 'bg-royal text-white border border-royal shadow-md shadow-royal/20 font-semibold'
                  : 'bg-card/90 backdrop-blur-md border border-border/80 text-muted hover:text-foreground hover:border-gold/50'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

