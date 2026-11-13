import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, CheckCircle2 } from 'lucide-react';
import { Card } from './ui/Card';
import { Badge } from './ui/Badge';
import { getInitials } from '../utils/formatters';

export function SolutionCard({ solution, showFeatures = false }) {
  if (!solution) return null;

  return (
    <Link to={`/solutions/${solution.id}`} className="group block h-full">
      <Card interactive className="h-full flex flex-col justify-between">
        <div>
          <div className="flex items-center justify-between mb-4">
            <div className="w-11 h-11 rounded-lg bg-soft/10 text-royal-light flex items-center justify-center font-bold font-serif text-base border-b-2 border-gold group-hover:scale-105 transition-transform">
              {getInitials(solution.title)}
            </div>
            {solution.badge && <Badge variant="neutral" size="sm">{solution.badge}</Badge>}
          </div>

          <h3 className="text-lg font-serif font-semibold text-foreground group-hover:text-gold transition-colors mb-2">
            {solution.title}
          </h3>
          <p className="text-xs text-muted leading-relaxed mb-4">
            {solution.subtitle}
          </p>

          {showFeatures && solution.features && (
            <div className="space-y-2 mb-5">
              {solution.features.slice(0, 4).map((feat, fIdx) => (
                <div key={fIdx} className="flex items-start gap-2 text-xs text-foreground/80">
                  <CheckCircle2 size={13} className="text-gold shrink-0 mt-0.5" />
                  <span>{feat}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="pt-3 border-t border-border/40 flex items-center justify-between text-xs text-gold font-medium">
          <span>{showFeatures ? 'Explore full specifications' : 'Explore features'}</span>
          <ArrowRight size={14} className="group-hover:translate-x-1 transition-transform" />
        </div>
      </Card>
    </Link>
  );
}

