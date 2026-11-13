import React from 'react';
import { PageBanner } from '../../../components/PageBanner';
import { ContentSection } from '../../../components/ContentSection';
import { PolicyContent } from '../../../components/PolicyContent';

export default function CookiePolicyPage() {
  const sections = [
    {
      heading: 'What Are Cookies & Local Storage Tokens',
      content:
        'Cookies and browser Local Storage are small cryptographic text files placed on your client device when accessing our web portals, customer account consoles, and interactive demo environments.',
    },
    {
      heading: 'Categories of Cookies We Use',
      content:
        'We categorize our browser storage mechanisms into strictly essential operational tokens and functional preference states:',
      bullets: [
        'Strictly Essential Cookies: Session authentication tokens, CSRF protection nonces, and correlation headers required for API security.',
        'Functional Preference Tokens: Theme preferences (dark/light mode), cart configurations, and regional currency settings.',
        'Zero Invasive Tracking: AXINIX does NOT deploy behavioral ad-tracking pixels, cross-site trackers, or third-party marketing beacons.',
      ],
    },
    {
      heading: 'Managing Your Preferences',
      content:
        'Users may control, restrict, or clear cookies through their browser settings. Disabling essential session cookies may limit access to authenticated customer account portals and live license management dashboards.',
    },
  ];

  return (
    <div className="w-full">
      <PageBanner
        title="Cookie & Local Storage Policy"
        subtitle="Transparent disclosures on browser state tokens, authentication cookies, and client preference mechanisms."
        breadcrumbs={[
          { label: 'Help & Policies' },
          { label: 'Cookie Policy' },
        ]}
        badge="Data Protection"
      />

      <ContentSection>
        <PolicyContent
          title="Cookie & Session Management Policy"
          lastUpdated="October 2026"
          badge="Zero Third-Party Ad Trackers"
          summary="This disclosure clarifies our minimal use of cookies and Local Storage strictly for operational security and client portal session persistence."
          sections={sections}
        />
      </ContentSection>
    </div>
  );
}
