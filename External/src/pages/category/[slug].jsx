import React from 'react';
import { useParams } from 'react-router-dom';
import { PageBanner } from '../../components/PageBanner';
import { ContentSection } from '../../components/ContentSection';
import { CategoryShowcase } from '../../components/CategoryShowcase';
import { CtaBanner } from '../../components/CtaBanner';
import { CATEGORIES } from '../../api/data';

export default function CategoryDetailPage() {
  const { slug } = useParams();

  const currentCategory =
    CATEGORIES.find(c => c.slug === slug || c.id === slug) || CATEGORIES[0];

  return (
    <div className="w-full">
      <PageBanner
        title={currentCategory.name}
        subtitle={currentCategory.description}
        breadcrumbs={[
          { label: 'Products', to: '/products' },
          { label: 'Categories' },
          { label: currentCategory.name },
        ]}
        badge={currentCategory.badge || 'Product Category'}
      />

      <ContentSection>
        <CategoryShowcase activeCategorySlug={currentCategory.slug} />
      </ContentSection>

      <CtaBanner
        badge="Enterprise Procurement"
        title="Looking for Bulk Hardware Scanners or Multi-Tenant ERP?"
        subtitle="We support direct government GeM purchasing, corporate POs, and turnkey on-premise deployments."
        primaryAction={{ label: 'Contact Corporate Desk', to: '/contact?subject=Bulk%20Procurement' }}
        secondaryAction={{ label: 'Schedule Product Demo', to: '/contact?subject=Product%20Demo' }}
      />
    </div>
  );
}

