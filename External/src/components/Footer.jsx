import React from 'react';
import { Link } from 'react-router-dom';
import { SOLUTIONS, INDUSTRIES, SERVICES } from '../api/data';
import { useSettings } from '../context/SettingsContext';

export function Footer() {
  const { settings } = useSettings();

  return (
    <footer className="bg-[#050D1E] border-t border-border/80 text-muted text-xs pt-14 pb-8 transition-colors relative overflow-hidden">
      {/* Subtle brand color ambient glows */}
      <div className="absolute bottom-0 right-0 w-[450px] h-[260px] rounded-full bg-gradient-to-tl from-[#05B292]/12 via-[#1CC7F4]/10 to-transparent blur-3xl pointer-events-none"></div>
      <div className="absolute top-0 left-0 w-[450px] h-[260px] rounded-full bg-gradient-to-br from-[#123E87]/20 via-[#0E77C6]/15 to-transparent blur-3xl pointer-events-none"></div>

      <div className="max-w-[1600px] mx-auto px-4 sm:px-8 lg:px-12 xl:px-16 relative z-10">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8 lg:gap-10 pb-12 border-b border-border/40">
          {/* Brand Info */}
          <div className="lg:col-span-2 space-y-4">
            <Link to="/" className="inline-block">
              <span className="font-sans font-bold text-lg tracking-widest text-foreground">
                AXINIX <b className="text-gold font-bold">TECHNOLOGIES</b>
              </span>
            </Link>
            <p className="text-sm text-muted/90 max-w-sm leading-relaxed">
              One Partner. Every Business Solution. Intelligent ERP, POS, modern web applications, and digital systems engineered for every industry.
            </p>
            <div className="pt-2 flex items-center gap-3">
              {settings.fb && (
                <a href={settings.fb} target="_blank" rel="noopener noreferrer" className="hover:text-gold transition-colors">
                  Facebook
                </a>
              )}
              {settings.ig && (
                <a href={settings.ig} target="_blank" rel="noopener noreferrer" className="hover:text-gold transition-colors">
                  Instagram
                </a>
              )}
              {settings.li && (
                <a href={settings.li} target="_blank" rel="noopener noreferrer" className="hover:text-gold transition-colors">
                  LinkedIn
                </a>
              )}
              {settings.yt && (
                <a href={settings.yt} target="_blank" rel="noopener noreferrer" className="hover:text-gold transition-colors">
                  YouTube
                </a>
              )}
            </div>
            <p className="text-xs text-muted/70 pt-1">
              Direct Contact: {settings.phone} · {settings.email}
            </p>
          </div>

          {/* Solutions Column */}
          <div>
            <h4 className="font-sans font-semibold text-foreground text-sm uppercase tracking-wider mb-3">
              Solutions
            </h4>
            <ul className="space-y-2">
              {SOLUTIONS.slice(0, 5).map(s => (
                <li key={s.id}>
                  <Link to={`/solutions/${s.id}`} className="hover:text-gold transition-colors">
                    {s.title}
                  </Link>
                </li>
              ))}
              <li>
                <Link to="/solutions" className="text-gold hover:underline font-medium">
                  View all solutions →
                </Link>
              </li>
            </ul>
          </div>

          {/* Industries & Services Column */}
          <div>
            <h4 className="font-sans font-semibold text-foreground text-sm uppercase tracking-wider mb-3">
              Industries & Services
            </h4>
            <ul className="space-y-2">
              {INDUSTRIES.slice(0, 3).map(i => (
                <li key={i.id}>
                  <Link to={`/industries/${i.id}`} className="hover:text-gold transition-colors">
                    {i.name}
                  </Link>
                </li>
              ))}
              {SERVICES.slice(0, 2).map(srv => (
                <li key={srv.id}>
                  <Link to={`/services/${srv.id}`} className="hover:text-gold transition-colors">
                    {srv.title}
                  </Link>
                </li>
              ))}
              <li>
                <Link to="/industries" className="text-gold hover:underline font-medium">
                  All Industries & Services →
                </Link>
              </li>
            </ul>
          </div>

          {/* Company Column */}
          <div>
            <h4 className="font-sans font-semibold text-foreground text-sm uppercase tracking-wider mb-3">
              Company
            </h4>
            <ul className="space-y-2">
              <li>
                <Link to="/about" className="hover:text-gold transition-colors">
                  About AXINIX
                </Link>
              </li>
              <li>
                <Link to="/products" className="hover:text-gold transition-colors">
                  Products Catalog
                </Link>
              </li>
              <li>
                <Link to="/careers" className="hover:text-gold transition-colors flex items-center gap-1.5">
                  <span>Careers</span>
                  <span className="px-1.5 py-0.2 rounded-full text-[9px] bg-emerald-500/20 text-emerald-400 font-bold">
                    Hiring
                  </span>
                </Link>
              </li>
              <li>
                <Link to="/contact" className="hover:text-gold transition-colors">
                  Contact Our Team
                </Link>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-6 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-muted/80">
          <p>© {new Date().getFullYear()} AXINIX TECHNOLOGIES. All rights reserved.</p>
          <div className="flex items-center gap-6">
            <Link to="/legal" className="hover:text-gold transition-colors">
              Privacy Policy
            </Link>
            <Link to="/help-policies/terms" className="hover:text-gold transition-colors">
              Terms of Service
            </Link>
            <Link to="/help-policies/cookie-policy" className="hover:text-gold transition-colors">
              Cookie Policy
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
