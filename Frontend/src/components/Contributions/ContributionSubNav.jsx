import React from "react";
import { Link, useLocation } from "react-router-dom";
import { 
  LayoutDashboard, 
  PlusCircle, 
  Clock, 
  BarChart3, 
  Sparkles,
  TrendingUp
} from "lucide-react";

export default function ContributionSubNav({ openFollowUpsCount = 0 }) {
  const location = useLocation();
  const currentPath = location.pathname;

  const navItems = [
    {
      name: "Dashboard & Equity",
      to: "/contributions/dashboard",
      icon: LayoutDashboard,
      activePattern: /^\/contributions\/dashboard/,
      description: "KPIs & Shareholder %",
    },
    {
      name: "Add Work Status",
      to: "/contributions/add",
      icon: PlusCircle,
      activePattern: /^\/contributions\/add/,
      badge: "AI Powered",
      badgeColor: "bg-purple-100 text-purple-700 dark:bg-purple-950/70 dark:text-purple-300",
      description: "WhatsApp Chat Drop",
    },
    {
      name: "Follow-Ups",
      to: "/contributions/follow-ups",
      icon: Clock,
      activePattern: /^\/contributions\/follow-ups/,
      badge: openFollowUpsCount > 0 ? `${openFollowUpsCount} Open` : null,
      badgeColor: "bg-amber-100 text-amber-800 dark:bg-amber-950/70 dark:text-amber-300",
      description: "In-Progress Tasks",
    },
    {
      name: "Reports & Ledger",
      to: "/contributions/reports",
      icon: BarChart3,
      activePattern: /^\/contributions\/reports/,
      description: "Multi-Filter Audits",
    },
  ];

  return (
    <header className="mb-6 bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800/80 rounded-2xl p-3 shadow-xs">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        {/* Module Title & Identity */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-purple-600 via-indigo-600 to-blue-600 flex items-center justify-center text-white shadow-md shadow-purple-500/20">
            <TrendingUp className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-bold text-slate-900 dark:text-white tracking-tight">
                Work Contributions & Profit Sharing
              </h1>
              <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded-full bg-indigo-50 dark:bg-indigo-950/80 text-indigo-600 dark:text-indigo-400 border border-indigo-200/60 dark:border-indigo-800/60">
                Equity Ledger
              </span>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Deterministic point weighting directly powering shareholder profit distributions
            </p>
          </div>
        </div>

        {/* Tab Navigation Pill Group */}
        <nav aria-label="Contribution Sub-Navigation" className="flex items-center gap-1.5 p-1 bg-slate-100 dark:bg-slate-800/80 rounded-xl border border-slate-200/60 dark:border-slate-700/60 overflow-x-auto w-full md:w-auto">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = item.activePattern.test(currentPath) || (item.to === "/contributions/dashboard" && currentPath === "/contributions");

            return (
              <Link
                key={item.to}
                to={item.to}
                className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all shrink-0 ${
                  isActive
                    ? "bg-white dark:bg-slate-900 text-purple-700 dark:text-purple-300 shadow-xs font-semibold"
                    : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-white/60 dark:hover:bg-slate-700/50"
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isActive ? "text-purple-600 dark:text-purple-400" : "text-slate-400"}`} />
                <span>{item.name}</span>
                {item.badge && (
                  <span className={`text-[10px] font-bold px-1.5 py-0.2 rounded-md ${item.badgeColor || "bg-purple-100 text-purple-700"}`}>
                    {item.badge}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}

