import React, { forwardRef } from 'react';
import { cn } from '../../utils/cn';

export const Select = forwardRef(function Select(
  {
    label,
    options = [],
    error,
    helperText,
    className = '',
    required = false,
    id,
    ...props
  },
  ref
) {
  const selectId = id || props.name || Math.random().toString(36).substr(2, 6);

  return (
    <div className="w-full flex flex-col gap-1.5">
      {label && (
        <label htmlFor={selectId} className="text-xs font-medium text-muted uppercase tracking-wider flex items-center justify-between">
          <span>{label} {required && <span className="text-red-400">*</span>}</span>
        </label>
      )}
      <div className="relative">
        <select
          ref={ref}
          id={selectId}
          className={cn(
            'w-full px-3.5 py-2.5 rounded bg-card/60 border text-foreground text-sm transition-all duration-150 appearance-none cursor-pointer',
            'focus:outline-none focus:ring-1 focus:ring-gold focus:border-gold',
            error ? 'border-red-500 focus:ring-red-400 focus:border-red-500' : 'border-border/60 hover:border-border',
            className
          )}
          {...props}
        >
          {options.map((opt, idx) => {
            const isObj = typeof opt === 'object' && opt !== null;
            const value = isObj ? opt.value : opt;
            const text = isObj ? opt.label : opt;
            return (
              <option key={idx} value={value} className="bg-navy text-foreground">
                {text}
              </option>
            );
          })}
        </select>
        <div className="absolute right-3.5 top-1/2 -translate-y-1/2 pointer-events-none text-muted">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>
      {error ? (
        <p className="text-xs text-red-400 font-medium tracking-wide">{error}</p>
      ) : helperText ? (
        <p className="text-xs text-muted">{helperText}</p>
      ) : null}
    </div>
  );
});

