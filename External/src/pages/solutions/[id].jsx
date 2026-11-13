import React from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { ArrowLeft, CheckCircle2, ShieldCheck, Zap } from 'lucide-react';
import { SOLUTIONS, INDUSTRIES } from '../../api/data';
import { PageBanner } from '../../components/PageBanner';
import { ContentSection } from '../../components/ContentSection';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import { Badge } from '../../components/ui/Badge';
import { FaqAccordion } from '../../components/FaqAccordion';
import { DashboardPreview } from '../../components/DashboardPreview';
import { EmptyState } from '../../components/EmptyState';
import { CtaBanner } from '../../components/CtaBanner';
import { getInitials } from '../../utils/formatters';

export default function SolutionDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const solution = SOLUTIONS.find(s => s.id === id);

  if (!solution) {
    return (
      <ContentSection containerClassName="max-w-xl text-center py-20">
        <EmptyState
          title="Solution Not Located"
          description={`The enterprise solution identifier "${id}" does not exist in our catalog.`}
          action={
            <Link to="/solutions">
              <Button variant="gold" size="md">
                ← Return to Solutions
              </Button>
            </Link>
          }
        />
      </ContentSection>
    );
  }

  const solutionFaqs = [
    {
      question: `Is ${solution.title} available for deployment now?`,
      answer: `Yes. Core modules are production-ready. We configure branch locations, user permission roles, and customized print/report templates within 7–14 days. Request a live demo to review deployment timelines.`,
    },
    {
      question: `Can it be tailored to our specific multi-branch workflows?`,
      answer: `Absolutely. AXINIX specializes in custom workflow adaptation. We adapt database schemas, tax structures, approval chains, and third-party integrations to match your operational playbook.`,
    },
    {
      question: `What are the licensing and cloud hosting options?`,
      answer: `We offer scalable annual SaaS subscriptions hosted on secure private clouds as well as on-premise hybrid deployments with local offline edge nodes.`,
    },
  ];

  return (
    <div className="w-full">
      <PageBanner
        title={solution.title}
        subtitle={solution.description}
        badge={solution.badge}
        initials={getInitials(solution.title)}
        breadcrumbs={[
          { label: 'Solutions', to: '/solutions' },
          { label: solution.title },
        ]}
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={() => navigate('/solutions')} className="gap-1.5">
              <ArrowLeft size={14} />
              <span>Back to List</span>
            </Button>
            <Link to={`/contact?subject=${encodeURIComponent(`Demo Request: ${solution.title}`)}&service=Solutions`}>
              <Button variant="gold" size="sm">
                Request Demo
              </Button>
            </Link>
          </div>
        }
      />

      <ContentSection className="space-y-10">
        {/* Features & Dashboard Preview */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-center">
          <div className="lg:col-span-7 space-y-4">
            <div>
              <span className="text-xs font-semibold text-gold tracking-widest uppercase">System Capabilities</span>
              <h2 className="text-2xl sm:text-3xl font-serif font-bold text-foreground mt-1 mb-2">
                Engineered for High Reliability & Scale
              </h2>
              <p className="text-xs sm:text-sm text-muted leading-relaxed">
                {solution.title} eliminates operational friction and provides crystal-clear audit trails across departments.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {solution.features.map((feat, idx) => (
                <div key={idx} className="bg-card border border-border/80 rounded-lg p-3 flex items-start gap-2.5">
                  <CheckCircle2 size={15} className="text-gold shrink-0 mt-0.5" />
                  <span className="text-xs text-foreground font-medium">{feat}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="lg:col-span-5 w-full">
            <DashboardPreview />
          </div>
        </div>

        {/* Business Benefits */}
        <Card className="p-6 sm:p-8 bg-card/50 border border-border/80 space-y-5">
          <h2 className="text-xl sm:text-2xl font-serif font-bold text-foreground">
            Measurable Business Impact
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {solution.benefits.map((benefit, bIdx) => (
              <div key={bIdx} className="border-l-2 border-gold pl-3.5 space-y-1">
                <span className="text-[11px] font-semibold text-gold uppercase tracking-wider">Benefit 0{bIdx + 1}</span>
                <p className="text-xs sm:text-sm text-foreground/90 font-medium leading-relaxed">
                  {benefit}
                </p>
              </div>
            ))}
          </div>
        </Card>

        {/* Industries Supported */}
        <div className="space-y-3">
          <h2 className="text-xl sm:text-2xl font-serif font-bold text-foreground">
            Industries Utilizing {solution.title}
          </h2>
          <p className="text-xs text-muted">
            Select an industry to explore tailored modules and configuration presets:
          </p>
          <div className="flex flex-wrap gap-2 pt-1">
            {INDUSTRIES.map(ind => (
              <Link
                key={ind.id}
                to={`/industries/${ind.id}`}
                className="px-3 py-1.5 rounded-full text-xs font-medium bg-card border border-border/80 text-foreground hover:border-gold hover:text-gold transition-colors"
              >
                {ind.name}
              </Link>
            ))}
          </div>
        </div>

        {/* FAQs */}
        <div className="pt-2">
          <FaqAccordion items={solutionFaqs} title={`Frequently Asked Questions About ${solution.title}`} />
        </div>
      </ContentSection>

      {/* Reusable CTA */}
      <CtaBanner
        badge="Live Walkthrough"
        title={`Ready to See ${solution.title} in Action?`}
        subtitle="Book a dedicated 30-minute interactive live demonstration with our senior solution engineers."
        primaryAction={{
          label: `Request ${solution.title} Consultation`,
          to: `/contact?subject=${encodeURIComponent(`Consultation: ${solution.title}`)}&service=Solutions`,
        }}
        secondaryAction={{
          label: 'Request Pricing & Quotation',
          to: `/contact?subject=${encodeURIComponent(`Pricing Request: ${solution.title}`)}&service=Solutions`,
        }}
      />
    </div>
  );
}
