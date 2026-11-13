import React from 'react';
import { Layers, Sliders, ShieldCheck, Zap, HeartHandshake, Sparkles } from 'lucide-react';
import { WHY_CHOOSE_US } from '../api/data';
import { cn } from '../utils/cn';
import { StaggerContainer, StaggerItem } from './motion';

const PILLAR_ICONS = [Layers, Zap, Sliders, ShieldCheck];

export function WhyChooseUsGrid({ items = WHY_CHOOSE_US.slice(0, 4), className = '' }) {
  return (
    <StaggerContainer
      staggerDelay={0.1}
      className={cn('grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6', className)}
    >
      {items.map((item, idx) => {
        const Icon = PILLAR_ICONS[idx % PILLAR_ICONS.length] || Sparkles;
        return (
          <StaggerItem
            key={idx}
            direction="pop"
            className="bg-card/80 backdrop-blur-md border border-border/70 rounded-2xl p-6 hover:border-gold/60 transition-all hover:-translate-y-1 hover:shadow-lg group"
          >
            <div className="w-11 h-11 rounded-xl bg-gold/15 text-gold flex items-center justify-center font-bold text-sm mb-4 border border-gold/30 group-hover:scale-110 transition-transform">
              <Icon size={20} />
            </div>
            <h3 className="text-base font-serif font-bold text-foreground group-hover:text-gold transition-colors mb-2">
              {item.title}
            </h3>
            <p className="text-xs text-muted leading-relaxed">
              {item.description}
            </p>
          </StaggerItem>
        );
      })}
    </StaggerContainer>
  );
}

export default WhyChooseUsGrid;
