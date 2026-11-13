import React from 'react';
import { PRODUCTS, CATEGORIES } from '../../api/data';
import { PageBanner } from '../../components/PageBanner';
import { ContentSection } from '../../components/ContentSection';
import { CategoryCard } from '../../components/CategoryCard';
import { ProductCard } from '../../components/ProductCard';
import { CtaBanner } from '../../components/CtaBanner';

export default function ProductsPage() {
  return (
    <div className="w-full">
      <PageBanner
        title="Enterprise Products, Hardware & Software Suites"
        subtitle="Turnkey production software, industrial retail POS hardware kits, and high-availability managed cloud infrastructure."
        breadcrumbs={[{ label: 'Products' }]}
        badge="Enterprise Commercial Catalog"
      />

      {/* 1. Categories Grid */}
      <ContentSection
        badge="Product Categories"
        title="Explore by Category"
        subtitle="Browse specialized divisions across enterprise software, retail hardware, and cloud hosting."
      >
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {CATEGORIES.map(cat => (
            <CategoryCard key={cat.id} category={cat} />
          ))}
        </div>
      </ContentSection>

      {/* 2. All Commercial Products & Packages */}
      <ContentSection
        bg="card"
        badge="Available Packages"
        title="All Products & Hardware Terminals"
        subtitle="Production-ready commercial licenses, thermal printing peripherals, and dedicated cloud nodes."
      >
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {PRODUCTS.map(p => (
            <ProductCard key={p.id} product={p} />
          ))}
        </div>
      </ContentSection>

      <CtaBanner
        badge="Enterprise White-Label Licensing"
        title="Explore Custom White-Label Licensing & On-Premise Source Escrow"
        subtitle="We offer private enterprise white-label solutions, source code escrow, and dedicated air-gapped on-premise installations."
        primaryAction={{ label: 'Inquire for Enterprise Licensing', to: '/contact?subject=Enterprise%20White-Label%20Licensing' }}
        secondaryAction={{ label: 'Contact Architecture Team', to: '/contact?subject=Architecture%20Consultation' }}
      />
    </div>
  );
}
