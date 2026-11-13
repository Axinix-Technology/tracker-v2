import React, { useState, useEffect, useCallback } from "react";
import ContributionSubNav from "../../components/Contributions/ContributionSubNav";
import FollowUpTracker from "../../components/Contributions/FollowUpTracker";
import contributionService from "../../services/contributionService";
import ModernLoader from "../../components/Common/ModernLoader";
import SeoHead from "../../components/SeoHead";

export default function ContributionsFollowUpsPage() {
  const [contributions, setContributions] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await contributionService.getContributions();
      setContributions(res.data || []);
    } catch (err) {
      console.error("Failed to load contributions:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const openFollowUpsCount = contributions.filter(
    (c) => c.delivery_status === "in_progress" || c.delivery_status === "stalled" || !c.factor_deliverable
  ).length;

  return (
    <div className="p-4 sm:p-6 max-w-7xl mx-auto space-y-6">
      <SeoHead title="In-Progress Work Follow-Up Radar | WorkHub ERP" />
      <ContributionSubNav openFollowUpsCount={openFollowUpsCount} />

      {loading ? (
        <div className="py-20 flex justify-center">
          <ModernLoader />
        </div>
      ) : (
        <FollowUpTracker contributions={contributions} onRefetch={loadData} />
      )}
    </div>
  );
}

