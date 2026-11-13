import React, { useState, useEffect } from 'react';
import { Star, ChevronLeft, ChevronRight, Quote } from 'lucide-react';
import { TESTIMONIALS } from '../api/data';
import { cn } from '../utils/cn';

export function TestimonialSlider({ testimonials = TESTIMONIALS, autoPlay = true, className = '' }) {
  const [active, setActive] = useState(0);
  const [isPaused, setIsPaused] = useState(false);

  useEffect(() => {
    if (!autoPlay || isPaused || testimonials.length <= 1) return;
    const timer = setInterval(() => {
      setActive(prev => (prev + 1) % testimonials.length);
    }, 5500);
    return () => clearInterval(timer);
  }, [autoPlay, isPaused, testimonials.length]);

  if (!testimonials || testimonials.length === 0) return null;
  const current = testimonials[active];

  const handlePrev = () => {
    setActive(prev => (prev === 0 ? testimonials.length - 1 : prev - 1));
  };

  const handleNext = () => {
    setActive(prev => (prev + 1) % testimonials.length);
  };

  return (
    <div
      className={cn(
        'bg-card/90 backdrop-blur-md border border-border/80 rounded-3xl p-8 sm:p-12 shadow-2xl relative min-h-[260px] flex flex-col justify-between max-w-4xl mx-auto transition-all',
        className
      )}
      onMouseEnter={() => setIsPaused(true)}
      onMouseLeave={() => setIsPaused(false)}
    >
      {/* Decorative Quote Icon in corner */}
      <div className="absolute top-6 right-8 text-gold/15 pointer-events-none">
        <Quote size={50} />
      </div>

      <div>
        {/* Star Rating */}
        <div className="flex justify-center gap-1.5 text-gold mb-5">
          {[...Array(5)].map((_, i) => (
            <Star key={i} size={18} fill="currentColor" />
          ))}
        </div>

        {/* Active Quote with smooth fade */}
        <p key={active} className="text-base sm:text-xl text-slate-900 dark:text-white font-serif italic leading-relaxed text-center mb-6 max-w-2xl mx-auto animate-in fade-in duration-200">
          "{current.quote}"
        </p>

        {/* Client Bio */}
        <div className="text-center space-y-1">
          <b className="text-sm sm:text-base font-bold text-foreground block">
            {current.client}
          </b>
          <div className="text-xs text-muted font-medium">
            {current.role} {current.location ? `· ${current.location}` : ''}
          </div>
        </div>
      </div>

      {/* Navigation Controls: Arrows & Indicators */}
      <div className="flex items-center justify-between pt-8 border-t border-border/40 mt-6">
        <button
          type="button"
          onClick={handlePrev}
          className="w-9 h-9 rounded-full bg-white/5 hover:bg-gold/20 hover:text-gold text-slate-400 flex items-center justify-center transition-all border border-border/60"
          aria-label="Previous testimonial"
        >
          <ChevronLeft size={18} />
        </button>

        {/* Dot Indicators */}
        <div className="flex items-center gap-2">
          {testimonials.map((_, i) => (
            <button
              key={i}
              type="button"
              onClick={() => setActive(i)}
              className={`h-2 rounded-full transition-all ${
                active === i ? 'bg-gold w-7' : 'bg-muted/40 hover:bg-muted w-2'
              }`}
              aria-label={`Go to testimonial ${i + 1}`}
            />
          ))}
        </div>

        <button
          type="button"
          onClick={handleNext}
          className="w-9 h-9 rounded-full bg-white/5 hover:bg-gold/20 hover:text-gold text-slate-400 flex items-center justify-center transition-all border border-border/60"
          aria-label="Next testimonial"
        >
          <ChevronRight size={18} />
        </button>
      </div>
    </div>
  );
}
