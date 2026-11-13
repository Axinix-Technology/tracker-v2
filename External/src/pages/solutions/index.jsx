import React, { useState } from 'react';
import { SOLUTIONS } from '../../api/data';
import { PageBanner } from '../../components/PageBanner';
import { ContentSection } from '../../components/ContentSection';
import { SearchFilterBar } from '../../components/SearchFilterBar';
import { SolutionCard } from '../../components/SolutionCard';
import { EmptyState } from '../../components/EmptyState';
import { CtaBanner } from '../../components/CtaBanner';

export default function SolutionsPage() {
  const [search, setSearch] = useState('');

  const filteredSolutions = SOLUTIONS.filter(s => {
    if (!search.trim()) return true;
    const q = search.toLowerCase().trim();
    return (
      s.title.toLowerCase().includes(q) ||
      s.subtitle.toLowerCase().includes(q) ||
      s.features.some(f => f.toLowerCase().includes(q))
    );
  });

  return (
    <div className="w-full">
      <PageBanner
        title="Everything Your Business Needs. All in One Place."
        subtitle="Intelligent enterprise software engineered to simplify multi-branch operations, eliminate manual reconciliation, and drive sustainable growth."
        breadcrumbs={[{ label: 'Solutions' }]}
        badge="Enterprise Suites"
      />

      <ContentSection>
        <SearchFilterBar
          search={search}
          onSearchChange={setSearch}
          searchPlaceholder="Search by solution name, feature, or keyword..."
          count={filteredSolutions.length}
          countLabel="enterprise solutions"
        />

        {filteredSolutions.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 pt-6">
            {filteredSolutions.map(sol => (
              <SolutionCard key={sol.id} solution={sol} showFeatures />
            ))}
          </div>
        ) : (
          <EmptyState
            title={`No enterprise solutions match "${search}"`}
            onReset={() => setSearch('')}
          />
        )}
      </ContentSection>

      <CtaBanner
        badge="Custom Architecture"
        title="Need a Custom Solution for Your Company?"
        subtitle="We configure and develop tailored business systems matching your exact operational rules."
        primaryAction={{ label: 'Schedule a Personalized Walkthrough', to: '/contact?subject=Solutions%20Walkthrough' }}
        secondaryAction={{ label: 'Request Corporate Quote', to: '/contact?subject=Corporate%20Quote' }}
      />
    </div>
  );
}
