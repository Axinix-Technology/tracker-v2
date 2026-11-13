import React from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { ArrowLeft, CheckCircle2, Send } from 'lucide-react';
import { SERVICES } from '../../api/data';
import { PageBanner } from '../../components/PageBanner';
import { ContentSection } from '../../components/ContentSection';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import { FaqAccordion } from '../../components/FaqAccordion';
import { EmptyState } from '../../components/EmptyState';
import { CtaBanner } from '../../components/CtaBanner';

export default function ServiceDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const service = SERVICES.find(s => s.id === id);

  if (!service) {
    return (
      <ContentSection containerClassName="max-w-xl text-center py-20">
        <EmptyState
          title="Service Not Located"
          description={`The service identifier "${id}" does not exist in our catalog.`}
          action={
            <Link to="/services">
              <Button variant="gold" size="md">
                ← Return to Services
              </Button>
            </Link>
          }
        />
      </ContentSection>
    );
  }

  const serviceFaqs = [
    {
      question: `What is the typical delivery timeline for ${service.title}?`,
      answer: `Standard delivery ranges between 2 to 6 weeks depending on custom feature requirements, API integrations, and review rounds. We provide a milestone-based project schedule upfront.`,
    },
    {
      question: `Do we receive full ownership and source code?`,
      answer: `Yes. Upon final delivery and sign-off, you receive 100% intellectual property ownership, source repositories, documentation, and administrative credentials with zero vendor lock-in.`,
    },
    {
      question: `What post-launch support and warranty is included?`,
      answer: `Every service includes 30 to 90 days of dedicated complimentary post-launch warranty, bug-fixing, and performance monitoring, backed by ongoing SLA maintenance contracts.`,
    },
  ];

  return (
    <div className="w-full">
      <PageBanner
        title={service.title}
        subtitle={service.description}
        badge="Professional Capability"
        breadcrumbs={[
          { label: 'Services', to: '/services' },
          { label: service.title },
        ]}
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={() => navigate('/services')} className="gap-1.5">
              <ArrowLeft size={14} />
              <span>All Services</span>
            </Button>
            <Link to={`/contact/create?service=${encodeURIComponent(service.title)}`}>
              <Button variant="gold" size="sm" className="gap-1.5">
                <Send size={14} />
                <span>Request Quote</span>
              </Button>
            </Link>
          </div>
        }
      />

      <ContentSection className="space-y-10">
        {/* Core Capabilities */}
        <div className="space-y-4">
          <div>
            <span className="text-xs font-semibold text-gold tracking-widest uppercase">Scope of Work</span>
            <h2 className="text-2xl sm:text-3xl font-serif font-bold text-foreground mt-1 mb-1">
              What's Included in {service.title}
            </h2>
            <p className="text-xs text-muted">Comprehensive architectural deliverables and execution stages.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {service.features.map((feat, idx) => (
              <div key={idx} className="bg-card border border-border/80 rounded-lg p-3.5 flex items-start gap-2.5">
                <CheckCircle2 size={15} className="text-gold shrink-0 mt-0.5" />
                <span className="text-xs sm:text-sm text-foreground font-medium">{feat}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Tangible Deliverables */}
        <Card className="p-6 sm:p-8 bg-card/50 border border-border/80 space-y-6">
          <div className="max-w-2xl">
            <span className="text-xs font-semibold text-gold tracking-widest uppercase">Milestones & Assets</span>
            <h2 className="text-2xl sm:text-3xl font-serif font-bold text-foreground mt-1">
              Guaranteed Deliverables
            </h2>
            <p className="text-xs sm:text-sm text-muted mt-1.5">
              Every project is managed with clear documentation, rigorous testing, and transparent progress updates.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {service.deliverables.map((deliv, dIdx) => (
              <div key={dIdx} className="bg-deep/70 border border-border/80 rounded-xl p-4 border-l-4 border-l-gold">
                <span className="text-xs font-semibold text-gold uppercase tracking-wider block mb-1">
                  Deliverable 0{dIdx + 1}
                </span>
                <p className="text-xs sm:text-sm text-foreground font-medium leading-relaxed">
                  {deliv}
                </p>
              </div>
            ))}
          </div>
        </Card>

        {/* FAQs */}
        <div className="pt-2">
          <FaqAccordion items={serviceFaqs} title={`Service FAQs for ${service.title}`} />
        </div>
      </ContentSection>

      {/* Reusable CTA */}
      <CtaBanner
        badge="Accurate Scope & Estimate"
        title={`Get an Accurate Estimate for ${service.title}`}
        subtitle="Our engineering consultants will review your requirements and provide a detailed scope, architecture plan, and cost estimate."
        primaryAction={{
          label: 'Request a Detailed Quote',
          to: `/contact?service=${encodeURIComponent(service.title)}`,
        }}
        secondaryAction={{
          label: 'Book a Consultation',
          to: `/contact?subject=${encodeURIComponent(`Consultation: ${service.title}`)}&service=${encodeURIComponent(service.title)}`,
        }}
      />
    </div>
  );
}
