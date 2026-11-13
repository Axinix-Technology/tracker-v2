import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence, useReducedMotion } from 'motion/react';

/**
 * PagePreloader: Enterprise reload and initial-mount loading experience.
 * Displays an orchestrated brand animation on hard reload or initial site entry,
 * then gracefully unlocks the page with an upward spring lift.
 */
export function PagePreloader({ onLoaded }) {
  const [isDone, setIsDone] = useState(false);
  const shouldReduceMotion = useReducedMotion();

  useEffect(() => {
    // Check if reduced motion is requested
    if (shouldReduceMotion) {
      setIsDone(true);
      if (onLoaded) onLoaded();
      return;
    }

    // Brief loading sequence for hard reloads (~750ms total)
    const timer = setTimeout(() => {
      setIsDone(true);
      if (onLoaded) onLoaded();
    }, 750);

    return () => clearTimeout(timer);
  }, [shouldReduceMotion, onLoaded]);

  return (
    <AnimatePresence>
      {!isDone && (
        <motion.div
          key="axinix-preloader"
          initial={{ opacity: 1 }}
          exit={{
            opacity: 0,
            scale: 1.03,
            filter: 'blur(6px)',
            transition: { duration: 0.45, ease: [0.21, 0.47, 0.32, 0.98] },
          }}
          className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-[#061126] text-white selection:bg-gold/30 selection:text-gold-light"
        >
          {/* Ambient luminous glow behind brand mark */}
          <div className="absolute w-[400px] h-[400px] rounded-full bg-gradient-to-tr from-[#123E87]/40 via-[#0E77C6]/30 to-[#05B292]/20 blur-[100px] pointer-events-none animate-pulse" />

          <div className="relative z-10 flex flex-col items-center gap-5 text-center px-4">
            {/* Animated Brand Emblem */}
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{
                duration: 0.45,
                ease: [0.34, 1.56, 0.64, 1],
              }}
              className="relative w-20 h-20 flex items-center justify-center"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" fill="none" className="w-full h-full drop-shadow-[0_0_24px_rgba(28,199,244,0.4)]">
                <defs>
                  <linearGradient id="preloaderGrad" x1="0%" y1="100%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor="#123E87" />
                    <stop offset="35%" stopColor="#0E77C6" />
                    <stop offset="70%" stopColor="#1CC7F4" />
                    <stop offset="100%" stopColor="#05B292" />
                  </linearGradient>
                </defs>
                <rect width="100" height="100" rx="22" fill="#0A1838" />
                <rect x="2" y="2" width="96" height="96" rx="20" stroke="url(#preloaderGrad)" strokeWidth="2.5" fill="none" />
                <path d="M24 76L50 22L76 76H62L50 48L38 76H24Z" fill="url(#preloaderGrad)" />
                <circle cx="50" cy="35" r="5" fill="#E5C378" />
              </svg>
            </motion.div>

            {/* Typography */}
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15, duration: 0.35 }}
              className="space-y-1.5"
            >
              <div className="text-xs uppercase tracking-[0.25em] font-semibold text-gold font-sans">
                AXINIX TECHNOLOGIES
              </div>
              <div className="text-[11px] text-slate-400 font-sans tracking-wide">
                Engineering Purpose-Built Enterprise Solutions
              </div>
            </motion.div>

            {/* Progress line indicator */}
            <div className="w-44 h-1 rounded-full bg-slate-800/80 overflow-hidden relative mt-2 border border-white/5">
              <motion.div
                initial={{ x: '-100%' }}
                animate={{ x: '0%' }}
                transition={{
                  duration: 0.65,
                  ease: [0.65, 0, 0.35, 1],
                }}
                className="w-full h-full bg-gradient-to-r from-[#123E87] via-[#1CC7F4] to-[#05B292]"
              />
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

export default PagePreloader;

