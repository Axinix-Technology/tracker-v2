import React from 'react';
import { PageBanner } from '../../components/PageBanner';
import { WorkhubModuleCalculator } from '../../components/WorkhubModuleCalculator';
import { ComparisonSection } from '../../components/ComparisonSection';
import { ContentSection } from '../../components/ContentSection';
import { CtaBanner } from '../../components/CtaBanner';
import { ScrollReveal } from '../../components/motion';
import { ShieldCheck, Database, Layers, CheckCircle2 } from 'lucide-react';

export default function WorkhubPlatformPage() {
  return (
    <div className="w-full space-y-8 sm:space-y-12">
      {/* 1. Page Banner */}
      <PageBanner
        title="Workhub Modular Business Operating Platform"
        subtitle="Unify all cross-functional operations into a single secure platform with physical database-per-tenant isolation, real-time sync, and zero application sprawl."
        breadcrumbs={[{ label: 'Workhub Platform' }]}
        badge="Enterprise SaaS Monolith (v4.3.0)"
      />

      {/* 2. Interactive Modular Bundle Calculator & Module Explorer */}
      <WorkhubModuleCalculator />

      {/* 3. Operational Comparison (Fragmented App Sprawl vs. Unified Workhub) */}
      <ScrollReveal direction="pop">
        <ComparisonSection />
      </ScrollReveal>

      {/* 4. Enterprise Architecture Pillars */}
      <ScrollReveal direction="pop">
        <ContentSection
          bg="card"
          centered
          badge="Platform Governance"
          title="Engineered for Physical Multi-Tenancy & Zero Data Leakage"
          subtitle="Unlike common shared-database multi-tenant systems, Workhub enforces strict physical boundaries for every client."
        >
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4 text-left">
            <div className="rounded-2xl p-6 bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/10 space-y-3">
              <div className="w-10 h-10 rounded-xl bg-gold/15 text-gold flex items-center justify-center">
                <Database size={20} />
              </div>
              <h4 className="font-serif font-bold text-base text-slate-900 dark:text-white">
                Physical Database-Per-Tenant
              </h4>
              <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
                Your data resides in its own isolated MySQL database schema. Row leaks between organizations are physically impossible at the database engine level.
              </p>
            </div>

            <div className="rounded-2xl p-6 bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/10 space-y-3">
              <div className="w-10 h-10 rounded-xl bg-sky-500/15 text-sky-500 flex items-center justify-center">
                <Layers size={20} />
              </div>
              <h4 className="font-serif font-bold text-base text-slate-900 dark:text-white">
                Graceful Modular Downgrades
              </h4>
              <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
                Removing a module never corrupts your operational workflow. Downstream records (like Tasks linked to Tickets) preserve immutable JSON snapshots permanently.
              </p>
            </div>

            <div className="rounded-2xl p-6 bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/10 space-y-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-500/15 text-emerald-500 flex items-center justify-center">
                <ShieldCheck size={20} />
              </div>
              <h4 className="font-serif font-bold text-base text-slate-900 dark:text-white">
                Automated 30-Day Storage Purge
              </h4>
              <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
                Degraded modules enter a 30-day read-only grace period, followed by automated cold ZIP archival, physical local/S3 attachment removal, and GDPR-compliant row purging.
              </p>
            </div>
          </div>
        </ContentSection>
      </ScrollReveal>

      {/* 5. Closing Call to Action */}
      <CtaBanner
        badge="Zero Commitment"
        title="Deploy a Dedicated Workhub Sandbox for Your Team"
        subtitle="Experience live biometric attendance, automated payroll, Kanban sprints, and customer helpdesk in your own isolated tenant environment."
        primaryAction={{ label: 'Start 14-Day Free Trial', to: '/contact?subject=Workhub%20Sandbox%20Trial' }}
        secondaryAction={{ label: 'Schedule Architecture Walkthrough', to: '/contact?subject=Workhub%20Architecture%20Demo' }}
      />
    </div>
  );
}

