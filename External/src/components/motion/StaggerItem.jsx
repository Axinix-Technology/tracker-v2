import React from 'react';
import { motion, useReducedMotion } from 'motion/react';

/**
 * StaggerItem: Child component to be nested inside a StaggerContainer.
 * Coordinates with parent's stagger timing to reveal itself smoothly.
 *
 * @param {'up' | 'down' | 'left' | 'right' | 'scale' | 'pop'} direction - Reveal vector
 * @param {number} distance - Movement distance in pixels (default 20)
 * @param {number} duration - Animation duration in seconds (default 0.45)
 * @param {boolean} spring - Whether to use spring physics (default false)
 * @param {string} className - Additional CSS classes
 * @param {React.ReactNode} children - Content
 */
export function StaggerItem({
  children,
  direction = 'up',
  distance = 20,
  duration = 0.45,
  spring = false,
  className = '',
  ...rest
}) {
  const shouldReduceMotion = useReducedMotion();

  if (shouldReduceMotion) {
    return <div className={className} {...rest}>{children}</div>;
  }

  const getHiddenVariant = () => {
    switch (direction) {
      case 'pop':
        return { opacity: 0, scale: 0.85, y: 16 };
      case 'up':
        return { opacity: 0, y: distance };
      case 'down':
        return { opacity: 0, y: -distance };
      case 'left':
        return { opacity: 0, x: distance };
      case 'right':
        return { opacity: 0, x: -distance };
      case 'scale':
        return { opacity: 0, scale: 0.95 };
      default:
        return { opacity: 0, y: distance };
    }
  };

  const transitionConfig = spring || direction === 'pop'
    ? {
      type: 'spring',
      stiffness: 280,
      damping: 20,
      mass: 0.7,
    }
    : {
      duration,
      ease: [0.21, 0.47, 0.32, 0.98],
    };

  const itemVariants = {
    hidden: getHiddenVariant(),
    visible: {
      opacity: 1,
      x: 0,
      y: 0,
      scale: 1,
      transition: transitionConfig,
    },
  };

  return (
    <motion.div variants={itemVariants} className={className} {...rest}>
      {children}
    </motion.div>
  );
}

export default StaggerItem;

