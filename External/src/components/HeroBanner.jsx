import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, CheckCircle2, Sparkles } from 'lucide-react';
import { motion, useReducedMotion } from 'motion/react';
import { Button } from './ui/Button';
import { HeroVisualHub } from './HeroVisualHub';

/**
 * HeroBanner: Orchestrated pop-in entrance with Silicon-Valley aesthetic.
 * Sequences badge, headline, value proposition, and interactive preview canvas.
 */
export function HeroBanner({
  badge = 'AXINIX TECHNOLOGIES',
  title = 'Powering Every Industry.',
  highlight = 'Enabling Every Possibility.',
  description = 'From intelligent enterprise ERP and high-velocity retail POS to cloud architecture and digital applications, AXINIX streamlines multi-branch operations and accelerates business growth.',
  primaryAction = { label: 'Explore Our Solutions', to: '/solutions' },
  secondaryAction = { label: 'Book a Consultation', to: '/contact' },
}) {
  const shouldReduceMotion = useReducedMotion();

  // Motion variants for spring pop-ins
  const springTransition = (delay = 0, stiffness = 260, damping = 22) => ({
    type: 'spring',
    stiffness,
    damping,
    mass: 0.8,
    delay,
  });

  return (
    <section className="py-16 sm:py-24 px-4 sm:px-6 lg:px-8 border-b border-border/60 w-full text-foreground relative overflow-hidden bg-gradient-to-b from-[#1CC7F4]/10 via-[#0E77C6]/5 to-transparent dark:from-[#0E77C6]/15 dark:via-[#123E87]/10 dark:to-transparent">
      {/* Relative atmospheric highlight glows */}
      <div className="absolute -top-16 left-10 w-[700px] h-[450px] rounded-full bg-gradient-to-br from-[#1CC7F4]/14 via-[#0E77C6]/10 to-transparent blur-3xl pointer-events-none -z-0 opacity-60 dark:opacity-100" />
      <div className="absolute top-10 right-[-5%] w-[650px] h-[450px] rounded-full bg-gradient-to-bl from-[#05B292]/12 via-[#1CC7F4]/10 to-transparent blur-3xl pointer-events-none -z-0 opacity-60 dark:opacity-100" />

      <div className="max-w-[1600px] mx-auto px-4 sm:px-8 lg:px-12 xl:px-16 grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-16 items-center relative z-10">
        {/* Left Column: Hero Content */}
        <div className="lg:col-span-7 space-y-6 text-center lg:text-left">
          {/* Pop-in Badge */}
          <motion.div
            initial={shouldReduceMotion ? false : { opacity: 0, scale: 0.8, y: -8 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            transition={springTransition(0.08, 320, 20)}
            className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-gold/15 border border-gold/40 text-gold-hover dark:text-gold text-xs font-semibold tracking-wider uppercase backdrop-blur-md"
          >
            <Sparkles size={13} />
            <span>{badge}</span>
            <span className="w-1.5 h-1.5 rounded-full bg-gold animate-pulse" />
          </motion.div>

          {/* Pop-in H1 Headline */}
          <motion.h1
            initial={shouldReduceMotion ? false : { opacity: 0, scale: 0.94, y: 22 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            transition={springTransition(0.18, 240, 22)}
            className="text-3xl sm:text-5xl lg:text-6xl xl:text-7xl font-serif font-bold text-slate-900 dark:text-white tracking-tight leading-[1.1]"
          >
            {title} <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-gold-hover to-gold dark:from-gold dark:via-gold-light dark:to-white">
              {highlight}
            </span>
          </motion.h1>

          {/* Pop-in Description */}
          <motion.p
            initial={shouldReduceMotion ? false : { opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.45, delay: 0.28, ease: [0.21, 0.47, 0.32, 0.98] }}
            className="text-base sm:text-lg text-slate-600 dark:text-slate-300 max-w-2xl leading-relaxed mx-auto lg:mx-0"
          >
            {description}
          </motion.p>

          {/* Pop-in Action CTAs */}
          <motion.div
            initial={shouldReduceMotion ? false : { opacity: 0, scale: 0.9, y: 16 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            transition={springTransition(0.38, 280, 20)}
            className="pt-2 flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-3.5"
          >
            <Link to={primaryAction.to} className="w-full sm:w-auto">
              <Button size="lg" variant="gold" className="w-full sm:w-auto shadow-lg shadow-gold/25 gap-2 font-semibold transition-transform active:scale-95">
                <span>{primaryAction.label}</span>
                <ArrowRight size={16} />
              </Button>
            </Link>
            <Link to={secondaryAction.to} className="w-full sm:w-auto">
              <Button size="lg" variant="outline" className="w-full sm:w-auto text-slate-800 border-slate-300 hover:bg-slate-100 hover:border-gold dark:text-white dark:border-white/40 dark:hover:bg-white/10 dark:hover:border-gold transition-transform active:scale-95">
                {secondaryAction.label}
              </Button>
            </Link>
          </motion.div>

          {/* Pop-in Trust Indicators (Verified Architecture Truth) */}
          <motion.div
            initial={shouldReduceMotion ? false : { opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.45, delay: 0.48 }}
            className="pt-3 flex flex-wrap items-center justify-center lg:justify-start gap-y-2 gap-x-6 text-xs text-slate-500 dark:text-slate-400 font-medium"
          >
            <div className="flex items-center gap-1.5">
              <CheckCircle2 size={14} className="text-gold shrink-0" />
              <span>Physical Database-Per-Tenant Isolation</span>
            </div>
            <div className="flex items-center gap-1.5">
              <CheckCircle2 size={14} className="text-gold shrink-0" />
              <span>Unified Enterprise Portal</span>
            </div>
            <div className="flex items-center gap-1.5">
              <CheckCircle2 size={14} className="text-gold shrink-0" />
              <span>Modular Capability Scaling</span>
            </div>
          </motion.div>
        </div>

        {/* Right Column: Option 1 - Floating Holographic Brand Hub */}
        <motion.div
          initial={shouldReduceMotion ? false : { opacity: 0, scale: 0.92, y: 24 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          transition={springTransition(0.24, 220, 24)}
          className="lg:col-span-5 w-full flex items-center justify-center relative"
        >
          <HeroVisualHub />
        </motion.div>
      </div>
    </section>
  );
}
