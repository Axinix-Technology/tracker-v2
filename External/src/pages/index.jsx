import React from 'react';
import { HeroBanner } from '../components/HeroBanner';
import { AlternatingFeatureShowcase } from '../components/features';
import { ComparisonSection } from '../components/ComparisonSection';
import { RoiCalculator } from '../components/RoiCalculator';
import { ContentSection } from '../components/ContentSection';
import { WhyChooseUsGrid } from '../components/WhyChooseUsGrid';
import { TestimonialSlider } from '../components/TestimonialSlider';
import { CtaBanner } from '../components/CtaBanner';
import { ScrollReveal } from '../components/motion';

export default function HomePage() {
  return (
    <div className="w-full space-y-4 sm:space-y-6">
      {/* 1. Spacious Hero with Orchestrated Pop-in Entrance */}
      <HeroBanner />

      {/* 2. Alternating Split-Card Destination Showcase */}
      <AlternatingFeatureShowcase />

      {/* 5. Interactive Before vs. After Operational Switcher */}
      <ScrollReveal direction="pop">
        <ComparisonSection />
      </ScrollReveal>

      {/* 6. Live Interactive Business Savings & ROI Calculator */}
      <ScrollReveal direction="pop">
        <RoiCalculator />
      </ScrollReveal>

      {/* 7. Why Choose AXINIX: 4 Core Pillars */}
      <ScrollReveal direction="pop">
        <ContentSection
          bg="deep"
          centered
          badge="The Axinix Advantage"
          title="More Than Technology. A Partner in Your Growth."
          subtitle="We stand apart through our deep operational immersion, responsive human support, and engineered software scalability."
        >
          <WhyChooseUsGrid />
        </ContentSection>
      </ScrollReveal>

      {/* 8. Client Testimonials Carousel */}
      <ScrollReveal direction="pop">
        <ContentSection
          bg="card"
          centered
          badge="Client Trust"
          title="What Our Enterprise Clients Say"
          containerClassName="max-w-4xl"
        >
          <TestimonialSlider />
        </ContentSection>
      </ScrollReveal>

      {/* 9. Closing Call to Action Banner */}
      <CtaBanner
        badge="Get Started"
        title="Ready to Transform Your Business Technology?"
        subtitle="Schedule a consultation with our technology specialists to evaluate your technical and operational roadmap."
        primaryAction={{ label: 'Contact Our Team', to: '/contact' }}
        secondaryAction={{ label: 'Explore Our Products', to: '/products' }}
      />
    </div>
  );
}
