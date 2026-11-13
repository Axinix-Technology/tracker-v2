import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';
import { Card } from './ui/Card';
import { Badge } from './ui/Badge';

export function PortfolioCard({ project }) {
  if (!project) return null;

  return (
    <Link
      to={`/contact?subject=${encodeURIComponent(`Case Study Inquiry: ${project.title}`)}&industry=${encodeURIComponent(project.industry || '')}`}
      className="group block h-full"
    >
      <Card interactive className="h-full flex flex-col justify-between">
        <div>
          <div className="flex items-center justify-between mb-3">
            <Badge variant="gold" size="sm">{project.category}</Badge>
            <span className="text-[11px] text-muted">{project.industry}</span>
          </div>

          <h3 className="text-xl font-serif font-semibold text-foreground group-hover:text-gold transition-colors mb-2">
            {project.title}
          </h3>
          <p className="text-xs text-muted font-medium mb-3">
            {project.client}
          </p>
          <p className="text-xs text-muted leading-relaxed line-clamp-3 mb-4">
            {project.challenge}
          </p>

          {project.tags && (
            <div className="flex flex-wrap gap-1.5 mb-4">
              {project.tags.map((tag, tIdx) => (
                <Badge key={tIdx} variant="neutral" size="sm">
                  {tag}
                </Badge>
              ))}
            </div>
          )}
        </div>

        <div className="pt-4 border-t border-border/40 flex items-center justify-between text-xs text-gold font-medium">
          <span>Inquire about this architecture</span>
          <ArrowRight size={14} className="group-hover:translate-x-1 transition-transform" />
        </div>
      </Card>
    </Link>
  );
}
