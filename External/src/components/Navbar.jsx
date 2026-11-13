import React from 'react';
import { Link } from 'react-router-dom';
import { Sun, Moon } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';
import { Button } from './ui/Button';

/**
 * Navbar Header
 * Displays the AXINIX brand logo on the left and theme toggle + Contact Us on the right.
 * The middle tab navigation links have been removed in favor of the in-page destination cards.
 */
export function Navbar() {
  const { isDark, toggleTheme } = useTheme();

  return (
    <header className="sticky top-0 z-40 bg-[#061126]/90 backdrop-blur-md text-white border-b border-white/10 transition-colors shadow-lg">
      <div className="max-w-[1600px] mx-auto px-4 sm:px-8 lg:px-12 xl:px-16">
        <div className="flex items-center justify-between h-16 gap-6">
          {/* Brand Logo with 4-color gradient */}
          <Link to="/" className="flex items-center gap-2.5 group shrink-0">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-[#123E87] via-[#0E77C6] via-[#1CC7F4] to-[#05B292] p-[1.5px] flex items-center justify-center shadow-md shadow-[#0E77C6]/30 group-hover:scale-105 transition-transform">
              <div className="w-full h-full bg-[#061126] rounded-[10px] flex items-center justify-center">
                <span className="font-serif font-black text-transparent bg-clip-text bg-gradient-to-r from-[#1CC7F4] to-[#05B292] text-lg">A</span>
              </div>
            </div>
            <span className="font-sans font-bold text-sm sm:text-base tracking-wider text-white group-hover:text-gold transition-colors">
              AXINIX <span className="text-gold font-bold">TECHNOLOGIES</span>
            </span>
          </Link>

          {/* Right Actions: Theme Toggle & Contact Us CTA */}
          <div className="flex items-center gap-3">
            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
              className="p-2 rounded-lg text-slate-300 hover:text-gold hover:bg-white/10 transition-colors focus:outline-none"
              aria-label="Toggle theme"
            >
              {isDark ? <Sun size={17} /> : <Moon size={17} />}
            </button>

            {/* Primary Contact Us Button */}
            <Link to="/contact">
              <Button size="sm" variant="gold" className="font-semibold shadow-gold/20 text-xs px-4">
                <span>Contact Us</span>
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </header>
  );
}
