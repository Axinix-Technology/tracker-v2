import React from 'react';
import { motion, useReducedMotion } from 'motion/react';

/**
 * ScrollReveal: Viewport-triggered fade & translate transformation.
 * Automatically respects user system accessibility preferences (prefers-reduced-motion).
 *
 * @param {'up' | 'down' | 'left' | 'right' | 'scale' | 'pop' | 'none'} direction - Entrance vector
 * @param {number} delay - Animation delay in seconds (default 0)
 * @param {number} duration - Animation duration in seconds (default 0.5)
 * @param {number} distance - Travel distance in pixels (default 24)
 * @param {boolean} spring - Whether to use snappy spring physics (default false)
 * @param {string} className - Additional CSS classes
 * @param {boolean} once - Whether to animate only once when entering viewport (default true)
 * @param {string} margin - Viewport rootMargin trigger threshold (default '-60px')
 * @param {React.ReactNode} children - Content to animate
 */
export function ScrollReveal({
  children,
  direction = 'up',
  delay = 0,
  duration = 0.5,
  distance = 24,
  spring = false,
  className = '',
  once = true,
  margin = '-60px',
  ...rest
}) {
  const shouldReduceMotion = useReducedMotion();

  if (shouldReduceMotion) {
    return <div className={className} {...rest}>{children}</div>;
  }

  const getInitialPosition = () => {
    switch (direction) {
      case 'pop':
        return { opacity: 0, scale: 0.88, y: 16 };
      case 'up':
        return { opacity: 0, y: distance, scale: 1 };
      case 'down':
        return { opacity: 0, y: -distance, scale: 1 };
      case 'left':
        return { opacity: 0, x: distance, scale: 1 };
      case 'right':
        return { opacity: 0, x: -distance, scale: 1 };
      case 'scale':
        return { opacity: 0, scale: 0.94, y: 0 };
      case 'none':
      default:
        return { opacity: 0, y: 0, scale: 1 };
    }
  };

  const transitionConfig = spring || direction === 'pop'
    ? {
      type: 'spring',
      stiffness: 260,
      damping: 20,
      mass: 0.8,
      delay,
    }
    : {
      duration,
      delay,
      ease: [0.21, 0.47, 0.32, 0.98], // Snappy cubic bezier
    };

  return (
    <motion.div
      initial={getInitialPosition()}
      whileInView={{
        opacity: 1,
        x: 0,
        y: 0,
        scale: 1,
      }}
      viewport={{ once, margin }}
      transition={transitionConfig}
      className={className}
      {...rest}
    >
      {children}
    </motion.div>
  );
}

export default ScrollReveal;

