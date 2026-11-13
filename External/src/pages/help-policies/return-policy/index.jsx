import React from 'react';
import { PageBanner } from '../../../components/PageBanner';
import { ContentSection } from '../../../components/ContentSection';
import { PolicyContent } from '../../../components/PolicyContent';

export default function ReturnPolicyPage() {
  const sections = [
    {
      heading: '30-Day Enterprise Software Satisfaction Guarantee',
      content:
        'We stand firmly behind the performance of our software suites. If our standard cloud ERP, POS, CRM, or HRMS solution fails to fulfill verified technical specifications within the first 30 calendar days from subscription activation, you are eligible for a 100% refund of subscription software fees.',
      bullets: [
        'Applicable to all standard monthly and annual software subscription tiers.',
        'Custom bespoke development hours, on-site legacy data migration fees, and third-party SMS/WhatsApp API gateway costs are non-refundable.',
      ],
    },
    {
      heading: 'Hardware Equipment Return & Exchange Criteria',
      content:
        'Physical equipment including AXINIX POS terminals, thermal printers, and barcode scanners may be returned or exchanged within 14 days of confirmed carrier delivery.',
      bullets: [
        'Hardware must be in like-new cosmetic condition with original protective packaging, cables, power bricks, and documentation.',
        'Dead-on-Arrival (DOA) units receive instant expedited advance replacement with complimentary reverse logistics.',
        'Units returned for change-of-mind without technical defect may be subject to a nominal 10% repackaging and diagnostic fee.',
      ],
    },
    {
      heading: 'Return Merchandise Authorization (RMA) Process',
      content:
        'To initiate a return or exchange, submit an RMA request through our dedicated Client Portal or contact our logistics desk. An RMA number and pre-paid courier shipping label will be generated within 24 business hours.',
    },
  ];

  return (
    <div className="w-full">
      <PageBanner
        title="Return & Refund Policy"
        subtitle="Transparent return guidelines for hardware POS terminals, barcode scanners, and software subscription guarantees."
        breadcrumbs={[
          { label: 'Help & Policies' },
          { label: 'Return Policy' },
        ]}
        badge="Commercial Protection"
      />

      <ContentSection>
        <PolicyContent
          title="Hardware Return & Software Guarantee Policy"
          lastUpdated="October 2026"
          badge="30-Day Guarantee"
          summary="AXINIX guarantees enterprise-grade performance and clear, fair return and refund mechanisms for all commercial engagements."
          sections={sections}
        />
      </ContentSection>
    </div>
  );
}
