import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';
import { Card } from './ui/Card';
import { Badge } from './ui/Badge';
import { getInitials } from '../utils/formatters';

export function CategoryCard({ category }) {
  if (!category) return null;

  return (
    <Link to={`/category/${category.slug}`} className="group block h-full">
      <Card interactive className="h-full flex flex-col justify-between">
        <div>
          <div className="flex items-center justify-between mb-4">
            <div className="w-11 h-11 rounded-lg bg-soft/10 text-royal-light flex items-center justify-center font-bold font-serif text-base border-b-2 border-gold group-hover:scale-105 transition-transform">
              {getInitials(category.name)}
            </div>
            {category.badge && (
              <Badge variant="neutral" size="sm">
                {category.badge}
              </Badge>
            )}
          </div>

          <h3 className="text-lg font-serif font-semibold text-foreground group-hover:text-gold transition-colors mb-2">
            {category.name}
          </h3>
          <p className="text-xs text-muted leading-relaxed mb-4">
            {category.description}
          </p>
        </div>

        <div className="pt-3 border-t border-border/40 flex items-center justify-between text-xs text-gold font-medium">
          <span>Explore {category.itemCount || ''} Packages</span>
          <ArrowRight size={14} className="group-hover:translate-x-1 transition-transform" />
        </div>
      </Card>
    </Link>
  );
}

