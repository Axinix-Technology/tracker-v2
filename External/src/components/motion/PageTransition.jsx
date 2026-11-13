import React, { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { motion, AnimatePresence, useReducedMotion } from 'motion/react';

/**
 * PageTransition: Route-level entrance & exit choreographer.
 * Wraps view outlets inside an AnimatePresence container to ensure page changes
 * animate smoothly with zero content flickering or layout shifts.
 *
 * @param {React.ReactNode} children - Active route element
 */
export function PageTransition({ children }) {
  const location = useLocation();
  const shouldReduceMotion = useReducedMotion();

  // Ensure scroll is restored cleanly on transition
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'instant' });
  }, [location.pathname]);

  if (shouldReduceMotion) {
    return <div key={location.pathname} className="w-full">{children}</div>;
  }

  const pageVariants = {
    initial: {
      opacity: 0,
      y: 12,
      filter: 'blur(2px)',
    },
    enter: {
      opacity: 1,
      y: 0,
      filter: 'blur(0px)',
      transition: {
        duration: 0.32,
        ease: [0.21, 0.47, 0.32, 0.98],
      },
    },
    exit: {
      opacity: 0,
      y: -8,
      filter: 'blur(2px)',
      transition: {
        duration: 0.2,
        ease: [0.32, 0, 0.67, 0],
      },
    },
  };

  return (
    <AnimatePresence mode="wait" initial={false}>
      <motion.div
        key={location.pathname}
        variants={pageVariants}
        initial="initial"
        animate="enter"
        exit="exit"
        className="w-full"
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
}

export default PageTransition;

