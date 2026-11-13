import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, FileText } from 'lucide-react';
import { Card } from './ui/Card';
import { Badge } from './ui/Badge';
import { getInitials, formatCurrency } from '../utils/formatters';

export function ProductCard({ product }) {
  if (!product) return null;

  return (
    <Card interactive className="h-full flex flex-col justify-between group">
      <div>
        {/* Top initials box + badge */}
        <div className="flex items-center justify-between mb-4">
          <div className="w-11 h-11 rounded-lg bg-soft/10 text-royal-light flex items-center justify-center font-bold font-serif text-base border-b-2 border-gold group-hover:scale-105 transition-transform">
            {getInitials(product.name)}
          </div>
          {product.badge && (
            <Badge variant="neutral" size="sm">
              {product.badge}
            </Badge>
          )}
        </div>

        {/* Title */}
        <h3 className="text-lg font-serif font-semibold text-foreground group-hover:text-gold transition-colors mb-2">
          {product.name}
        </h3>

        {/* Subtitle */}
        <p className="text-xs text-muted leading-relaxed mb-4">
          {product.tagline || product.description}
        </p>
      </div>

      {/* Footer Row: Pricing & Enterprise Inquiry CTA */}
      <div className="pt-3 border-t border-border/40 flex items-center justify-between text-xs text-gold font-medium">
        <span className="font-serif font-bold text-foreground text-sm">
          {formatCurrency(product.price)}
          {product.period === 'year' && (
            <span className="text-xs text-muted font-normal ml-1 font-sans">/ yr</span>
          )}
          {product.period === 'month' && (
            <span className="text-xs text-muted font-normal ml-1 font-sans">/ mo</span>
          )}
        </span>

        <Link
          to={`/contact?subject=${encodeURIComponent(`Product Inquiry & Quote: ${product.name}`)}&service=Products`}
          className="inline-flex items-center gap-1.5 text-xs text-gold hover:text-gold-hover hover:underline transition-colors font-semibold"
        >
          <span>Request Quote</span>
          <ArrowRight size={13} className="group-hover:translate-x-0.5 transition-transform" />
        </Link>
      </div>
    </Card>
  );
}
