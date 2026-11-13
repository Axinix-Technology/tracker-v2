import React from 'react';
import { PageBanner } from '../../../components/PageBanner';
import { ContentSection } from '../../../components/ContentSection';
import { FaqAccordion } from '../../../components/FaqAccordion';
import { CtaBanner } from '../../../components/CtaBanner';

export default function FaqPage() {
  const allFaqs = [
    {
      question: 'What is the implementation timeline for AXINIX ERP?',
      answer:
        'Standard single-location rollouts take approximately 7–14 days. Multi-branch enterprises with custom integrations, hardware setups, and legacy data cleansing typically deploy within 3–5 weeks.',
    },
    {
      question: 'Can AXINIX software operate offline?',
      answer:
        'Yes. Our POS and local retail nodes feature an offline-first architecture with local SQLite/IndexedDB caching. Sales transactions, barcode scans, and receipt prints continue seamlessly during internet outages, syncing automatically once connectivity restores.',
    },
    {
      question: 'How do you safeguard client data privacy and compliance?',
      answer:
        'All network transmissions utilize TLS 1.3 encryption. Passwords and credentials are never stored in plain text. Every mutation is audited with unique correlation IDs in compliance with enterprise audit policies.',
    },
    {
      question: 'What hardware is compatible with AXINIX POS?',
      answer:
        'AXINIX POS integrates with standard USB/Bluetooth barcode scanners, ESC/POS thermal receipt printers, electronic weighing scales (via RS-232/USB serial interfaces), cash drawers, and customer-facing secondary displays.',
    },
    {
      question: 'Do you offer custom software development beyond off-the-shelf modules?',
      answer:
        'Yes. Our systems engineering team builds tailored database schemas, custom third-party API bridges, and proprietary business calculators designed specifically around your operational processes.',
    },
    {
      question: 'How do software license renewals and upgrades work?',
      answer:
        'Annual cloud subscriptions include automatic rolling minor version updates, regulatory tax and GST compliance patches, and 24/7 SLA infrastructure monitoring. Renewal invoices are generated 30 days prior to expiry in the Client Portal.',
    },
  ];

  return (
    <div className="w-full">
      <PageBanner
        title="Help Center & FAQs"
        subtitle="Find answers to common questions about deployment, hardware integrations, security standards, and customization."
        breadcrumbs={[
          { label: 'Help & Policies' },
          { label: 'Frequently Asked Questions' },
        ]}
        badge="Knowledge Base"
      />

      <ContentSection containerClassName="max-w-4xl">
        <FaqAccordion title="Common Enterprise Inquiries" items={allFaqs} />
      </ContentSection>

      <CtaBanner
        badge="Have a Question Not Answered Here?"
        title="Speak Directly With an AXINIX Systems Consultant"
        subtitle="Our engineering leads are available to review your technical requirements."
        primaryAction={{ label: 'Contact Support Desk', to: '/contact/create' }}
        secondaryAction={{ label: 'Schedule Product Demo', to: '/demo/create' }}
      />
    </div>
  );
}
