import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { CATEGORIES, PRODUCTS } from '../api/data';
import { ProductCard } from './ProductCard';
import { CategoryCard } from './CategoryCard';
import { Card } from './ui/Card';
import { Badge } from './ui/Badge';
import { Button } from './ui/Button';
import { getInitials } from '../utils/formatters';

export function CategoryShowcase({
  activeCategorySlug = 'software-suites',
}) {
  const currentCategory =
    CATEGORIES.find(c => c.slug === activeCategorySlug) || CATEGORIES[0];

  const filteredProducts = PRODUCTS.filter(
    p => p.category === currentCategory.slug || p.category === currentCategory.id
  );

  const otherCategories = CATEGORIES.filter(c => c.slug !== currentCategory.slug);

  return (
    <div className="space-y-10">
      {/* Active Category Description Card (matching Image 2 Card aesthetics) */}
      <Card className="p-6 sm:p-8 bg-card border border-border/80">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-lg bg-soft/10 text-royal-light flex items-center justify-center font-bold font-serif text-lg border-b-2 border-gold shrink-0">
              {getInitials(currentCategory.name)}
            </div>
            <div className="space-y-1">
              <div className="flex items-center gap-2 flex-wrap">
                <h2 className="text-xl sm:text-2xl font-serif font-bold text-foreground">
                  {currentCategory.name}
                </h2>
                <Badge variant="gold" size="sm">
                  {currentCategory.badge}
                </Badge>
              </div>
              <p className="text-xs sm:text-sm text-muted max-w-2xl leading-relaxed">
                {currentCategory.description}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 shrink-0 self-start sm:self-auto">
            <Link to="/products">
              <Button size="sm" variant="outline" className="gap-1.5 text-xs">
                <ArrowLeft size={13} />
                <span>All Products</span>
              </Button>
            </Link>
          </div>
        </div>
      </Card>

      {/* Products Grid as Clean Cards (matching Image 2 format) */}
      <div className="space-y-4">
        <div className="flex items-center justify-between pb-2 border-b border-border/60">
          <h3 className="text-sm font-bold text-foreground uppercase tracking-wider">
            Available Packages in {currentCategory.name} ({filteredProducts.length})
          </h3>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProducts.map(product => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      </div>

      {/* Explore Other Categories as Clean Cards (Image 2 format) */}
      <div className="space-y-4 pt-4 border-t border-border/60">
        <h3 className="text-sm font-bold text-muted uppercase tracking-wider">
          Other Categories
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {otherCategories.map(cat => (
            <CategoryCard key={cat.id} category={cat} />
          ))}
        </div>
      </div>
    </div>
  );
}
