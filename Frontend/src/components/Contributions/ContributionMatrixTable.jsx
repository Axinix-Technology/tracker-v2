import React, { useState, useMemo } from "react";
import { Award, DollarSign, Calculator, ChevronRight, ShieldCheck } from "lucide-react";

export default function ContributionMatrixTable({ contributions = [] }) {
  const [profitPool, setProfitPool] = useState(500000); // Default ₹5 Lakhs simulation
  const [activeTab, setActiveTab] = useState("all"); // 'all' | 'project' | 'company' | 'combined'

  // Aggregate points by member and scope
  const summary = useMemo(() => {
    const memberMap = {};

    let totalProjectPoints = 0;
    let totalCompanyPoints = 0;
    let totalProjectEntries = 0;
    let totalCompanyEntries = 0;

    // Fixed canonical list of team members to ensure everyone appears on the roster
    const defaultRoster = [
      "Arunbharathi",
      "Ajay",
      "Siva Anna",
      "Rithika",
      "Karuppasamy",
      "Ruthran",
      "Guruprasath",
      "Boopalan",
    ];

    defaultRoster.forEach((name) => {
      memberMap[name] = {
        name,
        projectPoints: 0,
        projectEntries: 0,
        companyPoints: 0,
        companyEntries: 0,
      };
    });

    contributions.forEach((c) => {
      // Resolve member display name cleanly
      const name = c.user?.first_name || c.user?.username || (c.project_name?.includes("Arun") ? "Arunbharathi" : "Team Member");
      if (!memberMap[name]) {
        memberMap[name] = {
          name,
          projectPoints: 0,
          projectEntries: 0,
          companyPoints: 0,
          companyEntries: 0,
        };
      }

      const points = parseFloat(c.final_points) || 0;
      const scope = (c.scope || "").toLowerCase();

      if (scope.includes("project")) {
        memberMap[name].projectPoints += points;
        memberMap[name].projectEntries += 1;
        totalProjectPoints += points;
        totalProjectEntries += 1;
      } else {
        memberMap[name].companyPoints += points;
        memberMap[name].companyEntries += 1;
        totalCompanyPoints += points;
        totalCompanyEntries += 1;
      }
    });

    const totalCombinedPoints = totalProjectPoints + totalCompanyPoints;

    const list = Object.values(memberMap).map((m) => {
      const combinedPoints = m.projectPoints + m.companyPoints;
      const combinedEntries = m.projectEntries + m.companyEntries;
      const projectShare = totalProjectPoints > 0 ? (m.projectPoints / totalProjectPoints) * 100 : 0;
      const companyShare = totalCompanyPoints > 0 ? (m.companyPoints / totalCompanyPoints) * 100 : 0;
      const combinedShare = totalCombinedPoints > 0 ? (combinedPoints / totalCombinedPoints) * 100 : 0;
      const payout = (combinedShare / 100) * profitPool;

      return {
        ...m,
        combinedPoints,
        combinedEntries,
        projectShare,
        companyShare,
        combinedShare,
        payout,
      };
    });

    // Sort descending by combined points
    list.sort((a, b) => b.combinedPoints - a.combinedPoints);

    return {
      members: list,
      totalProjectPoints,
      totalCompanyPoints,
      totalCombinedPoints,
      totalProjectEntries,
      totalCompanyEntries,
      totalCombinedEntries: totalProjectEntries + totalCompanyEntries,
    };
  }, [contributions, profitPool]);

  // Distinct color tokens for top shareholders
  const memberColors = [
    "bg-indigo-600 dark:bg-indigo-500",
    "bg-emerald-600 dark:bg-emerald-500",
    "bg-purple-600 dark:bg-purple-500",
    "bg-amber-600 dark:bg-amber-500",
    "bg-sky-600 dark:bg-sky-500",
    "bg-rose-600 dark:bg-rose-500",
    "bg-slate-500 dark:bg-slate-400",
    "bg-slate-400 dark:bg-slate-500",
  ];

  return (
    <div className="space-y-6">
      {/* 1. Top Telemetry KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Project Points */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800/80 rounded-2xl p-4 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-medium">
            <span>PROJECT CONTRIBUTIONS</span>
            <span className="p-1.5 rounded-lg bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400">📁</span>
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-extrabold text-slate-900 dark:text-white tracking-tight">
              {summary.totalProjectPoints.toFixed(2)}
            </span>
            <span className="text-xs font-semibold text-blue-600 dark:text-blue-400">pts</span>
          </div>
          <div className="mt-2 text-[11px] text-slate-500 dark:text-slate-400">
            {summary.totalProjectEntries} billable client activities
          </div>
        </div>

        {/* Company Points */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800/80 rounded-2xl p-4 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-medium">
            <span>COMPANY CONTRIBUTIONS</span>
            <span className="p-1.5 rounded-lg bg-purple-50 dark:bg-purple-950/60 text-purple-600 dark:text-purple-400">🏢</span>
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-extrabold text-slate-900 dark:text-white tracking-tight">
              {summary.totalCompanyPoints.toFixed(2)}
            </span>
            <span className="text-xs font-semibold text-purple-600 dark:text-purple-400">pts</span>
          </div>
          <div className="mt-2 text-[11px] text-slate-500 dark:text-slate-400">
            {summary.totalCompanyEntries} internal IP & asset milestones
          </div>
        </div>

        {/* Total Combined Points */}
        <div className="bg-gradient-to-br from-purple-900 via-indigo-900 to-slate-900 text-white rounded-2xl p-4 shadow-md relative overflow-hidden">
          <div className="absolute right-0 top-0 translate-x-4 -translate-y-4 w-28 h-28 bg-white/5 rounded-full blur-xl pointer-events-none" />
          <div className="flex items-center justify-between text-purple-200 text-xs font-medium">
            <span>TOTAL COMBINED POOL</span>
            <span className="p-1.5 rounded-lg bg-white/10 text-purple-200">💎</span>
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-extrabold text-white tracking-tight">
              {summary.totalCombinedPoints.toFixed(2)}
            </span>
            <span className="text-xs font-semibold text-purple-300">pts</span>
          </div>
          <div className="mt-2 text-[11px] text-purple-200/80">
            {summary.totalCombinedEntries} total verified milestones
          </div>
        </div>

        {/* Active Contributors */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800/80 rounded-2xl p-4 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-medium">
            <span>ACTIVE CONTRIBUTORS</span>
            <span className="p-1.5 rounded-lg bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400">👥</span>
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-extrabold text-slate-900 dark:text-white tracking-tight">
              {summary.members.filter((m) => m.combinedPoints > 0).length}
            </span>
            <span className="text-xs font-medium text-slate-500">/ {summary.members.length} members</span>
          </div>
          <div className="mt-2 text-[11px] text-emerald-600 dark:text-emerald-400 font-medium flex items-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5" /> 100% Deterministic Math
          </div>
        </div>
      </div>

      {/* 2. Visual Equity Proportional Bar Gauge */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800/80 rounded-2xl p-4 shadow-xs">
        <div className="flex items-center justify-between mb-3">
          <div className="text-xs font-bold text-slate-900 dark:text-white tracking-tight flex items-center gap-2">
            <Award className="w-4 h-4 text-purple-600 dark:text-purple-400" />
            <span>SHAREHOLDER PROFIT SHARE DISTRIBUTION</span>
          </div>
          <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">
            Based on {summary.totalCombinedPoints.toFixed(2)} Total Points
          </span>
        </div>

        {/* Stacked Proportional Bar */}
        <div className="h-4 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden flex shadow-inner">
          {summary.members
            .filter((m) => m.combinedShare > 0)
            .map((m, idx) => (
              <div
                key={m.name}
                style={{ width: `${Math.max(m.combinedShare, 0.5)}%` }}
                className={`${memberColors[idx % memberColors.length]} transition-all relative group`}
                title={`${m.name}: ${m.combinedShare.toFixed(1)}% (${m.combinedPoints.toFixed(2)} pts)`}
              />
            ))}
        </div>

        {/* Color Legend */}
        <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1.5 text-xs">
          {summary.members
            .filter((m) => m.combinedShare > 0)
            .map((m, idx) => (
              <div key={m.name} className="flex items-center gap-1.5">
                <span className={`w-2.5 h-2.5 rounded-full ${memberColors[idx % memberColors.length]}`} />
                <span className="font-medium text-slate-700 dark:text-slate-300">{m.name}</span>
                <span className="font-bold text-slate-900 dark:text-white">{m.combinedShare.toFixed(1)}%</span>
              </div>
            ))}
        </div>
      </div>

      {/* 3. The 3 Comparative Tables */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Project Contributions Table */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800/80 rounded-2xl p-4 shadow-xs flex flex-col">
          <div className="flex items-center justify-between pb-3 border-b border-slate-200/60 dark:border-slate-800/60 mb-2">
            <h3 className="text-xs font-bold text-slate-900 dark:text-white tracking-tight flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-blue-500" />
              PROJECT CONTRIBUTIONS
            </h3>
            <span className="text-[11px] font-semibold text-slate-500">
              {summary.totalProjectPoints.toFixed(2)} pts
            </span>
          </div>

          <div className="overflow-x-auto grow">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="text-slate-500 dark:text-slate-400 font-medium border-b border-slate-100 dark:border-slate-800">
                  <th className="py-2">Member</th>
                  <th className="py-2 text-center">Entries</th>
                  <th className="py-2 text-right">Points</th>
                  <th className="py-2 text-right">% Share</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
                {summary.members.map((m) => (
                  <tr key={m.name} className="hover:bg-slate-50/60 dark:hover:bg-slate-800/30">
                    <td className="py-2 font-medium text-slate-800 dark:text-slate-200">{m.name}</td>
                    <td className="py-2 text-center text-slate-500">{m.projectEntries}</td>
                    <td className="py-2 text-right font-semibold text-slate-900 dark:text-white">{m.projectPoints.toFixed(2)}</td>
                    <td className="py-2 text-right font-bold text-blue-600 dark:text-blue-400">{m.projectShare.toFixed(1)}%</td>
                  </tr>
                ))}
              </tbody>
              <tfoot>
                <tr className="border-t-2 border-slate-200 dark:border-slate-700 font-bold text-slate-900 dark:text-white">
                  <td className="py-2.5">Total</td>
                  <td className="py-2.5 text-center">{summary.totalProjectEntries}</td>
                  <td className="py-2.5 text-right">{summary.totalProjectPoints.toFixed(2)}</td>
                  <td className="py-2.5 text-right text-blue-600 dark:text-blue-400">100.0%</td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>

        {/* Company Contributions Table */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800/80 rounded-2xl p-4 shadow-xs flex flex-col">
          <div className="flex items-center justify-between pb-3 border-b border-slate-200/60 dark:border-slate-800/60 mb-2">
            <h3 className="text-xs font-bold text-slate-900 dark:text-white tracking-tight flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-purple-500" />
              COMPANY CONTRIBUTIONS
            </h3>
            <span className="text-[11px] font-semibold text-slate-500">
              {summary.totalCompanyPoints.toFixed(2)} pts
            </span>
          </div>

          <div className="overflow-x-auto grow">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="text-slate-500 dark:text-slate-400 font-medium border-b border-slate-100 dark:border-slate-800">
                  <th className="py-2">Member</th>
                  <th className="py-2 text-center">Entries</th>
                  <th className="py-2 text-right">Points</th>
                  <th className="py-2 text-right">% Share</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
                {summary.members.map((m) => (
                  <tr key={m.name} className="hover:bg-slate-50/60 dark:hover:bg-slate-800/30">
                    <td className="py-2 font-medium text-slate-800 dark:text-slate-200">{m.name}</td>
                    <td className="py-2 text-center text-slate-500">{m.companyEntries}</td>
                    <td className="py-2 text-right font-semibold text-slate-900 dark:text-white">{m.companyPoints.toFixed(2)}</td>
                    <td className="py-2 text-right font-bold text-purple-600 dark:text-purple-400">{m.companyShare.toFixed(1)}%</td>
                  </tr>
                ))}
              </tbody>
              <tfoot>
                <tr className="border-t-2 border-slate-200 dark:border-slate-700 font-bold text-slate-900 dark:text-white">
                  <td className="py-2.5">Total</td>
                  <td className="py-2.5 text-center">{summary.totalCompanyEntries}</td>
                  <td className="py-2.5 text-right">{summary.totalCompanyPoints.toFixed(2)}</td>
                  <td className="py-2.5 text-right text-purple-600 dark:text-purple-400">100.0%</td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>

        {/* Overall Combined (Equity & Profit Share) Table */}
        <div className="bg-white dark:bg-slate-900 border-2 border-purple-200 dark:border-purple-900/60 rounded-2xl p-4 shadow-sm flex flex-col">
          <div className="flex items-center justify-between pb-3 border-b border-slate-200/60 dark:border-slate-800/60 mb-2">
            <h3 className="text-xs font-bold text-purple-900 dark:text-purple-300 tracking-tight flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              OVERALL COMBINED (PROFIT & EQUITY SHARE)
            </h3>
            <span className="text-[11px] font-extrabold text-purple-700 dark:text-purple-400">
              {summary.totalCombinedPoints.toFixed(2)} pts
            </span>
          </div>

          <div className="overflow-x-auto grow">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="text-slate-500 dark:text-slate-400 font-medium border-b border-slate-100 dark:border-slate-800">
                  <th className="py-2">Member</th>
                  <th className="py-2 text-right">Proj Pts</th>
                  <th className="py-2 text-right">Comp Pts</th>
                  <th className="py-2 text-right">Total Pts</th>
                  <th className="py-2 text-right font-bold text-purple-700 dark:text-purple-300">% Share</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
                {summary.members.map((m) => (
                  <tr key={m.name} className="hover:bg-purple-50/40 dark:hover:bg-purple-950/20">
                    <td className="py-2 font-bold text-slate-900 dark:text-white">{m.name}</td>
                    <td className="py-2 text-right text-slate-600 dark:text-slate-400">{m.projectPoints.toFixed(2)}</td>
                    <td className="py-2 text-right text-slate-600 dark:text-slate-400">{m.companyPoints.toFixed(2)}</td>
                    <td className="py-2 text-right font-bold text-slate-900 dark:text-white">{m.combinedPoints.toFixed(2)}</td>
                    <td className="py-2 text-right font-black text-purple-700 dark:text-purple-400">{m.combinedShare.toFixed(1)}%</td>
                  </tr>
                ))}
              </tbody>
              <tfoot>
                <tr className="border-t-2 border-purple-200 dark:border-purple-800 font-bold text-slate-900 dark:text-white bg-purple-50/30 dark:bg-purple-950/20">
                  <td className="py-2.5">Total</td>
                  <td className="py-2.5 text-right">{summary.totalProjectPoints.toFixed(2)}</td>
                  <td className="py-2.5 text-right">{summary.totalCompanyPoints.toFixed(2)}</td>
                  <td className="py-2.5 text-right">{summary.totalCombinedPoints.toFixed(2)}</td>
                  <td className="py-2.5 text-right font-black text-purple-700 dark:text-purple-400">100.0%</td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>
      </div>

      {/* 4. Interactive Profit Pool Payout Simulator */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-purple-950 text-white rounded-2xl p-5 shadow-md">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 pb-4 border-b border-white/10">
          <div>
            <div className="flex items-center gap-2">
              <Calculator className="w-5 h-5 text-emerald-400" />
              <h4 className="text-sm font-bold text-white tracking-tight">
                Live Shareholder Dividend & Profit Payout Simulator
              </h4>
            </div>
            <p className="text-xs text-purple-200/80 mt-1">
              Adjust the distributable profit pool to simulate exact monetary dividend payout per shareholder
            </p>
          </div>

          <div className="flex items-center gap-3">
            <label className="text-xs font-semibold text-purple-200">Profit Pool (₹):</label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 font-bold text-xs">₹</span>
              <input
                type="number"
                step="50000"
                value={profitPool}
                onChange={(e) => setProfitPool(Math.max(0, parseFloat(e.target.value) || 0))}
                className="pl-7 pr-3 py-1.5 rounded-xl bg-white/10 border border-white/20 text-white text-xs font-bold w-36 focus:outline-hidden focus:ring-2 focus:ring-purple-400"
              />
            </div>
          </div>
        </div>

        {/* Payout Grid */}
        <div className="mt-4 grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3">
          {summary.members.map((m) => (
            <div key={m.name} className="p-2.5 rounded-xl bg-white/5 border border-white/10 text-center">
              <div className="text-[11px] font-medium text-slate-300 truncate">{m.name}</div>
              <div className="text-xs font-bold text-purple-300 mt-0.5">{m.combinedShare.toFixed(1)}%</div>
              <div className="text-xs font-extrabold text-emerald-400 mt-1">
                ₹{Math.round(m.payout).toLocaleString("en-IN")}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

