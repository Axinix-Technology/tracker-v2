import React, { useState, useEffect, useCallback } from "react";
import ContributionSubNav from "../../components/Contributions/ContributionSubNav";
import ContributionReportsView from "../../components/Contributions/ContributionReportsView";
import contributionService from "../../services/contributionService";
import ModernLoader from "../../components/Common/ModernLoader";
import SeoHead from "../../components/SeoHead";

export default function ContributionsReportsPage() {
  const [contributions, setContributions] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [contribRes, catRes] = await Promise.all([
        contributionService.getContributions(),
        contributionService.getCategories(),
      ]);
      setContributions(contribRes.data || []);
      setCategories(catRes || []);
    } catch (err) {
      console.error("Failed to load reports data:", err);
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
      <SeoHead title="Work Contribution Reports & Audit Ledger | WorkHub ERP" />
      <ContributionSubNav openFollowUpsCount={openFollowUpsCount} />

      {loading ? (
        <div className="py-20 flex justify-center">
          <ModernLoader />
        </div>
      ) : (
        <ContributionReportsView contributions={contributions} categories={categories} />
      )}
    </div>
  );
}

