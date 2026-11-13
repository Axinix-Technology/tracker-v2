import React, { useState, useEffect, useMemo } from 'react';
import { Link } from 'react-router-dom';
import {
  Clock,
  DollarSign,
  CheckSquare,
  Headphones,
  TrendingUp,
  Receipt,
  Box,
  UserPlus,
  Users,
  MessageSquare,
  Check,
  Shield,
  Database,
  ArrowRight,
  Sparkles,
  Info,
  ChevronDown,
  ChevronUp,
  Lock,
  Layers,
  Loader2,
} from 'lucide-react';
import { populateHelper } from '../api/populateHelper';
import { Button } from './ui/Button';

// Icon mapping lookup for dynamic database strings
const ICON_LOOKUP = {
  Clock,
  DollarSign,
  CheckSquare,
  Headphones,
  TrendingUp,
  Receipt,
  Box,
  UserPlus,
  Users,
  MessageSquare,
  Layers,
};

export function WorkhubModuleCalculator() {
  const [modules, setModules] = useState([]);
  const [selectedIds, setSelectedIds] = useState(['attendance', 'payroll', 'tasks']);
  const [userCount, setUserCount] = useState(25);
  const [billingCycle, setBillingCycle] = useState('annual'); // 'annual' (20% discount) or 'monthly'
  const [activeCategory, setActiveCategory] = useState('All');
  const [expandedCards, setExpandedCards] = useState({});
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState(null);

  // 100% Dynamic Hydration: Fetch live catalog directly from MySQL via Populate Engine
  useEffect(() => {
    let isMounted = true;
    async function loadCatalog() {
      try {
        setIsLoading(true);
        setLoadError(null);
        const res = await populateHelper.query('module', {
          filter: { is_active: true },
          sort: 'name',
          limit: 50,
        });

        if (isMounted) {
          const fetched = res?.data || [];
          setModules(fetched);
          // Set initial default selections if available in live data
          if (fetched.length > 0) {
            const availableKeys = fetched.map(m => m.module_id);
            const initialDefaults = ['attendance', 'payroll', 'tasks'].filter(k => availableKeys.includes(k));
            if (initialDefaults.length > 0) {
              setSelectedIds(initialDefaults);
            } else {
              setSelectedIds([fetched[0].module_id]);
            }
          }
        }
      } catch (err) {
        if (isMounted) {
          console.error('Failed to load Workhub module catalog from Populate API:', err);
          setLoadError('Unable to load live catalog. Please refresh or contact sales.');
        }
      } finally {
        if (isMounted) setIsLoading(false);
      }
    }

    loadCatalog();
    return () => { isMounted = false; };
  }, []);

  // Dynamically derive category tabs from database records
  const categories = useMemo(() => {
    const cats = new Set(modules.map(m => m.category).filter(Boolean));
    return ['All', ...Array.from(cats)];
  }, [modules]);

  // Dynamic search and category filtering
  const filteredModules = useMemo(() => {
    return modules.filter(m => {
      const matchCat = activeCategory === 'All' || m.category === activeCategory;
      const q = searchQuery.toLowerCase().trim();
      const matchQuery =
        !q ||
        (m.name && m.name.toLowerCase().includes(q)) ||
        (m.description && m.description.toLowerCase().includes(q));
      return matchCat && matchQuery;
    });
  }, [modules, activeCategory, searchQuery]);

  // Dependency-aware selection toggle
  const handleToggle = (moduleId) => {
    setSelectedIds(prev => {
      const isSelected = prev.includes(moduleId);
      if (isSelected) {
        // Deselecting: deselect any module that lists this as a prerequisite
        return prev.filter(id => {
          if (id === moduleId) return false;
          const mod = modules.find(m => m.module_id === id);
          if (mod?.prerequisites?.includes(moduleId)) return false;
          return true;
        });
      } else {
        // Selecting: automatically include required prerequisites
        const targetMod = modules.find(m => m.module_id === moduleId);
        const toAdd = [moduleId];
        if (targetMod?.prerequisites?.length > 0) {
          targetMod.prerequisites.forEach(prereq => {
            if (!prev.includes(prereq)) {
              toAdd.push(prereq);
            }
          });
        }
        return [...prev, ...toAdd];
      }
    });
  };

  const toggleExpand = (id) => {
    setExpandedCards(prev => ({ ...prev, [id]: !prev[id] }));
  };

  // Pricing math directly derived from database fields
  const totalPerUserMonthly = useMemo(() => {
    return selectedIds.reduce((sum, id) => {
      const mod = modules.find(m => m.module_id === id);
      const price = parseFloat(mod?.price_per_user_monthly) || 30.0;
      return sum + price;
    }, 0);
  }, [selectedIds, modules]);

  const discountMultiplier = billingCycle === 'annual' ? 0.8 : 1.0;
  const effectivePerUser = Math.round(totalPerUserMonthly * discountMultiplier);
  const monthlyTotal = effectivePerUser * userCount;
  const annualTotal = monthlyTotal * 12;

  // Query parameter link for trial requests
  const trialLink = useMemo(() => {
    const params = new URLSearchParams({
      subject: 'Workhub Modular Platform Trial',
      modules: selectedIds.join(','),
      users: userCount.toString(),
      billing: billingCycle,
    });
    return `/contact?${params.toString()}`;
  }, [selectedIds, userCount, billingCycle]);

  return (
    <section className="w-full py-12 lg:py-20 relative">
      <div className="max-w-[1600px] mx-auto px-4 sm:px-8 lg:px-12 xl:px-16">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto space-y-4 mb-12">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-gold/10 border border-gold/30 text-gold text-xs font-semibold tracking-wider uppercase">
            <Sparkles size={13} />
            <span>MODULAR ENTERPRISE ARCHITECTURE</span>
          </div>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-serif font-bold text-slate-900 dark:text-white tracking-tight">
            Workhub Modular ERP Platform
          </h2>
          <p className="text-slate-600 dark:text-slate-300 text-base sm:text-lg">
            Purchase strictly what your enterprise needs. Add or downgrade modules seamlessly with physical database isolation, automated snapshot preservation, and zero data leakage.
          </p>
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="py-20 flex flex-col items-center justify-center gap-3 text-slate-500 dark:text-slate-400">
            <Loader2 size={32} className="animate-spin text-gold" />
            <span className="text-sm">Connecting to Workhub Control Plane catalog...</span>
          </div>
        )}

        {/* Error State */}
        {loadError && !isLoading && (
          <div className="p-6 rounded-2xl bg-rose-500/10 border border-rose-500/20 text-rose-600 dark:text-rose-400 text-center max-w-md mx-auto">
            <p className="text-sm font-medium">{loadError}</p>
          </div>
        )}

        {/* Dynamic Catalog UI */}
        {!isLoading && !loadError && (
          <>
            {/* Filter Bar */}
            <div className="flex flex-col md:flex-row items-center justify-between gap-4 mb-8">
              <div className="flex items-center gap-2 overflow-x-auto w-full md:w-auto pb-2 md:pb-0 scrollbar-none">
                {categories.map(cat => (
                  <button
                    key={cat}
                    onClick={() => setActiveCategory(cat)}
                    className={`px-4 py-2 rounded-xl text-xs sm:text-sm font-medium transition-all shrink-0 ${
                      activeCategory === cat
                        ? 'bg-gold text-slate-950 font-semibold shadow-md shadow-gold/20'
                        : 'bg-slate-100 dark:bg-white/5 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-white/10'
                    }`}
                  >
                    {cat}
                  </button>
                ))}
              </div>

              <div className="w-full md:w-72">
                <input
                  type="text"
                  placeholder="Search live module catalog..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full px-4 py-2 rounded-xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-sm text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:border-gold transition-colors"
                />
              </div>
            </div>

            {/* Modules Grid + Sticky Order Summary */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
              {/* Modules List */}
              <div className="lg:col-span-8 grid grid-cols-1 sm:grid-cols-2 gap-5">
                {filteredModules.map(mod => {
                  const mId = mod.module_id;
                  const isSelected = selectedIds.includes(mId);
                  const isExpanded = expandedCards[mId];
                  const IconComp = ICON_LOOKUP[mod.icon] || Box;
                  const price = parseFloat(mod.price_per_user_monthly) || 30.0;
                  const features = Array.isArray(mod.features) ? mod.features : [];
                  const prereqs = Array.isArray(mod.prerequisites) ? mod.prerequisites : [];

                  return (
                    <div
                      key={mId}
                      onClick={() => handleToggle(mId)}
                      className={`group relative rounded-2xl p-5 border transition-all cursor-pointer flex flex-col justify-between ${
                        isSelected
                          ? 'bg-gradient-to-br from-gold/10 via-gold/5 to-transparent border-gold/60 shadow-lg shadow-gold/5 ring-1 ring-gold/40'
                          : 'bg-white/60 dark:bg-white/[0.03] border-slate-200 dark:border-white/10 hover:border-slate-300 dark:hover:border-white/20 hover:shadow-md'
                      }`}
                    >
                      {/* Top Header */}
                      <div>
                        <div className="flex items-start justify-between gap-3 mb-3">
                          <div className="flex items-center gap-3">
                            <div
                              className={`w-10 h-10 rounded-xl flex items-center justify-center transition-colors ${
                                isSelected
                                  ? 'bg-gold text-slate-950 font-bold'
                                  : 'bg-slate-100 dark:bg-white/10 text-slate-700 dark:text-slate-200 group-hover:text-gold'
                              }`}
                            >
                              <IconComp size={20} />
                            </div>
                            <div>
                              <span className="text-xs uppercase tracking-wider font-semibold text-slate-400 dark:text-slate-400">
                                {mod.category || 'Operations'}
                              </span>
                              <h3 className="font-serif font-bold text-base text-slate-900 dark:text-white leading-tight">
                                {mod.name}
                              </h3>
                            </div>
                          </div>

                          {/* Checkbox Pill */}
                          <div
                            className={`w-6 h-6 rounded-lg flex items-center justify-center border transition-all ${
                              isSelected
                                ? 'bg-gold border-gold text-slate-950'
                                : 'border-slate-300 dark:border-white/20 bg-transparent group-hover:border-gold'
                            }`}
                          >
                            {isSelected && <Check size={14} strokeWidth={3} />}
                          </div>
                        </div>

                        {/* Description */}
                        <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 leading-relaxed mb-4">
                          {mod.description}
                        </p>

                        {/* Prerequisite Indicator */}
                        {prereqs.length > 0 && !selectedIds.includes(prereqs[0]) && (
                          <div className="mb-3 px-2.5 py-1.5 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-600 dark:text-amber-400 text-xs flex items-center gap-1.5">
                            <Info size={12} className="shrink-0" />
                            <span>Requires {prereqs.join(', ')} (auto-added on select)</span>
                          </div>
                        )}

                        {/* Features Drawer */}
                        {isExpanded && features.length > 0 && (
                          <ul className="space-y-1.5 mb-4 text-xs text-slate-600 dark:text-slate-300 pt-3 border-t border-slate-200/80 dark:border-white/10">
                            {features.map((feat, idx) => (
                              <li key={idx} className="flex items-start gap-2">
                                <span className="w-1.5 h-1.5 rounded-full bg-gold shrink-0 mt-1.5" />
                                <span>{feat}</span>
                              </li>
                            ))}
                          </ul>
                        )}
                      </div>

                      {/* Card Bottom: Dynamic Price & Expand */}
                      <div className="pt-3 border-t border-slate-200/60 dark:border-white/5 flex items-center justify-between text-xs">
                        <div>
                          <span className="font-bold text-slate-900 dark:text-white text-sm">
                            ₹{price.toFixed(0)}
                          </span>
                          <span className="text-slate-400"> /user/mo</span>
                        </div>

                        {features.length > 0 && (
                          <button
                            type="button"
                            onClick={(e) => {
                              e.stopPropagation();
                              toggleExpand(mId);
                            }}
                            className="text-slate-500 hover:text-gold dark:text-slate-400 dark:hover:text-gold transition-colors inline-flex items-center gap-1 font-medium"
                          >
                            <span>{isExpanded ? 'Less' : 'Features'}</span>
                            {isExpanded ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
                          </button>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Order Summary & Pricing Estimator */}
              <div className="lg:col-span-4 sticky top-24 space-y-6">
                <div className="rounded-3xl p-6 sm:p-7 bg-white dark:bg-[#071329] border border-slate-200 dark:border-white/10 shadow-2xl space-y-6">
                  {/* Header */}
                  <div className="flex items-center justify-between border-b border-slate-100 dark:border-white/10 pb-4">
                    <div>
                      <h4 className="font-serif font-bold text-lg text-slate-900 dark:text-white">
                        Modular Estimation
                      </h4>
                      <p className="text-xs text-slate-500 dark:text-slate-400">
                        {selectedIds.length} of {modules.length} modules selected
                      </p>
                    </div>
                    <div className="w-8 h-8 rounded-xl bg-gold/15 text-gold flex items-center justify-center">
                      <Database size={16} />
                    </div>
                  </div>

                  {/* Billing Switcher */}
                  <div className="space-y-2">
                    <label className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                      Billing Term
                    </label>
                    <div className="grid grid-cols-2 gap-2 p-1 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10">
                      <button
                        type="button"
                        onClick={() => setBillingCycle('annual')}
                        className={`py-2 px-3 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${
                          billingCycle === 'annual'
                            ? 'bg-gold text-slate-950 shadow-sm'
                            : 'text-slate-600 dark:text-slate-300 hover:text-gold'
                        }`}
                      >
                        <span>Annual</span>
                        <span className="text-[10px] bg-slate-950 text-gold px-1.5 py-0.5 rounded-full font-black">
                          -20%
                        </span>
                      </button>
                      <button
                        type="button"
                        onClick={() => setBillingCycle('monthly')}
                        className={`py-2 px-3 rounded-xl text-xs font-bold transition-all ${
                          billingCycle === 'monthly'
                            ? 'bg-gold text-slate-950 shadow-sm'
                            : 'text-slate-600 dark:text-slate-300 hover:text-gold'
                        }`}
                      >
                        Monthly
                      </button>
                    </div>
                  </div>

                  {/* Users Slider */}
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <label className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                        Team Size
                      </label>
                      <span className="text-sm font-bold text-slate-900 dark:text-white px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-white/10">
                        {userCount} Users
                      </span>
                    </div>
                    <input
                      type="range"
                      min="5"
                      max="250"
                      step="5"
                      value={userCount}
                      onChange={(e) => setUserCount(parseInt(e.target.value, 10))}
                      className="w-full accent-gold h-2 rounded-lg bg-slate-200 dark:bg-white/10 cursor-pointer"
                    />
                    <div className="flex justify-between text-[11px] text-slate-400">
                      <span>5 users</span>
                      <span>50 users</span>
                      <span>100 users</span>
                      <span>250+ users</span>
                    </div>
                  </div>

                  {/* Selected Tags */}
                  <div className="space-y-2">
                    <label className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                      Selected Modules
                    </label>
                    <div className="flex flex-wrap gap-1.5 max-h-32 overflow-y-auto pr-1">
                      {selectedIds.length === 0 ? (
                        <span className="text-xs text-slate-400 italic">Select at least one module</span>
                      ) : (
                        selectedIds.map(id => {
                          const m = modules.find(mod => mod.module_id === id);
                          return (
                            <span
                              key={id}
                              className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-gold/15 border border-gold/30 text-gold text-xs font-medium"
                            >
                              <span>{m?.name || id}</span>
                            </span>
                          );
                        })
                      )}
                    </div>
                  </div>

                  {/* Pricing Total */}
                  <div className="pt-4 border-t border-slate-100 dark:border-white/10 space-y-1">
                    <div className="flex items-baseline justify-between">
                      <span className="text-sm text-slate-500 dark:text-slate-400">
                        Total Investment:
                      </span>
                      <div className="text-right">
                        <span className="text-3xl font-serif font-black text-slate-900 dark:text-white">
                          ₹{monthlyTotal.toLocaleString('en-IN')}
                        </span>
                        <span className="text-xs text-slate-400 block">/ month</span>
                      </div>
                    </div>
                    {billingCycle === 'annual' && (
                      <p className="text-[11px] text-emerald-600 dark:text-emerald-400 text-right font-medium">
                        Billed annually (₹{annualTotal.toLocaleString('en-IN')}/year) — 20% discount applied
                      </p>
                    )}
                  </div>

                  {/* CTA Button */}
                  <div className="space-y-3 pt-2">
                    <Link to={trialLink} className="w-full block">
                      <Button variant="gold" size="lg" className="w-full justify-center font-bold text-sm shadow-xl shadow-gold/20">
                        <span>Deploy 14-Day Free Trial</span>
                        <ArrowRight size={16} />
                      </Button>
                    </Link>

                    <p className="text-[11px] text-center text-slate-500 dark:text-slate-400">
                      Dedicated tenant database · Instant activation · Cancel anytime
                    </p>
                  </div>

                  {/* Multi-Tenant Guarantees */}
                  <div className="pt-4 border-t border-slate-100 dark:border-white/10 space-y-2 text-xs text-slate-500 dark:text-slate-400">
                    <div className="flex items-center gap-2">
                      <Shield size={14} className="text-emerald-500 shrink-0" />
                      <span>Physical database-per-tenant isolation</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Database size={14} className="text-gold shrink-0" />
                      <span>30-Day cold archive & automated purge on degrade</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Lock size={14} className="text-sky-500 shrink-0" />
                      <span>Immutable JSON cross-module snapshot integrity</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </section>
  );
}
