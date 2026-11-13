import React, { useState } from 'react';
import { SERVICES } from '../../api/data';
import { PageBanner } from '../../components/PageBanner';
import { ContentSection } from '../../components/ContentSection';
import { SearchFilterBar } from '../../components/SearchFilterBar';
import { ServiceCard } from '../../components/ServiceCard';
import { EmptyState } from '../../components/EmptyState';
import { CtaBanner } from '../../components/CtaBanner';

export default function ServicesPage() {
  const [search, setSearch] = useState('');

  const filteredServices = SERVICES.filter(s => {
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
        title="From Digital Presence to Digital Growth"
        subtitle="Full-spectrum digital engineering and strategic marketing solutions built to deliver measurable revenue impact and brand distinction."
        breadcrumbs={[{ label: 'Services' }]}
        badge="Digital Capabilities"
      />

      <ContentSection>
        <SearchFilterBar
          search={search}
          onSearchChange={setSearch}
          searchPlaceholder="Search services or capabilities..."
          count={filteredServices.length}
          countLabel="capabilities"
        />

        {filteredServices.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 pt-6">
            {filteredServices.map(srv => (
              <ServiceCard key={srv.id} service={srv} showFeatures />
            ))}
          </div>
        ) : (
          <EmptyState
            title={`No services match "${search}"`}
            onReset={() => setSearch('')}
          />
        )}
      </ContentSection>

      <CtaBanner
        badge="Bespoke Engineering"
        title="Have a Special Project Requirement?"
        subtitle="Our engineering team develops bespoke software applications, API pipelines, and custom enterprise tools."
        primaryAction={{ label: 'Request a Technical Proposal', to: '/contact?subject=Technical%20Proposal' }}
        secondaryAction={{ label: 'Book Technical Consultation', to: '/contact?subject=Technical%20Consultation' }}
      />
    </div>
  );
}
