import React, { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import { ANNOUNCEMENTS } from '../api/data';

export function AnnouncementBar() {
  const [index, setIndex] = useState(0);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    if (dismissed) return;
    const timer = setInterval(() => {
      setIndex(prev => (prev + 1) % ANNOUNCEMENTS.length);
    }, 4500);
    return () => clearInterval(timer);
  }, [dismissed]);

  if (dismissed) return null;

  return (
    <aside aria-label="Announcement" className="bg-[#050D1E] border-b border-white/10 py-1.5 px-4 text-center text-[11px] tracking-wider text-gold font-medium select-none overflow-hidden relative">
      <div className="max-w-[1600px] mx-auto px-4 sm:px-8 lg:px-12 xl:px-16 flex items-center justify-center gap-2">
        <span className="w-1.5 h-1.5 rounded-full bg-gold animate-pulse"></span>
        <p className="transition-all duration-500 ease-in-out transform">
          {ANNOUNCEMENTS[index]}
        </p>
      </div>

      <button
        onClick={() => setDismissed(true)}
        className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white p-0.5 rounded transition-colors"
        aria-label="Dismiss banner"
      >
        <X size={12} />
      </button>
    </aside>
  );
}
