import React, { useState, useMemo } from "react";
import { 
  Filter, 
  Download, 
  RotateCcw, 
  Eye, 
  X, 
  Calendar, 
  User, 
  Building, 
  Tag, 
  CheckCircle2, 
  Clock,
  FileSpreadsheet,
  Layers
} from "lucide-react";

export default function ContributionReportsView({ contributions = [], categories = [] }) {
  // Filter States
  const [datePreset, setDatePreset] = useState("all");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [selectedMember, setSelectedMember] = useState("all");
  const [selectedScope, setSelectedScope] = useState("all");
  const [selectedProject, setSelectedProject] = useState("all");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [selectedStatus, setSelectedStatus] = useState("all");
  const [selectedItemForView, setSelectedItemForView] = useState(null);

  // Dynamic distinct filter options extracted from dataset
  const filterOptions = useMemo(() => {
    const members = new Set();
    const projects = new Set();

    contributions.forEach((c) => {
      const name = c.user?.first_name || c.user?.username;
      if (name) members.add(name);
      if (c.project_name) projects.add(c.project_name);
    });

    return {
      members: Array.from(members),
      projects: Array.from(projects),
    };
  }, [contributions]);

  // Apply filters
  const filteredItems = useMemo(() => {
    return contributions.filter((c) => {
      // 1. Member
      if (selectedMember !== "all") {
        const name = c.user?.first_name || c.user?.username;
        if (name !== selectedMember) return false;
      }

      // 2. Scope
      if (selectedScope !== "all") {
        if (c.scope !== selectedScope) return false;
      }

      // 3. Project
      if (selectedProject !== "all") {
        if (c.project_name !== selectedProject) return false;
      }

      // 4. Category
      if (selectedCategory !== "all") {
        const catName = c.primary_category?.name || c.category_name;
        if (catName !== selectedCategory) return false;
      }

      // 5. Status
      if (selectedStatus !== "all") {
        if (c.delivery_status !== selectedStatus) return false;
      }

      // 6. Date Range
      if (startDate && c.date < startDate) return false;
      if (endDate && c.date > endDate) return false;

      return true;
    });
  }, [contributions, selectedMember, selectedScope, selectedProject, selectedCategory, selectedStatus, startDate, endDate]);

  // Aggregate Metrics based on filtered records
  const aggregates = useMemo(() => {
    const totalEntries = filteredItems.length;
    let totalPoints = 0;
    let totalFactorSum = 0;

    filteredItems.forEach((it) => {
      totalPoints += parseFloat(it.final_points) || 0;
      totalFactorSum += parseFloat(it.factor_percentage) || 100;
    });

    const avgFactor = totalEntries > 0 ? (totalFactorSum / totalEntries) : 0;

    return {
      totalEntries,
      totalPoints: totalPoints.toFixed(2),
      avgFactor: avgFactor.toFixed(1),
    };
  }, [filteredItems]);

  // Reset Filters
  const handleReset = () => {
    setDatePreset("all");
    setStartDate("");
    setEndDate("");
    setSelectedMember("all");
    setSelectedScope("all");
    setSelectedProject("all");
    setSelectedCategory("all");
    setSelectedStatus("all");
  };

  // Export filtered data to CSV
  const handleExportCSV = () => {
    if (filteredItems.length === 0) return;

    const headers = [
      "Date",
      "Member",
      "Activity",
      "Project",
      "Scope",
      "Category",
      "Worked Days",
      "Base Points",
      "Effort (20%)",
      "Skill (15%)",
      "Deliverable (25%)",
      "Quality (20%)",
      "Evidence (10%)",
      "Outcome (10%)",
      "Factor %",
      "Final Points",
      "Status",
    ];

    const rows = filteredItems.map((c) => [
      `"${c.date || ""}"`,
      `"${c.user?.first_name || c.user?.username || ""}"`,
      `"${(c.activity || "").replace(/"/g, '""')}"`,
      `"${c.project_name || ""}"`,
      `"${c.scope || ""}"`,
      `"${c.primary_category?.name || ""}"`,
      c.worked_days || 1,
      c.base_points || 10,
      c.factor_effort ? "TRUE" : "FALSE",
      c.factor_complexity ? "TRUE" : "FALSE",
      c.factor_deliverable ? "TRUE" : "FALSE",
      c.factor_quality ? "TRUE" : "FALSE",
      c.factor_evidence ? "TRUE" : "FALSE",
      c.factor_outcome ? "TRUE" : "FALSE",
      `${c.factor_percentage}%`,
      c.final_points,
      c.delivery_status || "completed",
    ]);

    const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map((e) => e.join(","))].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `work_contributions_report_${new Date().toISOString().split("T")[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6">
      {/* 1. Multi-Dimensional Filter Bar Card */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800/80 rounded-2xl p-5 shadow-xs space-y-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-3 border-b border-slate-100 dark:border-slate-800">
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-purple-600 dark:text-purple-400" />
            <h3 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider">
              Contribution Report Filters
            </h3>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={handleReset}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              Reset Filters
            </button>

            <button
              type="button"
              onClick={handleExportCSV}
              className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-bold text-white bg-slate-900 hover:bg-slate-800 dark:bg-purple-600 dark:hover:bg-purple-700 shadow-xs transition-all cursor-pointer"
            >
              <Download className="w-3.5 h-3.5" />
              Export CSV
            </button>
          </div>
        </div>

        {/* Filter Controls Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-3">
          {/* Member */}
          <div>
            <label className="text-[11px] font-semibold text-slate-500 block mb-1">Contributed Person</label>
            <select
              value={selectedMember}
              onChange={(e) => setSelectedMember(e.target.value)}
              className="w-full text-xs font-medium p-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-hidden"
            >
              <option value="all">All Members</option>
              {filterOptions.members.map((m) => (
                <option key={m} value={m}>{m}</option>
              ))}
            </select>
          </div>

          {/* Scope */}
          <div>
            <label className="text-[11px] font-semibold text-slate-500 block mb-1">Contribution Scope</label>
            <select
              value={selectedScope}
              onChange={(e) => setSelectedScope(e.target.value)}
              className="w-full text-xs font-medium p-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-hidden"
            >
              <option value="all">All Scopes</option>
              <option value="Company Contribution">Company Contribution</option>
              <option value="Project Contribution">Project Contribution</option>
            </select>
          </div>

          {/* Project */}
          <div>
            <label className="text-[11px] font-semibold text-slate-500 block mb-1">Project / Client</label>
            <select
              value={selectedProject}
              onChange={(e) => setSelectedProject(e.target.value)}
              className="w-full text-xs font-medium p-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-hidden"
            >
              <option value="all">All Projects</option>
              {filterOptions.projects.map((p) => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>
          </div>

          {/* Category */}
          <div>
            <label className="text-[11px] font-semibold text-slate-500 block mb-1">Category</label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full text-xs font-medium p-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-hidden"
            >
              <option value="all">All Categories</option>
              {categories.map((c) => (
                <option key={c.id || c.name} value={c.name}>{c.name}</option>
              ))}
            </select>
          </div>

          {/* Status */}
          <div>
            <label className="text-[11px] font-semibold text-slate-500 block mb-1">Status</label>
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="w-full text-xs font-medium p-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-hidden"
            >
              <option value="all">All Statuses</option>
              <option value="completed">Completed</option>
              <option value="in_progress">In Progress</option>
              <option value="stalled">Stalled</option>
              <option value="on_hold">On Hold</option>
            </select>
          </div>

          {/* Date Presets */}
          <div>
            <label className="text-[11px] font-semibold text-slate-500 block mb-1">Date Range</label>
            <div className="flex items-center gap-1.5">
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                placeholder="From"
                className="w-1/2 text-[11px] p-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-hidden"
              />
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                placeholder="To"
                className="w-1/2 text-[11px] p-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-hidden"
              />
            </div>
          </div>
        </div>
      </div>

      {/* 2. Dynamic Aggregated Summary Strip */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800/80 rounded-2xl p-4 shadow-xs">
          <div className="text-slate-500 text-xs font-medium">MATCHING RECORDS</div>
          <div className="mt-1 text-2xl font-extrabold text-slate-900 dark:text-white">
            {aggregates.totalEntries} Activities
          </div>
        </div>

        <div className="bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800/80 rounded-2xl p-4 shadow-xs">
          <div className="text-slate-500 text-xs font-medium">TOTAL FILTERED POINTS</div>
          <div className="mt-1 text-2xl font-extrabold text-purple-600 dark:text-purple-400">
            {aggregates.totalPoints} pts
          </div>
        </div>

        <div className="bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800/80 rounded-2xl p-4 shadow-xs">
          <div className="text-slate-500 text-xs font-medium">AVG EXECUTION FACTOR</div>
          <div className="mt-1 text-2xl font-extrabold text-emerald-600 dark:text-emerald-400">
            {aggregates.avgFactor}%
          </div>
        </div>
      </div>

      {/* 3. Granular Data Table */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800/80 rounded-2xl p-4 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="text-slate-500 font-semibold border-b border-slate-100 dark:border-slate-800">
                <th className="py-2.5 px-3">Date</th>
                <th className="py-2.5 px-3">Member</th>
                <th className="py-2.5 px-3">Work — Original Activity</th>
                <th className="py-2.5 px-3">Project / Client</th>
                <th className="py-2.5 px-3">Category</th>
                <th className="py-2.5 px-2 text-center">Days</th>
                <th className="py-2.5 px-2 text-center">Base</th>
                <th className="py-2.5 px-2 text-center">Factor</th>
                <th className="py-2.5 px-3 text-right">Points</th>
                <th className="py-2.5 px-3 text-center">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
              {filteredItems.map((item, idx) => (
                <tr key={item.id || idx} className="hover:bg-slate-50/60 dark:hover:bg-slate-800/30 transition-colors">
                  <td className="py-3 px-3 whitespace-nowrap text-slate-500 font-medium">{item.date}</td>
                  <td className="py-3 px-3 whitespace-nowrap font-bold text-slate-900 dark:text-white">
                    {item.user?.first_name || item.user?.username || "Member"}
                  </td>
                  <td className="py-3 px-3 max-w-md">
                    <div className="text-slate-800 dark:text-slate-200 font-medium line-clamp-2 leading-relaxed">
                      {item.activity}
                    </div>
                  </td>
                  <td className="py-3 px-3 whitespace-nowrap text-slate-600 dark:text-slate-400">
                    <span className="font-semibold">{item.project_name}</span>
                    <div className="text-[10px] text-slate-400">{item.scope}</div>
                  </td>
                  <td className="py-3 px-3 whitespace-nowrap font-medium text-purple-700 dark:text-purple-300">
                    {item.primary_category?.name || item.category_name || "Development"}
                  </td>
                  <td className="py-3 px-2 text-center font-bold text-slate-700 dark:text-slate-300">
                    {item.worked_days}
                  </td>
                  <td className="py-3 px-2 text-center text-slate-500">
                    {item.base_points}
                  </td>
                  <td className="py-3 px-2 text-center">
                    <span className="font-bold text-purple-600 dark:text-purple-400">
                      {item.factor_percentage}%
                    </span>
                  </td>
                  <td className="py-3 px-3 text-right font-black text-slate-900 dark:text-white">
                    {parseFloat(item.final_points || 0).toFixed(2)}
                  </td>
                  <td className="py-3 px-3 text-center">
                    <button
                      type="button"
                      onClick={() => setSelectedItemForView(item)}
                      className="px-2.5 py-1 rounded-lg text-xs font-semibold text-purple-700 dark:text-purple-300 bg-purple-50 dark:bg-purple-950/60 hover:bg-purple-100 transition-colors"
                    >
                      View
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 4. Single Entry Detail Modal */}
      {selectedItemForView && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl max-w-xl w-full p-6 shadow-2xl relative animate-in fade-in zoom-in-95 duration-150">
            <button
              type="button"
              onClick={() => setSelectedItemForView(null)}
              className="absolute right-4 top-4 p-1.5 text-slate-400 hover:text-slate-700 dark:hover:text-white rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center gap-2 mb-4">
              <span className="text-[10px] font-bold uppercase px-2.5 py-1 rounded-full bg-purple-100 dark:bg-purple-950 text-purple-700 dark:text-purple-300">
                {selectedItemForView.scope}
              </span>
              <span className="text-xs text-slate-500 font-medium">
                {selectedItemForView.date}
              </span>
            </div>

            <h3 className="text-sm font-bold text-slate-900 dark:text-white leading-snug">
              {selectedItemForView.activity}
            </h3>

            {/* Metadata Grid */}
            <div className="mt-4 grid grid-cols-2 gap-3 text-xs bg-slate-50 dark:bg-slate-800/50 p-3 rounded-2xl border border-slate-100 dark:border-slate-800">
              <div>
                <span className="text-slate-400 block text-[11px]">Member:</span>
                <span className="font-bold text-slate-800 dark:text-slate-200">
                  {selectedItemForView.user?.first_name || selectedItemForView.user?.username}
                </span>
              </div>
              <div>
                <span className="text-slate-400 block text-[11px]">Project:</span>
                <span className="font-bold text-slate-800 dark:text-slate-200">
                  {selectedItemForView.project_name}
                </span>
              </div>
              <div>
                <span className="text-slate-400 block text-[11px]">Category:</span>
                <span className="font-bold text-purple-600 dark:text-purple-400">
                  {selectedItemForView.primary_category?.name || "Development"}
                </span>
              </div>
              <div>
                <span className="text-slate-400 block text-[11px]">Final Points:</span>
                <span className="font-black text-slate-900 dark:text-white text-sm">
                  {parseFloat(selectedItemForView.final_points).toFixed(2)} pts
                </span>
              </div>
            </div>

            {/* The 6 Factor Badges */}
            <div className="mt-4">
              <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-2">
                Evaluation Criteria Factors
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs">
                {[
                  { name: "Effort & Responsibility (20%)", val: selectedItemForView.factor_effort },
                  { name: "Complexity & Skill (15%)", val: selectedItemForView.factor_complexity },
                  { name: "Deliverable & Completion (25%)", val: selectedItemForView.factor_deliverable },
                  { name: "Quality & Reliability (20%)", val: selectedItemForView.factor_quality },
                  { name: "Evidence & Ownership (10%)", val: selectedItemForView.factor_evidence },
                  { name: "Outcome & Long-Term Value (10%)", val: selectedItemForView.factor_outcome },
                ].map((f) => (
                  <div
                    key={f.name}
                    className={`flex items-center gap-1.5 p-2 rounded-xl text-[11px] font-semibold border ${
                      f.val
                        ? "bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800"
                        : "bg-slate-50 dark:bg-slate-800/40 text-slate-400 border-slate-200 dark:border-slate-700 line-through"
                    }`}
                  >
                    <span>{f.val ? "✔" : "✖"}</span>
                    <span>{f.name}</span>
                  </div>
                ))}
              </div>
            </div>

            {selectedItemForView.ai_reasoning && (
              <div className="mt-4 p-3 bg-purple-50/60 dark:bg-purple-950/30 rounded-xl text-xs text-purple-800 dark:text-purple-300">
                <strong>AI Audit Note:</strong> {selectedItemForView.ai_reasoning}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

