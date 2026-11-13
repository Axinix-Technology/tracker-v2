import React, { useState, useMemo } from "react";
import { 
  Clock, 
  AlertTriangle, 
  CheckCircle2, 
  MessageSquare, 
  Send, 
  PauseCircle, 
  ChevronRight,
  Filter,
  Sparkles
} from "lucide-react";
import contributionService from "../../services/contributionService";
import toast from "react-hot-toast";

export default function FollowUpTracker({ contributions = [], onRefetch = () => {} }) {
  const [selectedMember, setSelectedMember] = useState("all");
  const [selectedStatus, setSelectedStatus] = useState("all");
  const [isUpdating, setIsUpdating] = useState(false);

  // Filter only in-progress, stalled, or on-hold tasks
  const openItems = useMemo(() => {
    return contributions.filter((c) => {
      const status = (c.delivery_status || "").toLowerCase();
      const isUnfinished = status === "in_progress" || status === "stalled" || status === "on_hold" || !c.factor_deliverable;
      if (!isUnfinished) return false;

      if (selectedMember !== "all") {
        const name = c.user?.first_name || c.user?.username || "";
        if (name !== selectedMember) return false;
      }

      if (selectedStatus !== "all") {
        if (status !== selectedStatus) return false;
      }

      return true;
    });
  }, [contributions, selectedMember, selectedStatus]);

  // Aggregate metrics
  const metrics = useMemo(() => {
    const totalOpen = openItems.length;
    let stalledCount = 0;
    let pointsInLimbo = 0;

    openItems.forEach((item) => {
      // Calculate days open based on item date vs now
      const itemDate = new Date(item.date || item.created_at);
      const diffDays = Math.max(0, Math.floor((new Date() - itemDate) / (1000 * 60 * 60 * 24)));
      if (diffDays >= 2 || item.delivery_status === "stalled") {
        stalledCount += 1;
      }
      pointsInLimbo += parseFloat(item.final_points) || 0;
    });

    return { totalOpen, stalledCount, pointsInLimbo };
  }, [openItems]);

  // Unique members for filter
  const memberList = useMemo(() => {
    const set = new Set();
    contributions.forEach((c) => {
      const name = c.user?.first_name || c.user?.username;
      if (name) set.add(name);
    });
    return Array.from(set);
  }, [contributions]);

  // Action: Mark completed and unlock remaining 25% deliverable points
  const handleMarkCompleted = async (item) => {
    setIsUpdating(true);
    try {
      await contributionService.updateContribution(item.id, {
        factor_deliverable: true,
        delivery_status: "completed",
        ai_reasoning: "Follow-up completed and milestone delivered.",
      });
      toast.success(`Completed! Remaining 25% Deliverable points unlocked for ${item.user?.first_name || "member"}.`);
      onRefetch();
    } catch {
      toast.error("Failed to update item.");
    } finally {
      setIsUpdating(false);
    }
  };

  // Action: Send Ping notification
  const handlePing = (item) => {
    const name = item.user?.first_name || "team member";
    toast.success(`Follow-up reminder sent to ${name}: "Has the activity '${item.activity.slice(0, 30)}...' been completed?"`, {
      icon: "🔔",
      duration: 4000,
    });
  };

  return (
    <div className="space-y-6">
      {/* 1. Header & Telemetry Strip */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800/80 rounded-2xl p-4 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
            <span>OPEN IN-PROGRESS TASKS</span>
            <Clock className="w-4 h-4 text-purple-600 dark:text-purple-400" />
          </div>
          <div className="mt-2 text-2xl font-extrabold text-slate-900 dark:text-white">
            {metrics.totalOpen} Items
          </div>
          <div className="mt-1 text-[11px] text-slate-500">
            Awaiting final completion verification
          </div>
        </div>

        <div className="bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800/80 rounded-2xl p-4 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
            <span>STALLED (&gt; 48 HOURS)</span>
            <AlertTriangle className="w-4 h-4 text-amber-500" />
          </div>
          <div className="mt-2 text-2xl font-extrabold text-amber-600 dark:text-amber-400">
            {metrics.stalledCount} Items
          </div>
          <div className="mt-1 text-[11px] text-amber-600/80">
            Require follow-up ping or resolution
          </div>
        </div>

        <div className="bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800/80 rounded-2xl p-4 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
            <span>POINTS IN LIMBO</span>
            <Sparkles className="w-4 h-4 text-blue-500" />
          </div>
          <div className="mt-2 text-2xl font-extrabold text-slate-900 dark:text-white">
            {metrics.pointsInLimbo.toFixed(2)} pts
          </div>
          <div className="mt-1 text-[11px] text-slate-500">
            25% completion bonus pending delivery
          </div>
        </div>
      </div>

      {/* 2. Filter Bar */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800/80 rounded-2xl p-4 shadow-xs flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-1.5 text-xs text-slate-500 font-medium">
            <Filter className="w-3.5 h-3.5" />
            <span>Filters:</span>
          </div>

          <select
            value={selectedMember}
            onChange={(e) => setSelectedMember(e.target.value)}
            className="text-xs font-medium px-2.5 py-1.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-hidden"
          >
            <option value="all">All Team Members</option>
            {memberList.map((m) => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>

          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="text-xs font-medium px-2.5 py-1.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-hidden"
          >
            <option value="all">All Delivery Statuses</option>
            <option value="in_progress">In Progress</option>
            <option value="stalled">Stalled (&gt; 2 Days)</option>
            <option value="on_hold">On Hold</option>
          </select>
        </div>

        <div className="text-xs font-semibold text-slate-500">
          Showing {openItems.length} uncompleted records
        </div>
      </div>

      {/* 3. Follow-Up Data Table */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800/80 rounded-2xl p-4 shadow-xs overflow-hidden">
        {openItems.length === 0 ? (
          <div className="p-8 text-center">
            <CheckCircle2 className="w-8 h-8 text-emerald-500 mx-auto mb-2" />
            <h4 className="text-sm font-bold text-slate-900 dark:text-white">Zero Stalled Tasks!</h4>
            <p className="text-xs text-slate-500 mt-1">All logged contributions have completed milestones and deliverables.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="text-slate-500 font-medium border-b border-slate-100 dark:border-slate-800">
                  <th className="py-2.5 px-3">Member</th>
                  <th className="py-2.5 px-3">Logged Activity</th>
                  <th className="py-2.5 px-3">Project / Client</th>
                  <th className="py-2.5 px-3">Started</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3 text-right">Current Pts</th>
                  <th className="py-2.5 px-3 text-center">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
                {openItems.map((item) => {
                  const itemDate = new Date(item.date || item.created_at);
                  const diffDays = Math.max(0, Math.floor((new Date() - itemDate) / (1000 * 60 * 60 * 24)));
                  const isStalled = diffDays >= 2 || item.delivery_status === "stalled";

                  return (
                    <tr key={item.id} className="hover:bg-slate-50/60 dark:hover:bg-slate-800/30 transition-colors">
                      <td className="py-3 px-3 font-bold text-slate-900 dark:text-white whitespace-nowrap">
                        {item.user?.first_name || item.user?.username || "Member"}
                      </td>

                      <td className="py-3 px-3 max-w-sm">
                        <div className="text-slate-800 dark:text-slate-200 line-clamp-2 leading-relaxed font-medium">
                          {item.activity}
                        </div>
                        <div className="text-[10px] text-purple-600 dark:text-purple-400 mt-0.5 font-semibold">
                          Factor: {item.factor_percentage}% (Deliverable: FALSE)
                        </div>
                      </td>

                      <td className="py-3 px-3 whitespace-nowrap font-medium text-slate-600 dark:text-slate-400">
                        {item.project_name || "Axinix Technologies"}
                      </td>

                      <td className="py-3 px-3 whitespace-nowrap text-slate-500">
                        <div>{item.date}</div>
                        <div className={`text-[10px] font-bold ${isStalled ? "text-rose-500" : "text-slate-400"}`}>
                          {diffDays === 0 ? "Today" : `${diffDays} days ago`}
                        </div>
                      </td>

                      <td className="py-3 px-3 whitespace-nowrap">
                        <span
                          className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-full ${
                            isStalled
                              ? "bg-rose-50 dark:bg-rose-950/60 text-rose-600 dark:text-rose-400 border border-rose-200 dark:border-rose-800"
                              : item.delivery_status === "on_hold"
                              ? "bg-amber-50 dark:bg-amber-950/60 text-amber-600 dark:text-amber-400 border border-amber-200 dark:border-amber-800"
                              : "bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 border border-blue-200 dark:border-blue-800"
                          }`}
                        >
                          {isStalled ? "🔴 Stalled" : item.delivery_status}
                        </span>
                      </td>

                      <td className="py-3 px-3 whitespace-nowrap text-right font-bold text-slate-900 dark:text-white">
                        {parseFloat(item.final_points || 0).toFixed(2)} pts
                      </td>

                      <td className="py-3 px-3 whitespace-nowrap text-center">
                        <div className="flex items-center justify-center gap-1.5">
                          <button
                            type="button"
                            onClick={() => handlePing(item)}
                            className="p-1.5 rounded-lg text-slate-500 hover:text-purple-600 hover:bg-purple-50 dark:hover:bg-purple-950/40 transition-colors"
                            title="Send follow-up ping"
                          >
                            <MessageSquare className="w-3.5 h-3.5" />
                          </button>

                          <button
                            type="button"
                            onClick={() => handleMarkCompleted(item)}
                            disabled={isUpdating}
                            className="flex items-center gap-1 px-2.5 py-1 rounded-lg text-[11px] font-bold text-white bg-emerald-600 hover:bg-emerald-700 shadow-xs transition-all disabled:opacity-50"
                            title="Unlock remaining 25% Deliverable points"
                          >
                            <CheckCircle2 className="w-3 h-3" />
                            <span>Mark Done</span>
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

