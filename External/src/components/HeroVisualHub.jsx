import React from 'react';
import { motion, useReducedMotion } from 'motion/react';
import { ShieldCheck, Activity, GitBranch, Sparkles } from 'lucide-react';

/**
 * HeroVisualHub (Option 1: Floating Holographic Brand Hub)
 * Transforms the static hero logo into a 2026-grade enterprise centerpiece.
 * Features an organic floating 3D ribbon mark, ambient multi-color atmospheric glow,
 * and 3 interactive floating frosted-glass telemetry chips with subtle parallax physics.
 */
export function HeroVisualHub({ className = '' }) {
  const shouldReduceMotion = useReducedMotion();

  return (
    <div
      className={`relative w-full max-w-[460px] sm:max-w-[520px] mx-auto flex items-center justify-center min-h-[400px] sm:min-h-[460px] select-none ${className}`}
    >
      {/* 1. Atmospheric Ambient Radial Glow (Brand Multi-Color Spectrum) */}
      <div
        className="absolute w-[340px] sm:w-[420px] h-[340px] sm:h-[420px] rounded-full pointer-events-none -z-0 blur-3xl opacity-65 dark:opacity-85 transition-opacity"
        style={{
          background:
            'radial-gradient(circle, rgba(28,199,244,0.32) 0%, rgba(14,119,198,0.2) 40%, rgba(5,178,146,0.18) 65%, transparent 75%)',
        }}
        aria-hidden="true"
      />

      {/* Decorative Rotating Ambient Orbit Ring */}
      <motion.div
        animate={shouldReduceMotion ? false : { rotate: 360 }}
        transition={{ duration: 40, repeat: Infinity, ease: 'linear' }}
        className="absolute w-[320px] sm:w-[400px] h-[320px] sm:h-[400px] rounded-full border border-dashed border-[#1CC7F4]/20 dark:border-[#1CC7F4]/30 pointer-events-none -z-0"
        aria-hidden="true"
      />

      {/* 2. Floating Telemetry Chip 1: Top-Right (Live Cluster SLA) */}
      <motion.div
        initial={shouldReduceMotion ? false : { opacity: 0, y: -16, scale: 0.92 }}
        animate={
          shouldReduceMotion
            ? { opacity: 1, y: 0, scale: 1 }
            : {
                opacity: 1,
                y: [-5, 5, -5],
                scale: 1,
              }
        }
        transition={{
          y: { duration: 4.2, repeat: Infinity, ease: 'easeInOut' },
          default: { duration: 0.6, delay: 0.15 },
        }}
        className="absolute top-1 sm:top-3 right-0 sm:-right-4 z-20 flex items-center gap-2.5 px-3 py-1.5 sm:px-3.5 sm:py-2 rounded-2xl bg-white/90 dark:bg-[#0A1429]/90 backdrop-blur-xl border border-slate-200/80 dark:border-white/15 shadow-xl shadow-slate-900/5 dark:shadow-black/50 hover:scale-105 transition-transform"
      >
        <div className="w-7 h-7 rounded-xl bg-emerald-500/15 text-emerald-500 flex items-center justify-center shrink-0">
          <Activity size={14} className="animate-pulse" />
        </div>
        <div>
          <div className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-xs font-bold text-slate-900 dark:text-white">99.99% Uptime SLA</span>
          </div>
          <span className="text-[10px] text-slate-500 dark:text-slate-400 font-medium block">
            High-Availability Cluster
          </span>
        </div>
      </motion.div>

      {/* 3. Centerpiece: Floating 3D Ribbon Emblem + Vector Typography Lockup */}
      <motion.div
        animate={
          shouldReduceMotion
            ? false
            : {
                y: [-6, 6, -6],
              }
        }
        transition={{
          duration: 5.2,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
        whileHover={shouldReduceMotion ? undefined : { scale: 1.04 }}
        className="relative z-10 flex flex-col items-center justify-center cursor-pointer group"
      >
        {/* Crisp Transparent 3D Ribbon Monogram */}
        <div className="w-52 h-44 sm:w-68 sm:h-56 lg:w-76 lg:h-64 flex items-center justify-center">
          <img
            src="/axinix-emblem-transparent.png"
            alt="AXINIX Technology Monogram"
            className="w-full h-full object-contain drop-shadow-[0_16px_30px_rgba(14,119,198,0.3)] dark:drop-shadow-[0_20px_40px_rgba(28,199,244,0.35)] transition-transform duration-500 group-hover:scale-103"
            loading="eager"
          />
        </div>

        {/* Clean System Typography Lockup (Zero raster clipping) */}
        <div className="text-center mt-2 space-y-0.5">
          <div className="font-sans font-black text-lg sm:text-xl tracking-wider text-slate-900 dark:text-white uppercase flex items-center justify-center gap-1.5">
            <span>AXINIX</span>
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#1CC7F4] to-[#05B292]">TECHNOLOGY</span>
          </div>
          <p className="text-[11px] sm:text-xs font-semibold text-slate-500 dark:text-slate-400 tracking-wide">
            Innovating Tomorrow, Today.
          </p>
        </div>
      </motion.div>

      {/* 4. Floating Telemetry Chip 2: Mid-Left (Security & Isolation) */}
      <motion.div
        initial={shouldReduceMotion ? false : { opacity: 0, x: -16, scale: 0.92 }}
        animate={
          shouldReduceMotion
            ? { opacity: 1, x: 0, scale: 1 }
            : {
                opacity: 1,
                y: [5, -5, 5],
                scale: 1,
              }
        }
        transition={{
          y: { duration: 4.6, repeat: Infinity, ease: 'easeInOut', delay: 0.3 },
          default: { duration: 0.6, delay: 0.25 },
        }}
        className="absolute top-[38%] -translate-y-1/2 -left-2 sm:-left-6 z-20 flex items-center gap-2.5 px-3 py-1.5 sm:px-3.5 sm:py-2 rounded-2xl bg-white/90 dark:bg-[#0A1429]/90 backdrop-blur-xl border border-slate-200/80 dark:border-white/15 shadow-xl shadow-slate-900/5 dark:shadow-black/50 hover:scale-105 transition-transform"
      >
        <div className="w-7 h-7 rounded-xl bg-gold/15 text-gold flex items-center justify-center shrink-0">
          <ShieldCheck size={14} />
        </div>
        <div>
          <div className="text-xs font-bold text-slate-900 dark:text-white">Multi-Tenant Isolation</div>
          <span className="text-[10px] text-slate-500 dark:text-slate-400 font-medium block">
            Physical Database Per Tenant
          </span>
        </div>
      </motion.div>

      {/* 5. Floating Telemetry Chip 3: Bottom-Right (Distributed Branch Sync) */}
      <motion.div
        initial={shouldReduceMotion ? false : { opacity: 0, y: 16, scale: 0.92 }}
        animate={
          shouldReduceMotion
            ? { opacity: 1, y: 0, scale: 1 }
            : {
                opacity: 1,
                y: [-4, 6, -4],
                scale: 1,
              }
        }
        transition={{
          y: { duration: 4.4, repeat: Infinity, ease: 'easeInOut', delay: 0.6 },
          default: { duration: 0.6, delay: 0.4 },
        }}
        className="absolute -bottom-2 sm:bottom-0 right-1 sm:right-2 z-20 flex items-center gap-2.5 px-3 py-1.5 sm:px-3.5 sm:py-2 rounded-2xl bg-white/90 dark:bg-[#0A1429]/90 backdrop-blur-xl border border-slate-200/80 dark:border-white/15 shadow-xl shadow-slate-900/5 dark:shadow-black/50 hover:scale-105 transition-transform"
      >
        <div className="w-7 h-7 rounded-xl bg-[#1CC7F4]/15 text-[#1CC7F4] flex items-center justify-center shrink-0">
          <GitBranch size={14} />
        </div>
        <div>
          <div className="text-xs font-bold text-slate-900 dark:text-white">14+ Connected Branches</div>
          <span className="text-[10px] text-slate-500 dark:text-slate-400 font-medium block">
            Sub-Second Financial Sync
          </span>
        </div>
      </motion.div>
    </div>
  );
}

