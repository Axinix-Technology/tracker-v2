import React, { forwardRef } from 'react';
import { cn } from '../../utils/cn';

export const Textarea = forwardRef(function Textarea(
  {
    label,
    error,
    helperText,
    rows = 4,
    className = '',
    required = false,
    id,
    ...props
  },
  ref
) {
  const textareaId = id || props.name || Math.random().toString(36).substr(2, 6);

  return (
    <div className="w-full flex flex-col gap-1.5">
      {label && (
        <label htmlFor={textareaId} className="text-xs font-medium text-muted uppercase tracking-wider flex items-center justify-between">
          <span>{label} {required && <span className="text-red-400">*</span>}</span>
        </label>
      )}
      <textarea
        ref={ref}
        id={textareaId}
        rows={rows}
        className={cn(
          'w-full px-3.5 py-2.5 rounded bg-card/60 border text-foreground placeholder:text-muted/60 text-sm transition-all duration-150 resize-y',
          'focus:outline-none focus:ring-1 focus:ring-gold focus:border-gold',
          error ? 'border-red-500 focus:ring-red-400 focus:border-red-500' : 'border-border/60 hover:border-border',
          className
        )}
        {...props}
      />
      {error ? (
        <p className="text-xs text-red-400 font-medium tracking-wide">{error}</p>
      ) : helperText ? (
        <p className="text-xs text-muted">{helperText}</p>
      ) : null}
    </div>
  );
});

