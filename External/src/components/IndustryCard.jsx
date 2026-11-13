import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, CheckCircle2 } from 'lucide-react';
import { Card } from './ui/Card';
import { Badge } from './ui/Badge';
import { getInitials } from '../utils/formatters';

export function IndustryCard({ industry, showFeatures = true }) {
  if (!industry) return null;

  return (
    <Link to={`/industries/${industry.id}`} className="group block h-full">
      <Card interactive className="h-full flex flex-col justify-between">
        <div>
          <div className="flex items-center justify-between mb-3">
            <div className="w-10 h-10 rounded-lg bg-soft/10 text-royal-light flex items-center justify-center font-bold font-serif text-sm border-b-2 border-gold group-hover:scale-105 transition-transform">
              {getInitials(industry.name)}
            </div>
            {industry.category && <Badge variant="neutral" size="sm">{industry.category}</Badge>}
          </div>

          <h3 className="text-lg font-serif font-semibold text-foreground group-hover:text-gold transition-colors mb-2">
            {industry.name}
          </h3>
          <p className="text-xs text-muted leading-relaxed line-clamp-2 mb-4">
            {industry.subtitle}
          </p>

          {showFeatures && industry.features && (
            <div className="space-y-1.5 mb-5 pt-3 border-t border-border/40">
              {industry.features.slice(0, 3).map((feat, fIdx) => (
                <div key={fIdx} className="flex items-center gap-1.5 text-xs text-foreground/80 truncate">
                  <CheckCircle2 size={12} className="text-gold shrink-0" />
                  <span className="truncate">{feat}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="pt-3 border-t border-border/40 flex items-center justify-between text-xs text-gold font-medium">
          <span>View industry architecture</span>
          <ArrowRight size={14} className="group-hover:translate-x-1 transition-transform" />
        </div>
      </Card>
    </Link>
  );
}

