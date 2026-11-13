import React, { useRef } from 'react';
import { motion, useScroll, useTransform, useReducedMotion } from 'motion/react';

/**
 * ScrollStoryboardSection: Scroll-progress-linked container for cinematic storytelling.
 * Animates opacity, subtle translation, and scale continuously as the section travels
 * through the user's viewport.
 *
 * @param {'fade-slide' | 'scale' | 'none'} effect - Transformation style
 * @param {string} className - Container CSS classes
 * @param {boolean} exitFade - Whether to smoothly fade out when scrolling past
 * @param {React.ReactNode | ((scrollProgress: MotionValue<number>) => React.ReactNode)} children
 */
export function ScrollStoryboardSection({
  children,
  effect = 'fade-slide',
  exitFade = false,
  className = '',
  ...rest
}) {
  const containerRef = useRef(null);
  const shouldReduceMotion = useReducedMotion();

  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start end', exitFade ? 'end start' : 'center center'],
  });

  // Calculate smooth scroll-driven values
  const opacity = useTransform(
    scrollYProgress,
    exitFade ? [0, 0.25, 0.75, 1] : [0, 0.3],
    exitFade ? [0, 1, 1, 0] : [0, 1]
  );

  const y = useTransform(
    scrollYProgress,
    exitFade ? [0, 0.3, 0.7, 1] : [0, 0.3],
    exitFade ? [40, 0, 0, -20] : [40, 0]
  );

  const scale = useTransform(
    scrollYProgress,
    exitFade ? [0, 0.3, 0.7, 1] : [0, 0.3],
    exitFade ? [0.96, 1, 1, 0.98] : [0.96, 1]
  );

  if (shouldReduceMotion || effect === 'none') {
    return (
      <div ref={containerRef} className={className} {...rest}>
        {typeof children === 'function' ? children(scrollYProgress) : children}
      </div>
    );
  }

  const styleProps = effect === 'scale'
    ? { opacity, scale }
    : { opacity, y };

  return (
    <motion.section
      ref={containerRef}
      style={styleProps}
      className={className}
      {...rest}
    >
      {typeof children === 'function' ? children(scrollYProgress) : children}
    </motion.section>
  );
}

export default ScrollStoryboardSection;

