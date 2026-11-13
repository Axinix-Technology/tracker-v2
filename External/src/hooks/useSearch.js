import { useState, useMemo } from 'react';

export function useSearch(items = [], keys = ['title', 'name', 'description']) {
  const [query, setQuery] = useState('');

  const filteredItems = useMemo(() => {
    if (!query.trim()) return items;
    const lower = query.toLowerCase().trim();

    return items.filter(item => {
      return keys.some(key => {
        const val = item[key];
        if (typeof val === 'string') {
          return val.toLowerCase().includes(lower);
        }
        if (Array.isArray(val)) {
          return val.some(v => typeof v === 'string' && v.toLowerCase().includes(lower));
        }
        return false;
      });
    });
  }, [items, query, keys]);

  return {
    query,
    setQuery,
    filteredItems,
    hasMatches: filteredItems.length > 0,
  };
}

