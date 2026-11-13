import React from 'react';
import { cn } from '../../utils/cn';

export function Card({
  children,
  className = '',
  interactive = false,
  as: Component = 'div',
  ...props
}) {
  return (
    <Component
      className={cn(
        'bg-card/90 backdrop-blur-md border border-border/80 rounded-xl p-6 relative transition-all duration-300',
        interactive && 'hover:-translate-y-1 hover:border-gold/80 hover:shadow-xl hover:shadow-[#0E77C6]/15 cursor-pointer',
        className
      )}
      {...props}
    >
      {children}
    </Component>
  );
}
