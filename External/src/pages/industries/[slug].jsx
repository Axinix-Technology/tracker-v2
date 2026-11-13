import React from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { ArrowLeft, CheckCircle2 } from 'lucide-react';
import { INDUSTRIES, SERVICES, PORTFOLIO } from '../../api/data';
import { PageBanner } from '../../components/PageBanner';
import { ContentSection } from '../../components/ContentSection';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import { ServiceCard } from '../../components/ServiceCard';
import { PortfolioCard } from '../../components/PortfolioCard';
import { FaqAccordion } from '../../components/FaqAccordion';
import { EmptyState } from '../../components/EmptyState';
import { CtaBanner } from '../../components/CtaBanner';

export default function IndustryDetailPage() {
  const { slug, id } = useParams();
  const navigate = useNavigate();
  const param = slug || id;

  const industry = INDUSTRIES.find(i => i.id === param);

  if (!industry) {
    return (
      <ContentSection containerClassName="max-w-xl text-center py-20">
        <EmptyState
          title="Industry Not Located"
          description={`The industry identifier "${param}" does not exist in our catalog.`}
          action={
            <Link to="/industries">
              <Button variant="gold" size="md">
                ← Return to Industries
              </Button>
            </Link>
          }
        />
      </ContentSection>
    );
  }

  const relatedProjects = PORTFOLIO.filter(
    p => p.industryId === industry.id || p.industry.includes(industry.name.split(' ')[0])
  );

  const industryFaqs = [
    {
      question: `How fast can AXINIX be deployed for ${industry.name} businesses?`,
      answer: `Depending on the number of branches and legacy data migration needs, standard onboarding typically completes in 2 to 4 weeks, with parallel training for cashiers, managers, and warehouse staff.`,
    },
    {
      question: `Does the system integrate with existing hardware?`,
      answer: `Yes. Our POS and inventory systems seamlessly interface with ESC/POS thermal printers, USB/Bluetooth barcode guns, electronic weighing scales, and touchscreen terminals.`,
    },
    {
      question: `Can we migrate our existing customer data and stock balances?`,
      answer: `Yes. Our technical team assists with automated Excel/CSV migration routines and data cleansing to ensure accurate opening balances on launch day.`,
    },
  ];

  return (
    <div className="w-full">
      <PageBanner
        title={industry.name}
        subtitle={industry.subtitle}
        badge={industry.category}
        breadcrumbs={[
          { label: 'Industries', to: '/industries' },
          { label: industry.name },
        ]}
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={() => navigate('/industries')} className="gap-1.5">
              <ArrowLeft size={14} />
              <span>All Industries</span>
            </Button>
            <Link to={`/contact?subject=${encodeURIComponent(`Demo Request: ${industry.name}`)}&industry=${encodeURIComponent(industry.name)}`}>
              <Button variant="gold" size="sm">
                Request Demo
              </Button>
            </Link>
          </div>
        }
      />

      <ContentSection className="space-y-10">
        {/* Common Operational Challenges */}
        <div className="space-y-4">
          <div>
            <span className="text-xs font-semibold text-gold tracking-widest uppercase">The Bottlenecks</span>
            <h2 className="text-2xl sm:text-3xl font-serif font-bold text-foreground mt-1 mb-1">
              Common Operational Friction in {industry.name}
            </h2>
            <p className="text-xs text-muted">Core operational challenges solved by AXINIX technology presets.</p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {industry.challenges.map((challenge, cIdx) => (
              <Card key={cIdx} className="p-4 bg-card border border-border/80 hover:border-gold/50 transition-colors">
                <div className="w-7 h-7 rounded-full bg-red-500/10 text-red-400 flex items-center justify-center font-bold text-xs mb-2">
                  !
                </div>
                <h3 className="text-xs font-semibold text-muted uppercase tracking-wider mb-1">
                  Challenge 0{cIdx + 1}
                </h3>
                <p className="text-xs sm:text-sm text-foreground/90 leading-relaxed">
                  {challenge}
                </p>
              </Card>
            ))}
          </div>
        </div>

        {/* Tailored Software Solutions & Features */}
        <Card className="p-6 sm:p-8 bg-card/50 border border-border/80 space-y-6">
          <div className="max-w-2xl">
            <span className="text-xs font-semibold text-gold tracking-widest uppercase">The Blueprint</span>
            <h2 className="text-2xl sm:text-3xl font-serif font-bold text-foreground mt-1">
              Engineered Technology Stack for {industry.name}
            </h2>
            <p className="text-xs sm:text-sm text-muted mt-1.5">
              Our pre-configured domain modules tackle these exact friction points right out of the box.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {industry.features.map((feat, fIdx) => (
              <div key={fIdx} className="bg-deep/60 border border-border/80 rounded-lg p-3 flex items-start gap-2.5">
                <CheckCircle2 size={15} className="text-gold shrink-0 mt-0.5" />
                <span className="text-xs sm:text-sm text-foreground font-medium">{feat}</span>
              </div>
            ))}
          </div>
        </Card>

        {/* Recommended Digital Capabilities / Related Services */}
        <div className="space-y-4">
          <div>
            <h2 className="text-2xl font-serif font-bold text-foreground mb-1">
              Recommended Digital Capabilities
            </h2>
            <p className="text-xs text-muted">
              Pair your core system with high-impact customer-facing digital services:
            </p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {SERVICES.slice(0, 4).map(srv => (
              <ServiceCard key={srv.id} service={srv} />
            ))}
          </div>
        </div>

        {/* Case Studies / Projects for this industry if any */}
        {relatedProjects.length > 0 && (
          <div className="space-y-4">
            <h2 className="text-2xl font-serif font-bold text-foreground">
              Demonstration Case Studies
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {relatedProjects.map(prj => (
                <PortfolioCard key={prj.id} project={prj} />
              ))}
            </div>
          </div>
        )}

        {/* FAQs */}
        <div className="pt-2">
          <FaqAccordion items={industryFaqs} title={`Deployment FAQs for ${industry.name}`} />
        </div>
      </ContentSection>

      {/* Reusable CTA */}
      <CtaBanner
        badge="Industry Specialized"
        title={`Transform Your ${industry.name} Operations with AXINIX`}
        subtitle="Experience how our integrated software streamlines transactions, eliminates discrepancies, and elevates customer satisfaction."
        primaryAction={{
          label: `Schedule a ${industry.name} Consultation`,
          to: `/contact?subject=${encodeURIComponent(`Consultation: ${industry.name}`)}&industry=${encodeURIComponent(industry.name)}`,
        }}
        secondaryAction={{
          label: 'Consult with our Specialists',
          to: `/contact?subject=${encodeURIComponent(`Inquiry: ${industry.name}`)}&industry=${encodeURIComponent(industry.name)}`,
        }}
      />
    </div>
  );
}
