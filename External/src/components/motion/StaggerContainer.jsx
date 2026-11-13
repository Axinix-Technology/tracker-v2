import React from 'react';
import { motion, useReducedMotion } from 'motion/react';

/**
 * StaggerContainer: Parent wrapper orchestrating sequential entrance animations
 * across multiple child StaggerItem elements (e.g. feature grids, card lists).
 *
 * @param {number} staggerDelay - Delay in seconds between each child reveal (default 0.08)
 * @param {number} initialDelay - Initial delay in seconds before first child starts (default 0.05)
 * @param {boolean} once - Whether to trigger only once on viewport entry (default true)
 * @param {string} margin - Viewport margin threshold (default '-60px')
 * @param {string} className - Additional CSS classes
 * @param {React.ReactNode} children - StaggerItem children
 */
export function StaggerContainer({
  children,
  staggerDelay = 0.08,
  initialDelay = 0.05,
  once = true,
  margin = '-60px',
  className = '',
  ...rest
}) {
  const shouldReduceMotion = useReducedMotion();

  if (shouldReduceMotion) {
    return <div className={className} {...rest}>{children}</div>;
  }

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: staggerDelay,
        delayChildren: initialDelay,
      },
    },
  };

  return (
    <motion.div
      initial="hidden"
      whileInView="visible"
      viewport={{ once, margin }}
      variants={containerVariants}
      className={className}
      {...rest}
    >
      {children}
    </motion.div>
  );
}

export default StaggerContainer;

