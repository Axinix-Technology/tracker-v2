import React from 'react';
import { PageBanner } from '../../../components/PageBanner';
import { ContentSection } from '../../../components/ContentSection';
import { PolicyContent } from '../../../components/PolicyContent';

export default function ShippingPolicyPage() {
  const sections = [
    {
      heading: 'Dispatch Timelines & Order Processing',
      content:
        'All in-stock hardware POS terminals, barcode scanners, thermal roll packs, and accessories are dispatched within 24 hours of order confirmation and GST verification from our central logistics facility in Chennai, Tamil Nadu.',
      bullets: [
        'Orders placed before 2:00 PM IST on business days are processed and manifested on the same day.',
        'Custom pre-flashed POS terminals with preloaded tenant credentials undergo automated burn-in testing and dispatch within 48 hours.',
      ],
    },
    {
      heading: 'Complimentary Enterprise Freight Logistics',
      content:
        'AXINIX provides 100% complimentary surface and air freight for all corporate hardware orders across India via authorized tier-1 logistics partners (BlueDart Express, Delhivery Freight, DTDC Corporate).',
      bullets: [
        'Transit Times (Metro Cities): 2 to 3 business days with door delivery.',
        'Transit Times (Tier-2 & Tier-3 Cities): 3 to 5 business days.',
        'Tamper-evident packaging and high-impact multi-layer foam cushioning prevent transit damages.',
      ],
    },
    {
      heading: 'Live GPS Tracking & Transit Insurance',
      content:
        'Every hardware consignment is assigned a unique tracking number immediately visible in the AXINIX Client Portal at /delivery. All shipments are fully insured against transit loss, theft, or physical damage at zero additional cost to the client.',
    },
    {
      heading: 'Delivery Exceptions & Damaged Consignments',
      content:
        'In the unlikely event of visible outer carton damage upon carrier arrival, clients are instructed to note the condition on the carrier Proof of Delivery (POD) slip and notify our dispatch desk immediately for emergency unit advance replacement.',
    },
  ];

  return (
    <div className="w-full">
      <PageBanner
        title="Shipping & Hardware Logistics Policy"
        subtitle="Domestic freight standards, transit timelines, pre-dispatch quality checks, and transit insurance parameters."
        breadcrumbs={[
          { label: 'Help & Policies' },
          { label: 'Shipping Policy' },
        ]}
        badge="Secure Freight Desk"
      />

      <ContentSection>
        <PolicyContent
          title="Hardware Logistics & Freight Fulfillment Policy"
          lastUpdated="October 2026"
          badge="100% Insured Freight"
          summary="This policy outlines the delivery processes, transit insurance coverage, carrier partners, and tracking procedures for all AXINIX hardware equipment."
          sections={sections}
        />
      </ContentSection>
    </div>
  );
}
