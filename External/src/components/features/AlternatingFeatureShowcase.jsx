import React, { useState, useEffect } from 'react';
import { FeaturePageHeader } from './FeaturePageHeader';
import { AlternatingFeatureSection } from './AlternatingFeatureSection';
import { apiClient } from '../../api/client';
import { cn } from '../../utils/cn';

export const DEFAULT_FEATURE_CARDS = [
  {
    id: 'dest-solutions',
    title: 'Enterprise Solutions',
    eyebrow: 'Enterprise Core',
    description: 'Intelligent software suites connecting supply chain, CRM, POS retail billing, HRMS payroll, and multi-location operations into a single real-time dashboard.',
    benefits: [
      'Eliminate manual data re-entry across disconnected systems',
      'Dynamic policy-governed permission engine & multi-tenant workflows',
      'Real-time operational dashboards, financial ledgers & audit logging',
    ],
    cta: {
      label: 'Explore Solutions',
      targetId: 'dest-solutions',
      to: '/solutions',
    },
    image: '/hero_concept_2.jpg',
    order: 1,
    is_active: true,
  },
  {
    id: 'dest-industries',
    title: 'Industry Verticals',
    eyebrow: 'Domain Tailored',
    description: 'Pre-configured vertical architectures adapted for high-compliance manufacturing, logistics, healthcare, retail distribution, and enterprise services.',
    benefits: [
      'Industry-specific compliance, tax, and validation rules',
      'Rapid deployment blueprints engineered for high-throughput scale',
      'Modular schema extensions adapted for localized operations',
    ],
    cta: {
      label: 'Explore Industries',
      targetId: 'dest-industries',
      to: '/industries',
    },
    image: '/hero_concept_1.jpg',
    order: 2,
    is_active: true,
  },
  {
    id: 'dest-services',
    title: 'Technology Services',
    eyebrow: 'Engineering & Advisory',
    description: 'Specialized systems engineering, cloud infrastructure migration, legacy application modernization, and 24/7 mission-critical platform support.',
    benefits: [
      'Zero-downtime database and populate API migration strategies',
      'High-concurrency performance optimization & backend hardening',
      'Direct engineer-to-engineer technical advisory and SLA support',
    ],
    cta: {
      label: 'Explore Services',
      targetId: 'dest-services',
      to: '/services',
    },
    image: '/hero_concept_3.jpg',
    order: 3,
    is_active: true,
  },
  {
    id: 'dest-products',
    title: 'Core Products',
    eyebrow: 'Packaged Software',
    description: 'High-performance enterprise software products and ready-to-deploy modules built for seamless integration into your corporate technology stack.',
    benefits: [
      'Battle-tested enterprise reliability and bank-grade security',
      'REST & real-time WebSocket communication protocols',
      'Automated telemetry, distributed diagnostics & continuous health checks',
    ],
    cta: {
      label: 'Explore Products',
      targetId: 'dest-products',
      to: '/products',
    },
    image: '/hero_concept_2.jpg',
    order: 4,
    is_active: true,
  },
  {
    id: 'dest-about',
    title: 'About AXINIX',
    eyebrow: 'Company & Mission',
    description: 'Pioneering resilient, enterprise-grade business technology with deep operational immersion, architectural discipline, and customer-first partnership.',
    benefits: [
      '8+ years of dedicated enterprise technology and software delivery',
      '150+ organizations powered across 16+ diverse industry verticals',
      'Uncompromising commitment to zero-hardcode, scalable platform architecture',
    ],
    cta: {
      label: 'Learn About Us',
      targetId: 'dest-about',
      to: '/about',
    },
    image: '/hero_concept_1.jpg',
    order: 5,
    is_active: true,
  },
  {
    id: 'dest-careers',
    title: 'Careers at AXINIX',
    eyebrow: 'Join Our Team',
    description: 'Join an elite engineering culture solving high-impact distributed systems, enterprise product architecture, and operational challenges.',
    benefits: [
      'Direct ownership of high-throughput enterprise platform systems',
      'Collaborative, meritocratic culture with modern tooling and high autonomy',
      'Comprehensive benefits, growth mentorship, and remote-friendly flexibility',
    ],
    cta: {
      label: 'View Open Positions',
      targetId: 'dest-careers',
      to: '/careers',
    },
    image: '/hero_concept_3.jpg',
    order: 6,
    is_active: true,
  },
  {
    id: 'dest-contact',
    title: 'Connect With Our Team',
    eyebrow: 'Start The Conversation',
    description: 'Schedule a one-on-one architecture consultation with our technology specialists to evaluate your technical and operational roadmap.',
    benefits: [
      'Detailed technical feasibility and operational readiness assessment',
      'Customized deployment blueprint and infrastructure cost projection',
      'Dedicated solutions architect assigned to your discovery process',
    ],
    cta: {
      label: 'Contact Us',
      targetId: 'dest-contact',
      to: '/contact',
    },
    image: '/hero_concept_2.jpg',
    order: 7,
    is_active: true,
  },
];

/**
 * AlternatingFeatureShowcase
 * Reusable composite section rendering a centered header and an alternating split-card stream.
 * Automatically alternates sides (Card 1: L/R, Card 2: R/L, Card 3: L/R, etc.) for any number of destination cards.
 * Hydrates dynamically from backend CMS (`site_section_content`) with resilient baseline fallback.
 *
 * @param {string} [eyebrow='Complete Ecosystem']
 * @param {string} [title='Everything Your Business Needs. All in One Unified Platform.']
 * @param {string} [description]
 * @param {Array} [features] - Optional features array override
 * @param {string} [className] - Wrapper class override
 */
export function AlternatingFeatureShowcase({
  eyebrow = 'Complete Ecosystem',
  title = 'Everything Your Business Needs. All in One Unified Platform.',
  description = 'Explore our enterprise software suites, industry-specific architectures, specialized engineering services, and packaged software products.',
  features,
  className = '',
  ...props
}) {
  const [headerState, setHeaderState] = useState({ eyebrow, title, description });
  const [cardsList, setCardsList] = useState(features || DEFAULT_FEATURE_CARDS);

  // If external features prop changes, synchronize state
  useEffect(() => {
    if (features && Array.isArray(features)) {
      setCardsList(features);
    }
  }, [features]);

  // Attempt live hydration from CMS database
  useEffect(() => {
    let isMounted = true;

    async function loadCmsContent() {
      try {
        const res = await apiClient.populateRead('site_section_content');
        const sections = res?.data?.data || [];
        const sectionData = sections.find(
          (s) => s.section_key === 'alternating_feature_cards'
        );

        if (sectionData && isMounted) {
          setHeaderState({
            eyebrow: sectionData.badge || eyebrow,
            title: sectionData.title || title,
            description: sectionData.subtitle || description,
          });

          const cmsCards = sectionData.content?.cards;
          if (Array.isArray(cmsCards) && cmsCards.length > 0) {
            // Filter active cards and sort by order
            const activeCards = cmsCards
              .filter((c) => c.is_active !== false)
              .sort((a, b) => (a.order || 0) - (b.order || 0));

            if (activeCards.length > 0) {
              setCardsList(activeCards);
            }
          }
        }
      } catch (err) {
        // Silently preserve baseline defaults on network / cold-start
      }
    }

    if (!features) {
      loadCmsContent();
    }

    return () => {
      isMounted = false;
    };
  }, [features, eyebrow, title, description]);

  return (
    <section
      className={cn(
        'w-full max-w-[1600px] mx-auto px-4 sm:px-8 lg:px-12 xl:px-16 py-12 sm:py-20 lg:py-24 relative overflow-hidden',
        className
      )}
      {...props}
    >
      {/* Centered Eyebrow & Prominent Headline */}
      <FeaturePageHeader
        eyebrow={headerState.eyebrow}
        title={headerState.title}
        description={headerState.description}
      />

      {/* Alternating Split Cards Stream */}
      <div className="space-y-6 sm:space-y-10 lg:space-y-16">
        {cardsList.map((feature, index) => {
          // Dynamic alternating: Even index = Content Left, Visual Right
          // Odd index = Visual Left, Content Right
          const isReversed = index % 2 !== 0;

          return (
            <AlternatingFeatureSection
              key={feature.id || `feature-${index}`}
              id={feature.id}
              reverse={isReversed}
              feature={feature}
            />
          );
        })}
      </div>
    </section>
  );
}

