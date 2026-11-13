import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, CheckCircle2 } from 'lucide-react';
import { Card } from './ui/Card';
import { Badge } from './ui/Badge';
import { getInitials } from '../utils/formatters';

export function ServiceCard({ service, showFeatures = false }) {
  if (!service) return null;

  return (
    <Link to={`/services/${service.id}`} className="group block h-full">
      <Card interactive className="h-full flex flex-col justify-between">
        <div>
          <div className="flex items-center justify-between mb-4">
            <div className="w-11 h-11 rounded-lg bg-soft/10 text-royal-light flex items-center justify-center font-bold font-serif text-base border-b-2 border-gold group-hover:scale-105 transition-transform">
              {getInitials(service.title)}
            </div>
            {service.badge && <Badge variant="neutral" size="sm">{service.badge}</Badge>}
          </div>

          <h3 className="text-xl font-serif font-semibold text-foreground group-hover:text-gold transition-colors mb-2">
            {service.title}
          </h3>
          <p className="text-xs text-muted leading-relaxed mb-4">
            {service.subtitle}
          </p>

          {service.features && (
            <div className="space-y-2 mb-5">
              {service.features.slice(0, showFeatures ? 4 : 3).map((feat, fIdx) => (
                <div key={fIdx} className="flex items-start gap-2 text-xs text-foreground/85">
                  <CheckCircle2 size={13} className="text-gold shrink-0 mt-0.5" />
                  <span>{feat}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="pt-3 border-t border-border/40 flex items-center justify-between text-xs text-gold font-medium">
          <span>Explore deliverables & quote</span>
          <ArrowRight size={14} className="group-hover:translate-x-1 transition-transform" />
        </div>
      </Card>
    </Link>
  );
}

