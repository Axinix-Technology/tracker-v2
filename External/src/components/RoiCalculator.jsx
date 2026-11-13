import React, { useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { Calculator, ArrowRight, Clock, ShieldCheck, Zap, Sparkles } from 'lucide-react';
import { Button } from './ui/Button';

export function RoiCalculator() {
  const [branches, setBranches] = useState(4);
  const [invoices, setInvoices] = useState(300);
  const [sector, setSector] = useState('retail');

  const sectors = [
    { id: 'retail', label: 'Retail & Supermarket', multiplier: 1.0 },
    { id: 'wholesale', label: 'Wholesale & Distribution', multiplier: 1.25 },
    { id: 'manufacturing', label: 'Manufacturing & BOM', multiplier: 1.4 },
    { id: 'healthcare', label: 'Healthcare & Pharma', multiplier: 1.15 },
  ];

  const currentSector = sectors.find(s => s.id === sector) || sectors[0];

  const calculations = useMemo(() => {
    // Dynamic formula
    const hoursSavedPerMonth = Math.round((branches * 24 + invoices * 0.18) * currentSector.multiplier);
    const annualSavingsAmount = Math.round(((branches * 95000) + (invoices * 180)) * currentSector.multiplier);

    const formattedLakhs = (annualSavingsAmount / 100000).toFixed(1);

    return {
      hoursSaved: hoursSavedPerMonth,
      annualSavings: `₹${formattedLakhs} Lakhs`,
      speedBoost: `${(2.8 + branches * 0.2).toFixed(1)}x`,
    };
  }, [branches, invoices, currentSector]);

  return (
    <section className="py-16 sm:py-24 px-4 sm:px-8 lg:px-12 xl:px-16 max-w-[1600px] mx-auto w-full relative">
      <div className="bg-gradient-to-br from-[#0A1429] via-[#060E1F] to-[#0A1429] border border-gold/30 rounded-3xl p-6 sm:p-10 lg:p-14 shadow-2xl text-white relative overflow-hidden">
        {/* Subtle background ambient mesh */}
        <div className="absolute top-0 right-0 w-[500px] h-[350px] rounded-full bg-gradient-to-bl from-[#05B292]/14 via-[#1CC7F4]/10 to-transparent blur-3xl pointer-events-none"></div>

        <div className="relative z-10 grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-14 items-center">
          {/* Left Column: Interactive Sliders & Controls */}
          <div className="lg:col-span-7 space-y-6">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-gold/15 text-gold text-xs font-semibold uppercase tracking-wider border border-gold/30">
              <Calculator size={13} />
              <span>Interactive ROI Estimator</span>
            </div>

            <h2 className="text-2xl sm:text-4xl font-serif font-bold text-white tracking-tight">
              See How Much Your Business <br className="hidden sm:inline" />
              Saves with AXINIX.
            </h2>

            <p className="text-xs sm:text-sm text-slate-300 leading-relaxed max-w-xl">
              Adjust the sliders below to estimate the monthly operational hours reclaimed and annual leakage prevented across your branches.
            </p>

            {/* Sector Selector */}
            <div className="space-y-2 pt-2">
              <label className="text-xs font-mono uppercase tracking-wider text-slate-400">
                Operational Sector
              </label>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                {sectors.map(sec => (
                  <button
                    key={sec.id}
                    type="button"
                    onClick={() => setSector(sec.id)}
                    className={`py-2 px-2.5 rounded-xl text-xs font-semibold transition-all truncate ${
                      sector === sec.id
                        ? 'bg-gold text-deep font-bold shadow-md'
                        : 'bg-white/5 hover:bg-white/10 text-slate-300 border border-white/10'
                    }`}
                  >
                    {sec.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Slider 1: Branches */}
            <div className="space-y-2.5 pt-2">
              <div className="flex items-center justify-between text-xs sm:text-sm">
                <span className="text-slate-300 font-medium">Number of Branches / Store Outlets</span>
                <span className="font-mono text-gold font-bold text-base px-3 py-0.5 rounded-lg bg-gold/15 border border-gold/30">
                  {branches} {branches === 1 ? 'Location' : 'Locations'}
                </span>
              </div>
              <input
                type="range"
                min="1"
                max="30"
                step="1"
                value={branches}
                onChange={(e) => setBranches(parseInt(e.target.value, 10))}
                className="w-full h-2 rounded-lg bg-white/10 accent-[#C69A43] cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-slate-500 font-mono">
                <span>1 Store</span>
                <span>15 Multi-Branch</span>
                <span>30+ Regional Chain</span>
              </div>
            </div>

            {/* Slider 2: Daily Invoices */}
            <div className="space-y-2.5 pt-2">
              <div className="flex items-center justify-between text-xs sm:text-sm">
                <span className="text-slate-300 font-medium">Daily Customer Invoices / Transactions</span>
                <span className="font-mono text-emerald-400 font-bold text-base px-3 py-0.5 rounded-lg bg-emerald-500/15 border border-emerald-500/30">
                  {invoices} / day
                </span>
              </div>
              <input
                type="range"
                min="50"
                max="2000"
                step="25"
                value={invoices}
                onChange={(e) => setInvoices(parseInt(e.target.value, 10))}
                className="w-full h-2 rounded-lg bg-white/10 accent-[#05B292] cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-slate-500 font-mono">
                <span>50 Orders</span>
                <span>1,000 High-Volume</span>
                <span>2,000+ Supermarket</span>
              </div>
            </div>
          </div>

          {/* Right Column: Dynamic Results Card */}
          <div className="lg:col-span-5 bg-[#0D1C38]/90 border border-gold/40 rounded-2xl p-6 sm:p-8 backdrop-blur-xl shadow-xl space-y-6">
            <div className="flex items-center justify-between pb-3 border-b border-white/10">
              <span className="text-xs font-mono uppercase tracking-wider text-slate-400">
                Estimated Operational Impact
              </span>
              <span className="text-xs font-semibold text-gold flex items-center gap-1">
                <Sparkles size={12} /> Live Calculations
              </span>
            </div>

            {/* Metric 1: Hours Saved */}
            <div className="p-4 rounded-xl bg-white/5 border border-white/10 space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-300 flex items-center gap-1.5">
                  <Clock size={14} className="text-gold" />
                  <span>Reconciliation Time Saved</span>
                </span>
                <span className="text-[10px] text-slate-400 font-mono">Monthly</span>
              </div>
              <div className="text-3xl sm:text-4xl font-serif font-bold text-white pt-1">
                {calculations.hoursSaved}+ <span className="text-sm font-sans font-normal text-slate-400">hrs / mo</span>
              </div>
            </div>

            {/* Metric 2: Revenue Leakage Prevented */}
            <div className="p-4 rounded-xl bg-white/5 border border-white/10 space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-300 flex items-center gap-1.5">
                  <ShieldCheck size={14} className="text-emerald-400" />
                  <span>Revenue Leakage Prevented</span>
                </span>
                <span className="text-[10px] text-slate-400 font-mono">Annualized</span>
              </div>
              <div className="text-3xl sm:text-4xl font-serif font-bold text-emerald-400 pt-1">
                {calculations.annualSavings} <span className="text-sm font-sans font-normal text-slate-400">/ yr</span>
              </div>
            </div>

            {/* Metric 3: Speed Multiplier */}
            <div className="p-3.5 rounded-xl bg-white/5 border border-white/10 flex items-center justify-between">
              <span className="text-xs text-slate-300 flex items-center gap-1.5">
                <Zap size={14} className="text-cyan" />
                <span>Counter Checkout Velocity</span>
              </span>
              <span className="text-base font-bold text-cyan font-mono">
                {calculations.speedBoost} Faster
              </span>
            </div>

            {/* Direct Consultation Link with Prefilled Calculations */}
            <div className="pt-2">
              <Link
                to={`/contact?subject=${encodeURIComponent(
                  `Savings Assessment Inquiry: ${branches} Branches, ${invoices} Invoices/day, ${calculations.annualSavings}/yr estimated savings`
                )}&service=ERP%20Software`}
                className="w-full block"
              >
                <Button variant="gold" size="lg" className="w-full gap-2 shadow-lg shadow-gold/25 font-semibold">
                  <span>Claim Custom Savings Plan</span>
                  <ArrowRight size={15} />
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

