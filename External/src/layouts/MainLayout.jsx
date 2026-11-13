import React, { useState, useEffect } from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { ArrowUp, Calendar } from 'lucide-react';
import { AnnouncementBar } from '../components/AnnouncementBar';
import { Navbar } from '../components/Navbar';
import { Footer } from '../components/Footer';
import { ToastContainer } from '../components/ToastContainer';
import { PageTransition, PagePreloader } from '../components/motion';

export function MainLayout() {
  const [showTopBtn, setShowTopBtn] = useState(false);
  const location = useLocation();

  useEffect(() => {
    // Scroll to top on route change
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [location.pathname, location.search]);

  useEffect(() => {
    const handleScroll = () => {
      setShowTopBtn(window.scrollY > 450);
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const isAdminRoute = location.pathname.startsWith('/admin');

  if (isAdminRoute) {
    return (
      <div className="min-h-screen flex flex-col bg-background text-foreground transition-colors relative selection:bg-gold/30 selection:text-gold-light">
        <Outlet />
        <ToastContainer />
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-background text-foreground transition-colors relative selection:bg-gold/30 selection:text-gold-light overflow-x-hidden">
      <PagePreloader />
      {/* Brand logo multi-color ambient mesh that illuminates the entire page in dark mode */}
      <div className="brand-page-glow fixed inset-0 pointer-events-none z-0 overflow-hidden" aria-hidden="true">
        {/* Top-Right: Electric Cyan & Aqua Teal ambient light (Apex & Ribbon of logo) */}
        <div className="absolute -top-32 right-[-5%] w-[800px] h-[800px] rounded-full bg-gradient-to-br from-[#1CC7F4]/16 via-[#05B292]/14 to-transparent blur-[110px]"></div>

        {/* Mid-Left: Cerulean Blue & Deep Cobalt ambient glow (Stem of logo) */}
        <div className="absolute top-[28%] -left-32 w-[720px] h-[720px] rounded-full bg-gradient-to-tr from-[#123E87]/28 via-[#0E77C6]/18 to-transparent blur-[120px]"></div>

        {/* Lower-Right: Aqua Teal & Cyan ambient accent (Chevron of logo) */}
        <div className="absolute top-[60%] -right-28 w-[650px] h-[650px] rounded-full bg-gradient-to-tl from-[#05B292]/14 via-[#1CC7F4]/12 to-transparent blur-[110px]"></div>

        {/* Bottom-Center: Deep Cobalt & Royal Blue ambient anchor */}
        <div className="absolute -bottom-40 left-[15%] w-[850px] h-[650px] rounded-full bg-gradient-to-t from-[#123E87]/24 via-[#0E77C6]/14 to-transparent blur-[130px]"></div>
      </div>

      <div className="relative z-10 flex flex-col min-h-screen">
        <AnnouncementBar />
        <Navbar />

        <main className="flex-1 w-full">
          <PageTransition>
            <Outlet />
          </PageTransition>
        </main>

        <Footer />
        <ToastContainer />
      </div>

      {/* Back to top button */}
      {showTopBtn && (
        <button
          onClick={scrollToTop}
          aria-label="Back to top"
          className="fixed right-5 bottom-6 z-30 w-10 h-10 rounded-full bg-gold hover:bg-gold-hover text-deep flex items-center justify-center shadow-xl transition-all hover:scale-110 active:scale-95 focus:outline-none"
        >
          <ArrowUp size={18} />
        </button>
      )}
    </div>
  );
}
