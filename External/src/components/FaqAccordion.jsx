import React, { useState } from 'react';
import { ChevronDown } from 'lucide-react';
import { cn } from '../utils/cn';

export function FaqAccordion({ title = 'Frequently Asked Questions', items = [] }) {
  const [openIndex, setOpenIndex] = useState(0);

  const toggle = (idx) => {
    setOpenIndex(prev => (prev === idx ? -1 : idx));
  };

  if (!items || items.length === 0) return null;

  return (
    <div className="w-full max-w-4xl mx-auto my-8">
      {title && (
        <h2 className="text-2xl sm:text-3xl font-serif font-semibold text-foreground mb-6">
          {title}
        </h2>
      )}
      <div className="divide-y divide-border/60 border-t border-b border-border/60">
        {items.map((item, idx) => {
          const isOpen = openIndex === idx;
          return (
            <div key={idx} className="py-4">
              <button
                type="button"
                onClick={() => toggle(idx)}
                className="w-full flex items-center justify-between text-left group focus:outline-none"
              >
                <span className="text-sm sm:text-base font-medium text-foreground group-hover:text-gold transition-colors pr-4">
                  {item.question || item[0]}
                </span>
                <ChevronDown
                  size={18}
                  className={cn(
                    'text-muted group-hover:text-gold transition-transform duration-200 shrink-0',
                    isOpen && 'rotate-180 text-gold'
                  )}
                />
              </button>
              {isOpen && (
                <div className="mt-3 text-xs sm:text-sm text-muted/90 leading-relaxed pr-6 animate-in fade-in duration-200">
                  {item.answer || item[1]}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

