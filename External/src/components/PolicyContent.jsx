import React from 'react';
import { Link } from 'react-router-dom';
import { Shield, Clock, FileText, ArrowRight, CheckCircle2, HelpCircle } from 'lucide-react';
import { Card } from './ui/Card';
import { Badge } from './ui/Badge';
import { Button } from './ui/Button';

export function PolicyContent({
  title,
  lastUpdated = 'October 2026',
  badge = 'Official Compliance',
  summary,
  sections = [],
  relatedLinks = [
    { label: 'Privacy Policy', to: '/help-policies/privacy-policy' },
    { label: 'Terms of Service', to: '/help-policies/terms' },
    { label: 'Return Policy', to: '/help-policies/return-policy' },
    { label: 'Shipping Policy', to: '/help-policies/shipping-policy' },
    { label: 'FAQ', to: '/help-policies/faq' },
  ],
}) {
  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header Card */}
      <Card className="p-5 sm:p-6 bg-card border border-border/80 space-y-3">
        <div className="flex items-center justify-between gap-2 flex-wrap">
          <Badge variant="gold" size="sm">
            {badge}
          </Badge>
          <div className="flex items-center gap-1.5 text-xs text-muted">
            <Clock size={13} className="text-gold" />
            <span>Effective / Last Updated: {lastUpdated}</span>
          </div>
        </div>

        <h2 className="text-xl sm:text-2xl font-serif font-bold text-foreground">
          {title}
        </h2>

        {summary && (
          <p className="text-xs sm:text-sm text-muted/90 leading-relaxed bg-deep/60 p-3.5 rounded-lg border border-border/50">
            {summary}
          </p>
        )}
      </Card>

      {/* Structured Sections */}
      <div className="space-y-4">
        {sections.map((sec, idx) => (
          <Card key={idx} className="p-5 sm:p-6 bg-card border border-border/80 space-y-3">
            <div className="flex items-baseline gap-2">
              <span className="font-mono text-gold text-xs font-bold">{String(idx + 1).padStart(2, '0')}.</span>
              <h3 className="text-base font-semibold text-foreground">{sec.heading}</h3>
            </div>
            <div className="text-xs sm:text-sm text-muted/90 leading-relaxed space-y-2 pl-6">
              {Array.isArray(sec.content) ? (
                sec.content.map((p, pIdx) => <p key={pIdx}>{p}</p>)
              ) : (
                <p>{sec.content}</p>
              )}
              {sec.bullets && (
                <ul className="space-y-1.5 pt-2">
                  {sec.bullets.map((b, bIdx) => (
                    <li key={bIdx} className="flex items-start gap-2">
                      <CheckCircle2 size={13} className="text-gold shrink-0 mt-0.5" />
                      <span>{b}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </Card>
        ))}
      </div>

      {/* Related Legal Policies Navigation */}
      <Card className="p-5 bg-deep border border-border/80 space-y-3">
        <h4 className="text-xs font-semibold text-muted uppercase tracking-wider">
          Legal & Governance Directory
        </h4>
        <div className="flex flex-wrap gap-2">
          {relatedLinks.map((link, idx) => (
            <Link
              key={idx}
              to={link.to}
              className="px-3 py-1.5 rounded-full bg-card hover:bg-white/5 border border-border/70 text-xs text-foreground/90 hover:text-gold transition-colors"
            >
              {link.label}
            </Link>
          ))}
        </div>
      </Card>

      {/* Support Action Callout */}
      <Card className="p-5 bg-card border border-gold/30 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-3 text-xs">
          <div className="w-10 h-10 rounded-full bg-gold/10 text-gold flex items-center justify-center shrink-0">
            <HelpCircle size={18} />
          </div>
          <div>
            <h4 className="font-semibold text-foreground">Questions regarding this policy?</h4>
            <p className="text-muted">Our compliance and legal operations desk is at your disposal.</p>
          </div>
        </div>
        <Link to="/contact/create" className="w-full sm:w-auto">
          <Button size="sm" variant="gold" className="w-full sm:w-auto text-xs font-semibold gap-1.5">
            <span>Contact Legal Desk</span>
            <ArrowRight size={13} />
          </Button>
        </Link>
      </Card>
    </div>
  );
}

