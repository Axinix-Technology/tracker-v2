import React from 'react';
import { PageBanner } from '../../../components/PageBanner';
import { ContentSection } from '../../../components/ContentSection';
import { PolicyContent } from '../../../components/PolicyContent';

export default function PrivacyPolicyPage() {
  const sections = [
    {
      heading: 'Information We Collect & Purpose',
      content:
        'AXINIX TECHNOLOGIES collects information strictly necessary to provision enterprise software, configure multi-branch instances, respond to quotation and demonstration requests, and fulfill contractual technical support. This includes corporate contact details, billing addresses, GSTIN credentials, and authorized administrator identities.',
      bullets: [
        'Enterprise contact information: authorized business email, direct phone, organization name, and headquarters address.',
        'Technical parameters: IP addresses, browser agents, and cryptographic correlation IDs (X-Request-ID) recorded in immutable audit logs.',
        'Billing and payment reconciliation data: transactional references, GST invoice parameters, and license entitlements.',
      ],
    },
    {
      heading: 'Client Data Isolation & Tenant Sovereignty',
      content:
        'All client transactional and operational records processed by AXINIX systems remain 100% the exclusive intellectual property and asset of the client organization. Each tenant environment is strictly isolated with role-based access control (RBAC) boundaries, parameterized queries, and mandatory database sanitization.',
      bullets: [
        'Dedicated database schema isolation ensuring zero cross-tenant query leaks or contamination.',
        'Zero monetization or distribution: AXINIX never sells, rents, or licenses client operational or customer data.',
        'Complete data export availability: client administrators may generate full PostgreSQL/MySQL SQL dumps and CSV archives upon written request.',
      ],
    },
    {
      heading: 'Cryptographic Security & System Auditing',
      content:
        'We enforce industry-standard security protocols across our entire software supply chain and cloud infrastructure. All data in transit is encrypted using modern TLS 1.3 ciphers, and all persistent storage volumes utilize AES-256 encryption at rest.',
      bullets: [
        'Mandatory API audit logging: every mutate and read request is recorded in immutable compliance logs.',
        'Continuous automated vulnerability scanning and third-party penetration testing.',
        'Daily offsite encrypted disaster recovery snapshots stored in dual-region cloud vaults.',
      ],
    },
    {
      heading: 'Data Retention & Right to Erasure',
      content:
        'Enterprise telemetry and system logs are retained for the duration of the active subscription agreement plus 90 days for business continuity reconciliation. Upon contract termination or formal deletion notice, tenant storage volumes and encryption keys are permanently destroyed following NIST SP 800-88 guidelines.',
    },
  ];

  return (
    <div className="w-full">
      <PageBanner
        title="Privacy & Data Governance Policy"
        subtitle="How AXINIX TECHNOLOGIES safeguards confidential enterprise data, multi-tenant databases, and institutional business records."
        breadcrumbs={[
          { label: 'Help & Policies' },
          { label: 'Privacy Policy' },
        ]}
        badge="Enterprise Compliance"
      />

      <ContentSection>
        <PolicyContent
          title="Corporate Data Privacy & Tenant Governance"
          lastUpdated="October 2026"
          badge="GDPR & Indian DPDP Act Compliant"
          summary="This Privacy Policy governs the collection, processing, and strict isolation of data across AXINIX software suites, cloud hosting instances, client portals, and corporate consultation workflows."
          sections={sections}
        />
      </ContentSection>
    </div>
  );
}
