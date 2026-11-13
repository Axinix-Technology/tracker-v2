import React, { useState } from 'react';
import { INDUSTRIES } from '../../api/data';
import { PageBanner } from '../../components/PageBanner';
import { ContentSection } from '../../components/ContentSection';
import { SearchFilterBar } from '../../components/SearchFilterBar';
import { IndustryCard } from '../../components/IndustryCard';
import { EmptyState } from '../../components/EmptyState';
import { CtaBanner } from '../../components/CtaBanner';

export default function IndustriesPage() {
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [search, setSearch] = useState('');

  const categories = ['All', ...new Set(INDUSTRIES.map(i => i.category))];

  const filteredIndustries = INDUSTRIES.filter(ind => {
    const matchesCat = selectedCategory === 'All' || ind.category === selectedCategory;
    const matchesSearch =
      !search.trim() ||
      ind.name.toLowerCase().includes(search.toLowerCase().trim()) ||
      ind.subtitle.toLowerCase().includes(search.toLowerCase().trim()) ||
      ind.features.some(f => f.toLowerCase().includes(search.toLowerCase().trim()));
    return matchesCat && matchesSearch;
  });

  return (
    <div className="w-full">
      <PageBanner
        title="Solutions Built Around Your Industry"
        subtitle="Every industry has unique operational constraints, inventory rules, and compliance standards. We deliver software tailored to how your business actually runs."
        breadcrumbs={[{ label: 'Industries' }]}
        badge="Industry Specialization"
      />

      <ContentSection>
        <SearchFilterBar
          search={search}
          onSearchChange={setSearch}
          searchPlaceholder="Search industries, challenges, or features..."
          categories={categories}
          selectedCategory={selectedCategory}
          onCategoryChange={setSelectedCategory}
          count={filteredIndustries.length}
          countLabel="industries"
        />

        {filteredIndustries.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 pt-6">
            {filteredIndustries.map(ind => (
              <IndustryCard key={ind.id} industry={ind} />
            ))}
          </div>
        ) : (
          <EmptyState
            title="No industries match the selected criteria"
            onReset={() => {
              setSelectedCategory('All');
              setSearch('');
            }}
          />
        )}
      </ContentSection>

      <CtaBanner
        badge="Custom Industry Modeling"
        title="Don't See Your Specific Industry Listed?"
        subtitle="We build specialized ERP modules, workflows, and database tables for proprietary and niche verticals."
        primaryAction={{ label: 'Discuss Your Custom Requirements', to: '/contact/create' }}
        secondaryAction={{ label: 'Explore Core Solutions', to: '/solutions' }}
      />
    </div>
  );
}
