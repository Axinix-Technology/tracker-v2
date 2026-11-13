import React from 'react';
import { Link } from 'react-router-dom';
import { Target, Eye } from 'lucide-react';
import { PageBanner } from '../../components/PageBanner';
import { ContentSection } from '../../components/ContentSection';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import { Badge } from '../../components/ui/Badge';
import { SectionHeader } from '../../components/SectionHeader';
import { WhyChooseUsGrid } from '../../components/WhyChooseUsGrid';
import { CtaBanner } from '../../components/CtaBanner';

export default function AboutPage() {
  return (
    <div className="w-full">
      <PageBanner
        title="About AXINIX TECHNOLOGIES"
        subtitle="We are focused on helping businesses embrace technology through intelligent software, modern digital experiences, and customized operational solutions."
        breadcrumbs={[{ label: 'About Us' }]}
        badge="Enterprise Story"
      />

      <ContentSection className="space-y-10">
        {/* Vision & Mission Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="p-6 sm:p-8 bg-card border border-border/80 hover:border-gold/60 transition-colors space-y-3">
            <div className="w-11 h-11 rounded-xl bg-gold/15 text-gold flex items-center justify-center font-bold border border-gold/30">
              <Eye size={22} />
            </div>
            <h2 className="text-xl sm:text-2xl font-serif font-bold text-foreground">Our Vision</h2>
            <p className="text-xs sm:text-sm text-muted/90 leading-relaxed">
              To become a trusted technology partner for businesses across industries worldwide by making enterprise technology accessible, practical, scalable, and impactful.
            </p>
          </Card>

          <Card className="p-6 sm:p-8 bg-card border border-border/80 hover:border-royal/60 transition-colors space-y-3">
            <div className="w-11 h-11 rounded-xl bg-royal/20 text-royal-light flex items-center justify-center font-bold border border-royal/40">
              <Target size={22} />
            </div>
            <h2 className="text-xl sm:text-2xl font-serif font-bold text-foreground">Our Mission</h2>
            <p className="text-xs sm:text-sm text-muted/90 leading-relaxed">
              To simplify complex business operations, engineer innovative digital solutions, and empower business owners and their teams to grow with confidence and clarity.
            </p>
          </Card>
        </div>

        {/* Core Values */}
        <Card className="p-6 sm:p-10 bg-card/40 border border-border/80 space-y-6">
          <SectionHeader
            centered
            badge="Our Operating Ethos"
            title="Core Principles Guiding Every Build"
            subtitle="We never believe in temporary patches or shortcuts. We design for longevity, performance, and operational precision."
          />
          <WhyChooseUsGrid />
        </Card>

        {/* Careers & Join Us */}
        <Card className="p-6 sm:p-10 bg-deep border border-border/80 flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="space-y-2 max-w-xl">
            <Badge variant="gold" size="sm">Talent & Careers</Badge>
            <h3 className="text-2xl font-serif font-bold text-white">Join Our Engineering & Product Team</h3>
            <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
              We are constantly seeking brilliant software engineers, UI/UX systems designers, and customer success architects who are passionate about building real-world enterprise infrastructure.
            </p>
          </div>
          <Link to="/careers" className="shrink-0">
            <Button variant="gold" size="md">
              Explore Career Openings
            </Button>
          </Link>
        </Card>
      </ContentSection>

      <CtaBanner
        badge="Enterprise Partnership"
        title="Start Building With AXINIX Today"
        subtitle="Schedule a consultation with our systems architects to evaluate your technical and digital roadmap."
        primaryAction={{ label: 'Schedule Consultation', to: '/contact?subject=Consultation%20Request' }}
        secondaryAction={{ label: 'Contact Corporate Office', to: '/contact' }}
      />
    </div>
  );
}
