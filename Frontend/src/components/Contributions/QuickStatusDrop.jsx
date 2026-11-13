import React, { useState } from "react";
import { 
  Sparkles, 
  Send, 
  Trash2, 
  CheckCircle2, 
  AlertCircle, 
  Plus, 
  Clock, 
  Calendar,
  Layers,
  ArrowRight,
  HelpCircle
} from "lucide-react";
import contributionService from "../../services/contributionService";
import toast from "react-hot-toast";

export default function QuickStatusDrop({ categories = [], onSubmitted = () => {} }) {
  const [rawText, setRawText] = useState("");
  const [targetDate, setTargetDate] = useState(() => new Date().toISOString().split("T")[0]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [draftItems, setDraftItems] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // The 6 Evaluation Factors and their exact weights
  const factorDefs = [
    { key: "factor_effort", name: "Effort", weight: 20, desc: "Genuine effort & consistency (20%)" },
    { key: "factor_complexity", name: "Skill", weight: 15, desc: "Technical difficulty & independence (15%)" },
    { key: "factor_deliverable", name: "Deliverable", weight: 25, desc: "Completed output / working milestone (25%)" },
    { key: "factor_quality", name: "Quality", weight: 20, desc: "Clean architecture & reliability (20%)" },
    { key: "factor_evidence", name: "Evidence", weight: 10, desc: "Verifiable PR/commits/records (10%)" },
    { key: "factor_outcome", name: "Outcome", weight: 10, desc: "Long-term reusability & company value (10%)" },
  ];

  // AI Extraction Trigger
  const handleAnalyze = async () => {
    if (!rawText.trim()) {
      toast.error("Please paste your work status text first!");
      return;
    }

    setIsAnalyzing(true);
    try {
      const res = await contributionService.aiParseText(rawText, targetDate);
      if (res.success && res.items?.length > 0) {
        setDraftItems(res.items);
        toast.success(`AI successfully extracted ${res.items.length} contribution activities!`);
      } else {
        toast.error("Could not extract discrete activities. Please check your text format.");
      }
    } catch (err) {
      toast.error(err.response?.data?.error || "AI parsing failed. Please try again.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Live Recalculate Points for a given item index
  const updateDraftItem = (index, field, value) => {
    setDraftItems((prev) => {
      const updated = [...prev];
      const item = { ...updated[index], [field]: value };

      // Recompute factor percentage
      let sum = 0;
      factorDefs.forEach((f) => {
        if (item[f.key]) sum += f.weight;
      });
      item.factor_percentage = sum;

      // Recompute final points: days * base * (sum / 100)
      const days = parseFloat(item.worked_days) || 1.0;
      const base = parseFloat(item.base_points) || 10.0;
      item.final_points = Math.round(days * base * (sum / 100) * 100) / 100;

      // Auto sync delivery status
      if (!item.factor_deliverable) {
        item.delivery_status = "in_progress";
      } else if (item.delivery_status === "in_progress") {
        item.delivery_status = "completed";
      }

      updated[index] = item;
      return updated;
    });
  };

  // Delete draft item
  const removeDraftItem = (index) => {
    setDraftItems((prev) => prev.filter((_, idx) => idx !== index));
  };

  // Submit all verified items to the Populate Engine
  const handleSubmitAll = async () => {
    if (draftItems.length === 0) return;

    setIsSubmitting(true);
    try {
      for (const item of draftItems) {
        // Resolve primary category ID if available
        const matchedCat = categories.find((c) => c.name.toLowerCase() === (item.category_name || "").toLowerCase());
        const payload = {
          activity: item.activity,
          project_name: item.project_name || "Axinix Technologies",
          scope: item.scope || "Company Contribution",
          primary_category_id: matchedCat?.id || null,
          worked_days: item.worked_days || 1.0,
          base_points: item.base_points || 10.0,
          factor_effort: !!item.factor_effort,
          factor_complexity: !!item.factor_complexity,
          factor_deliverable: !!item.factor_deliverable,
          factor_quality: !!item.factor_quality,
          factor_evidence: !!item.factor_evidence,
          factor_outcome: !!item.factor_outcome,
          delivery_status: item.delivery_status || "completed",
          date: targetDate,
          ai_reasoning: item.ai_reasoning || "",
        };
        await contributionService.createContribution(payload);
      }

      toast.success(`Successfully saved ${draftItems.length} activities to the Contribution Ledger!`);
      setDraftItems([]);
      setRawText("");
      onSubmitted();
    } catch (err) {
      toast.error(err.response?.data?.message || "Error submitting contributions.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* 1. Raw Text Drop Card */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800/80 rounded-2xl p-5 shadow-xs">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-3 border-b border-slate-100 dark:border-slate-800">
          <div>
            <h2 className="text-sm font-bold text-slate-900 dark:text-white tracking-tight flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-purple-600 dark:text-purple-400" />
              WhatsApp & Chat Quick Status Drop
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Paste your raw daily updates, bullet points, or forwarded chat messages below
            </p>
          </div>

          <div className="flex items-center gap-2">
            <label className="text-xs font-semibold text-slate-600 dark:text-slate-400">Target Date:</label>
            <input
              type="date"
              value={targetDate}
              onChange={(e) => setTargetDate(e.target.value)}
              className="px-2.5 py-1 text-xs rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white font-medium focus:outline-hidden focus:ring-2 focus:ring-purple-500"
            />
          </div>
        </div>

        {/* Text Area */}
        <div className="mt-4">
          <textarea
            rows={6}
            value={rawText}
            onChange={(e) => setRawText(e.target.value)}
            placeholder={`Example:
@all 
Today's Work Status

Axinix Technologies
1. Inspected all 5 core repositories to map architectures and modules.
2. Created and committed 15 central technical documentation files.
3. Audited, fixed, and documented Module 1 (HTTP Ingress & Export).

Tea Shop
1. Completed and committed the backend migration to Django integrated with axinix-core.`}
            className="w-full p-3.5 text-xs font-mono rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950/50 text-slate-800 dark:text-slate-200 focus:outline-hidden focus:ring-2 focus:ring-purple-500/80 transition-all leading-relaxed placeholder:text-slate-400"
          />
        </div>

        {/* Action Controls */}
        <div className="mt-3 flex items-center justify-between">
          <span className="text-[11px] text-slate-400">
            {rawText.length} characters entered
          </span>

          <div className="flex items-center gap-2">
            {rawText && (
              <button
                type="button"
                onClick={() => setRawText("")}
                className="px-3 py-1.5 text-xs text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 transition-colors"
              >
                Clear
              </button>
            )}

            <button
              type="button"
              onClick={handleAnalyze}
              disabled={isAnalyzing || !rawText.trim()}
              className="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold text-white bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 shadow-md shadow-purple-500/20 disabled:opacity-50 transition-all cursor-pointer"
            >
              <Sparkles className="w-3.5 h-3.5 animate-spin-slow" />
              {isAnalyzing ? "Analyzing Text with AI..." : "✨ Parse & Evaluate with AI"}
            </button>
          </div>
        </div>
      </div>

      {/* 2. Parsed Draft Cards & Calibration Review Queue */}
      {draftItems.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between bg-purple-50 dark:bg-purple-950/40 border border-purple-200/80 dark:border-purple-900/60 rounded-2xl p-4">
            <div>
              <h3 className="text-xs font-bold text-purple-900 dark:text-purple-300 tracking-tight flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                Parsed Draft Items ({draftItems.length} Activities Extracted)
              </h3>
              <p className="text-[11px] text-purple-700 dark:text-purple-400 mt-0.5">
                Review and toggle factor checkboxes below. Final points and delivery status update live.
              </p>
            </div>

            <button
              type="button"
              onClick={handleSubmitAll}
              disabled={isSubmitting}
              className="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-700 shadow-md shadow-emerald-500/20 disabled:opacity-50 transition-all cursor-pointer"
            >
              <CheckCircle2 className="w-3.5 h-3.5" />
              {isSubmitting ? "Submitting..." : `Submit All (${draftItems.length}) to Ledger`}
            </button>
          </div>

          {/* Cards List */}
          <div className="space-y-3">
            {draftItems.map((item, idx) => (
              <div
                key={idx}
                className="bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800/80 rounded-2xl p-4 shadow-xs hover:border-purple-300 dark:hover:border-purple-800 transition-all"
              >
                {/* Header: Project, Scope, Delete */}
                <div className="flex items-start justify-between gap-3">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400">
                      #{idx + 1}
                    </span>
                    <input
                      type="text"
                      value={item.project_name}
                      onChange={(e) => updateDraftItem(idx, "project_name", e.target.value)}
                      placeholder="Project / Client"
                      className="text-xs font-bold text-slate-900 dark:text-white bg-slate-50 dark:bg-slate-800/80 px-2.5 py-1 rounded-lg border border-slate-200 dark:border-slate-700 focus:outline-hidden focus:ring-1 focus:ring-purple-500"
                    />
                    <select
                      value={item.scope}
                      onChange={(e) => updateDraftItem(idx, "scope", e.target.value)}
                      className="text-xs font-semibold px-2.5 py-1 rounded-lg bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-purple-700 dark:text-purple-300 focus:outline-hidden"
                    >
                      <option value="Company Contribution">🏢 Company Contribution</option>
                      <option value="Project Contribution">📁 Project Contribution</option>
                    </select>

                    {/* Delivery Status Badge */}
                    <span
                      className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-full ${
                        item.delivery_status === "completed"
                          ? "bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800"
                          : "bg-amber-50 dark:bg-amber-950/60 text-amber-600 dark:text-amber-400 border border-amber-200 dark:border-amber-800"
                      }`}
                    >
                      {item.delivery_status}
                    </span>
                  </div>

                  <button
                    type="button"
                    onClick={() => removeDraftItem(idx)}
                    className="p-1.5 text-slate-400 hover:text-rose-600 rounded-lg hover:bg-rose-50 dark:hover:bg-rose-950/30 transition-colors"
                    title="Remove item"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>

                {/* Activity Description */}
                <div className="mt-2.5">
                  <textarea
                    rows={2}
                    value={item.activity}
                    onChange={(e) => updateDraftItem(idx, "activity", e.target.value)}
                    className="w-full text-xs text-slate-800 dark:text-slate-200 p-2 rounded-lg bg-slate-50/60 dark:bg-slate-950/40 border border-slate-200/80 dark:border-slate-800 focus:outline-hidden focus:ring-1 focus:ring-purple-500"
                  />
                </div>

                {/* Categories & Parameters */}
                <div className="mt-3 grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                  <div>
                    <label className="text-[11px] font-medium text-slate-500 block mb-1">Primary Category</label>
                    <select
                      value={item.category_name}
                      onChange={(e) => {
                        const cat = categories.find((c) => c.name === e.target.value);
                        updateDraftItem(idx, "category_name", e.target.value);
                        if (cat) updateDraftItem(idx, "base_points", cat.base_points);
                      }}
                      className="w-full p-1.5 rounded-lg bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs font-medium text-slate-900 dark:text-white"
                    >
                      {categories.map((c) => (
                        <option key={c.id || c.name} value={c.name}>
                          {c.name} ({c.base_points} pts)
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="text-[11px] font-medium text-slate-500 block mb-1">Worked Days</label>
                    <input
                      type="number"
                      step="0.5"
                      min="0.5"
                      value={item.worked_days}
                      onChange={(e) => updateDraftItem(idx, "worked_days", Math.max(0.1, parseFloat(e.target.value) || 1.0))}
                      className="w-full p-1.5 rounded-lg bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs font-bold text-slate-900 dark:text-white"
                    />
                  </div>

                  <div>
                    <label className="text-[11px] font-medium text-slate-500 block mb-1">Base Points per Day</label>
                    <input
                      type="number"
                      step="0.5"
                      value={item.base_points}
                      onChange={(e) => updateDraftItem(idx, "base_points", Math.max(1, parseFloat(e.target.value) || 10.0))}
                      className="w-full p-1.5 rounded-lg bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs font-bold text-slate-900 dark:text-white"
                    />
                  </div>
                </div>

                {/* 6 Evaluation Factors Checkbox Grid */}
                <div className="mt-3 pt-3 border-t border-slate-100 dark:border-slate-800">
                  <div className="text-[11px] font-bold text-slate-600 dark:text-slate-400 mb-2">
                    Evaluation Criteria (Total Weight: 100%)
                  </div>
                  <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
                    {factorDefs.map((f) => (
                      <label
                        key={f.key}
                        className={`flex items-center gap-1.5 p-2 rounded-lg border text-xs cursor-pointer transition-all ${
                          item[f.key]
                            ? "bg-purple-50/70 dark:bg-purple-950/40 border-purple-300 dark:border-purple-800 text-purple-900 dark:text-purple-200 font-semibold"
                            : "bg-slate-50 dark:bg-slate-800/40 border-slate-200 dark:border-slate-700 text-slate-400 line-through"
                        }`}
                        title={f.desc}
                      >
                        <input
                          type="checkbox"
                          checked={!!item[f.key]}
                          onChange={(e) => updateDraftItem(idx, f.key, e.target.checked)}
                          className="w-3.5 h-3.5 rounded-sm text-purple-600 focus:ring-purple-500"
                        />
                        <span>{f.name} ({f.weight}%)</span>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Footer: Live Point Summary */}
                <div className="mt-3 flex items-center justify-between text-xs pt-2">
                  <span className="text-[11px] text-slate-500 italic truncate max-w-md">
                    AI Note: {item.ai_reasoning || "Standard classification applied."}
                  </span>

                  <div className="flex items-center gap-3">
                    <span className="text-slate-500">
                      Factor: <strong className="text-purple-600 dark:text-purple-400">{item.factor_percentage}%</strong>
                    </span>
                    <span className="text-slate-500">
                      Points: <strong className="text-base text-slate-900 dark:text-white font-black">{item.final_points.toFixed(2)} pts</strong>
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

