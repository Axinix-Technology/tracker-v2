import React from 'react';
import { PageBanner } from '../../../components/PageBanner';
import { ContentSection } from '../../../components/ContentSection';
import { PolicyContent } from '../../../components/PolicyContent';

export default function TermsPage() {
  const sections = [
    {
      heading: 'Software Licensing & Authorized Use',
      content:
        'AXINIX grants the subscribing client organization a non-exclusive, non-transferable, revocable enterprise license to access and operate our software suites according to the contracted user seat count and branch limits.',
      bullets: [
        'User Seat Governance: Accounts must be assigned to individual authorized personnel and cannot be shared across simultaneous shifts.',
        'Reverse Engineering Prohibition: Clients may not decompile, disassemble, or derive source code from compiled production binaries without explicit white-label escrow agreements.',
        'High-Availability Cloud SLA: AXINIX guarantees 99.9% monthly service availability for managed cloud hosting tiers.',
      ],
    },
    {
      heading: 'Hardware Equipment Warranty & POS Terminals',
      content:
        'All physical retail billing terminals, thermal receipt printers, and barcode scanners supplied by AXINIX include a comprehensive hardware replacement warranty covering manufacturer defects.',
      bullets: [
        '2-Year Comprehensive Hardware Warranty on AXINIX Dual-Screen Touch Terminals.',
        '1-Year Instant Replacement on Omnidirectional 2D Barcode Scanners.',
        'Physical damages resulting from water immersion, power surges without surge protectors, or physical impact are excluded from warranty.',
      ],
    },
    {
      heading: 'Payment Terms, Invoicing & GST Compliance',
      content:
        'Subscription fees and hardware equipment invoices are payable in Indian Rupees (INR) or agreed foreign currency via Bank Wire, RTGS/NEFT, UPI, or corporate card. All charges are exclusive of statutory GST (18%) which is itemized for full B2B input tax credit.',
    },
    {
      heading: 'Limitation of Liability & Indemnification',
      content:
        'AXINIX TECHNOLOGIES shall not be liable for indirect, incidental, or consequential damages resulting from downtime outside our direct hosting control. Our total aggregate liability under any service contract shall not exceed the fees paid by the client in the twelve (12) months preceding the incident.',
    },
  ];

  return (
    <div className="w-full">
      <PageBanner
        title="Terms of Service & Master Services Agreement"
        subtitle="Contractual obligations, software licensing parameters, SLA availability commitments, and commercial governance."
        breadcrumbs={[
          { label: 'Help & Policies' },
          { label: 'Terms of Service' },
        ]}
        badge="Master Agreement"
      />

      <ContentSection>
        <PolicyContent
          title="Enterprise Master Services Agreement (MSA)"
          lastUpdated="October 2026"
          badge="Commercial Governance"
          summary="These Terms govern the procurement, subscription access, technical support, and hardware purchase across all AXINIX platforms and commercial offerings."
          sections={sections}
        />
      </ContentSection>
    </div>
  );
}
