import React, { useState } from 'react';
import { CheckCircle2, XCircle, Sparkles, ArrowRight, ShieldAlert, ShieldCheck } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Button } from './ui/Button';

export function ComparisonSection() {
  const [viewMode, setViewMode] = useState('with'); // 'with' | 'without'

  const points = [
    {
      title: 'Multi-Location Inventory Sync',
      traditional: 'Spreadsheet logs, stockouts between branches, manual phone call verifications.',
      axinix: 'Real-time automated sync, instant inter-branch transfers, zero stock discrepancies.',
    },
    {
      title: 'Checkout & Counter Velocity',
      traditional: 'Slow manual item lookups, peak-hour cashier queues, pricing entry errors.',
      axinix: 'Sub-second barcode scanning, electronic weighing scale interface, instant digital bills.',
    },
    {
      title: 'GST & Compliance Filing',
      traditional: 'Stressful end-of-month manual tallying, missing invoices, tax penalty risks.',
      axinix: 'Automated 1-click GSTR-1, GSTR-3B & E-Way bill generation with 100% audit trails.',
    },
    {
      title: 'Executive Visibility & Control',
      traditional: 'Waiting for weekly reports, blind spots across remote warehouses and staff.',
      axinix: 'Live multi-branch executive telemetry from any device with granular role access (RBAC).',
    },
  ];

  return (
    <section className="py-16 sm:py-24 px-4 sm:px-8 lg:px-12 xl:px-16 max-w-[1600px] mx-auto w-full relative">
      <div className="text-center max-w-2xl mx-auto space-y-3 mb-10">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-gold/15 text-gold text-xs font-semibold uppercase tracking-wider border border-gold/30">
          <Sparkles size={12} />
          <span>Operational Transformation</span>
        </div>
        <h2 className="text-2xl sm:text-4xl font-serif font-bold text-slate-900 dark:text-white">
          The Difference AXINIX Makes in Your Daily Operations.
        </h2>
        <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
          Toggle between legacy fragmented setups and the unified AXINIX ecosystem to see how your team saves hours every week.
        </p>
      </div>

      {/* Interactive 2-Way View Switcher */}
      <div className="flex justify-center mb-8">
        <div className="p-1 rounded-2xl bg-white/5 border border-slate-200 dark:border-white/10 flex items-center gap-1 shadow-inner">
          <button
            type="button"
            onClick={() => setViewMode('without')}
            className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs sm:text-sm font-semibold transition-all ${
              viewMode === 'without'
                ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30 font-bold shadow-md'
                : 'text-slate-500 dark:text-slate-400 hover:text-slate-200'
            }`}
          >
            <ShieldAlert size={15} />
            <span>Traditional Setup (Without AXINIX)</span>
          </button>

          <button
            type="button"
            onClick={() => setViewMode('with')}
            className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs sm:text-sm font-semibold transition-all ${
              viewMode === 'with'
                ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-bold shadow-md'
                : 'text-slate-500 dark:text-slate-400 hover:text-slate-200'
            }`}
          >
            <ShieldCheck size={15} />
            <span>Unified AXINIX Ecosystem</span>
          </button>
        </div>
      </div>

      {/* Comparison Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 animate-in fade-in duration-200">
        {points.map((pt, idx) => {
          const isAxinix = viewMode === 'with';
          return (
            <div
              key={idx}
              className={`rounded-2xl p-6 border transition-all ${
                isAxinix
                  ? 'bg-card/90 border-emerald-500/30 shadow-lg shadow-emerald-500/5 hover:border-emerald-400/60'
                  : 'bg-card/70 border-rose-500/20 shadow-xs hover:border-rose-400/40'
              }`}
            >
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs font-mono font-bold uppercase tracking-wider text-slate-400">
                  Pillar 0{idx + 1}
                </span>
                {isAxinix ? (
                  <div className="w-8 h-8 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center">
                    <CheckCircle2 size={17} />
                  </div>
                ) : (
                  <div className="w-8 h-8 rounded-full bg-rose-500/20 text-rose-400 flex items-center justify-center">
                    <XCircle size={17} />
                  </div>
                )}
              </div>

              <h3 className="text-base font-serif font-bold text-slate-900 dark:text-white mb-2">
                {pt.title}
              </h3>

              <p className={`text-xs sm:text-sm leading-relaxed ${isAxinix ? 'text-slate-600 dark:text-slate-200' : 'text-slate-500 dark:text-slate-400'}`}>
                {isAxinix ? pt.axinix : pt.traditional}
              </p>

              <div className="mt-4 pt-3 border-t border-border/40 text-[11px] font-mono">
                {isAxinix ? (
                  <span className="text-emerald-400 font-semibold flex items-center gap-1">
                    ✓ Operational Velocity
                  </span>
                ) : (
                  <span className="text-rose-400 font-semibold flex items-center gap-1">
                    ✕ Manual Friction
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Direct CTA */}
      <div className="mt-10 text-center">
        <Link to="/contact?subject=Upgrade%20from%20Legacy%20System">
          <Button variant="outline" size="md" className="gap-2 text-xs">
            <span>Upgrade Your Operations to AXINIX</span>
            <ArrowRight size={14} />
          </Button>
        </Link>
      </div>
    </section>
  );
}

