import React from 'react';
import { Link } from 'react-router-dom';
import { Home, Compass } from 'lucide-react';
import { Button } from '../../components/ui/Button';

export default function NotFoundPage() {
  return (
    <div className="py-24 px-4 sm:px-6 lg:px-8 text-center max-w-xl mx-auto space-y-6">
      <div className="w-20 h-20 rounded-2xl bg-gold/15 text-gold flex items-center justify-center mx-auto border border-gold/30">
        <Compass size={40} />
      </div>

      <div className="space-y-2">
        <span className="text-gold font-mono text-sm font-semibold uppercase tracking-widest">
          Error 404
        </span>
        <h1 className="text-3xl sm:text-4xl font-serif font-bold text-foreground">
          Page Not Located
        </h1>
        <p className="text-xs sm:text-sm text-muted leading-relaxed">
          The destination route you requested does not exist or may have been repositioned.
        </p>
      </div>

      <div className="flex flex-col sm:flex-row justify-center gap-4 pt-4">
        <Link to="/">
          <Button variant="gold" size="md" className="w-full sm:w-auto gap-2">
            <Home size={15} />
            <span>Return to Home</span>
          </Button>
        </Link>
        <Link to="/solutions">
          <Button variant="outline" size="md" className="w-full sm:w-auto">
            Browse Solutions
          </Button>
        </Link>
      </div>
    </div>
  );
}

