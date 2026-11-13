import React, { useState, useEffect, useRef } from 'react';
import { Layers, Store, Cpu, Activity, CheckCircle2 } from 'lucide-react';

export function DashboardPreview() {
  const [activeTab, setActiveTab] = useState('erp');
  const [isPaused, setIsPaused] = useState(false);
  const [progress, setProgress] = useState(0);

  const tabOrder = ['erp', 'pos', 'cloud'];
  const SLIDE_DURATION = 5000; // 5 seconds per slide
  const INTERVAL_STEP = 50; // update progress every 50ms

  useEffect(() => {
    if (isPaused) return;

    const timer = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          // Switch to next tab
          setActiveTab(curr => {
            const nextIdx = (tabOrder.indexOf(curr) + 1) % tabOrder.length;
            return tabOrder[nextIdx];
          });
          return 0;
        }
        return prev + (INTERVAL_STEP / SLIDE_DURATION) * 100;
      });
    }, INTERVAL_STEP);

    return () => clearInterval(timer);
  }, [isPaused]);

  const handleTabClick = (tab) => {
    setActiveTab(tab);
    setProgress(0);
  };

  const pillars = {
    erp: {
      tag: 'Core Enterprise ERP',
      title: 'Unified Multi-Branch Operations',
      kpi: '₹14.8M+',
      kpiLabel: 'Monthly Throughput',
      stat2: '14 Branches',
      stat2Label: 'Real-time Linked',
      highlights: ['Automated GST & E-Way Invoicing', 'Zero-Downtime Stock Reconciliation', 'Role-Based Access (RBAC)'],
    },
    pos: {
      tag: 'Smart Retail POS',
      title: 'Sub-Second Counter Velocity',
      kpi: '< 0.8s',
      kpiLabel: 'Transaction Speed',
      stat2: '100% Offline',
      stat2Label: 'Resilient Sync',
      highlights: ['Barcode & Weighing Scale Interface', 'Automated FIFO Expiry Alerts', 'Multi-Terminal Cash Management'],
    },
    cloud: {
      tag: 'High-Availability Cloud',
      title: 'Mission-Critical Reliability',
      kpi: '99.99%',
      kpiLabel: 'Uptime SLA',
      stat2: '12ms',
      stat2Label: 'Global Latency',
      highlights: ['Encrypted Automated Backups', 'Private Cloud / On-Premise Escrow', '24/7 Dedicated Ops Response'],
    },
  };

  const current = pillars[activeTab];

  return (
    <div
      className="relative mx-auto max-w-xl lg:max-w-none w-full"
      onMouseEnter={() => setIsPaused(true)}
      onMouseLeave={() => setIsPaused(false)}
    >
      {/* Subtle ambient backglow */}
      <div className="absolute -inset-1.5 rounded-3xl bg-gradient-to-r from-[#0E77C6]/30 via-[#1CC7F4]/20 to-[#05B292]/30 blur-2xl opacity-70 pointer-events-none"></div>

      {/* Main Glassmorphic Window */}
      <div className="relative rounded-2xl border border-white/15 bg-[#0A1429]/95 backdrop-blur-xl shadow-2xl p-6 sm:p-8 text-white overflow-hidden transition-all">
        {/* Top Window Header Bar */}
        <div className="flex items-center justify-between pb-4 mb-5 border-b border-white/10 text-xs">
          <div className="flex items-center gap-2">
            <div className="flex gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-rose-500/80 inline-block"></span>
              <span className="w-2.5 h-2.5 rounded-full bg-amber-500/80 inline-block"></span>
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500/80 inline-block"></span>
            </div>
            <span className="text-xs font-mono text-slate-400 pl-2">axinix-core-v4.0</span>
          </div>

          <div className="flex items-center gap-2 text-xs font-mono">
            {isPaused && (
              <span className="text-[10px] px-1.5 py-0.2 rounded bg-white/10 text-slate-300">
                Paused
              </span>
            )}
            <span className="flex items-center gap-1.5 text-emerald-400">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span>All Systems Live</span>
            </span>
          </div>
        </div>

        {/* 3 Pillar Selector Tabs with Progress Indicator */}
        <div className="grid grid-cols-3 gap-2 p-1.5 bg-white/5 rounded-xl border border-white/10 mb-6">
          {tabOrder.map((tabKey) => {
            const isActive = activeTab === tabKey;
            const labels = {
              erp: { label: 'ERP', icon: Layers },
              pos: { label: 'POS', icon: Store },
              cloud: { label: 'Cloud', icon: Cpu },
            };
            const Item = labels[tabKey];
            const Icon = Item.icon;

            return (
              <button
                key={tabKey}
                type="button"
                onClick={() => handleTabClick(tabKey)}
                className={`relative overflow-hidden py-2.5 px-3 rounded-lg text-xs sm:text-sm font-semibold transition-all flex items-center justify-center gap-2 ${
                  isActive
                    ? 'bg-gold text-deep shadow-md font-bold'
                    : 'text-slate-300 hover:text-white hover:bg-white/5'
                }`}
              >
                <Icon size={15} className="relative z-10" />
                <span className="relative z-10">{Item.label}</span>

                {/* Progress Bar inside active button */}
                {isActive && (
                  <div
                    className="absolute bottom-0 left-0 h-1 bg-deep/40 transition-all ease-linear"
                    style={{ width: `${progress}%` }}
                  />
                )}
              </button>
            );
          })}
        </div>

        {/* Active Pillar Card with Smooth Fade */}
        <div key={activeTab} className="space-y-5 animate-in fade-in duration-200">
          <div className="flex items-start justify-between">
            <div>
              <span className="text-xs font-mono uppercase tracking-wider text-gold font-bold">
                {current.tag}
              </span>
              <h3 className="text-lg sm:text-xl font-serif font-bold text-white mt-0.5">
                {current.title}
              </h3>
            </div>
            <div className="w-9 h-9 rounded-xl bg-gold/15 text-gold flex items-center justify-center shrink-0 border border-gold/30">
              <Activity size={18} />
            </div>
          </div>

          {/* Two Key Metrics */}
          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 rounded-xl bg-white/5 border border-white/10">
              <div className="text-2xl sm:text-3xl font-serif font-bold text-white">
                {current.kpi}
              </div>
              <div className="text-xs text-slate-400 mt-1 font-medium">
                {current.kpiLabel}
              </div>
            </div>

            <div className="p-4 rounded-xl bg-white/5 border border-white/10">
              <div className="text-2xl sm:text-3xl font-serif font-bold text-emerald-400">
                {current.stat2}
              </div>
              <div className="text-xs text-slate-400 mt-1 font-medium">
                {current.stat2Label}
              </div>
            </div>
          </div>

          {/* Clean Feature Highlights with Checkmarks */}
          <div className="pt-3 space-y-2.5 border-t border-white/10">
            {current.highlights.map((h, i) => (
              <div key={i} className="flex items-center gap-2.5 text-xs sm:text-sm text-slate-200">
                <CheckCircle2 size={15} className="text-gold shrink-0" />
                <span>{h}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Minimal Footer Status Bar */}
        <div className="mt-6 pt-4 border-t border-white/10 flex items-center justify-between text-xs text-slate-400 font-mono">
          <span>Multi-tenant Isolation</span>
          <span className="text-gold font-semibold">100% Data Portability</span>
        </div>
      </div>
    </div>
  );
}
