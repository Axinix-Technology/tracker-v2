import React, { useState, useEffect, useCallback } from "react";
import ContributionSubNav from "../../components/Contributions/ContributionSubNav";
import QuickStatusDrop from "../../components/Contributions/QuickStatusDrop";
import contributionService from "../../services/contributionService";
import ModernLoader from "../../components/Common/ModernLoader";
import SeoHead from "../../components/SeoHead";
import { useNavigate } from "react-router-dom";

export default function ContributionsAddPage() {
  const navigate = useNavigate();
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadCategories = useCallback(async () => {
    setLoading(true);
    try {
      const cats = await contributionService.getCategories();
      setCategories(cats);
    } catch (err) {
      console.error("Failed to load categories:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadCategories();
  }, [loadCategories]);

  return (
    <div className="p-4 sm:p-6 max-w-7xl mx-auto space-y-6">
      <SeoHead title="Add Work Status & AI Parse | WorkHub ERP" />
      <ContributionSubNav />

      {loading ? (
        <div className="py-20 flex justify-center">
          <ModernLoader />
        </div>
      ) : (
        <QuickStatusDrop
          categories={categories}
          onSubmitted={() => navigate("/contributions/dashboard")}
        />
      )}
    </div>
  );
}

