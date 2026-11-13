import React, { useState } from 'react';
import {
  Building2, Sparkles, Layers, Code2, Building,
  Trophy, TrendingUp, Star, Mail, LayoutGrid, Columns
} from 'lucide-react';
import { AdminAuthGuard } from '../../components/admin/AdminAuthGuard';
import { AdminHeader } from '../../components/admin/AdminHeader';
import { AdminProfileTab } from '../../components/admin/tabs/AdminProfileTab';
import { AdminHeroBannersTab } from '../../components/admin/tabs/AdminHeroBannersTab';
import { AdminFeatureCardsTab } from '../../components/admin/tabs/AdminFeatureCardsTab';
import { AdminSolutionsTab } from '../../components/admin/tabs/AdminSolutionsTab';
import { AdminServicesTab } from '../../components/admin/tabs/AdminServicesTab';
import { AdminIndustriesTab } from '../../components/admin/tabs/AdminIndustriesTab';
import { AdminPortfolioTab } from '../../components/admin/tabs/AdminPortfolioTab';
import { AdminStatsAnnouncementsTab } from '../../components/admin/tabs/AdminStatsAnnouncementsTab';
import { AdminTestimonialsTab } from '../../components/admin/tabs/AdminTestimonialsTab';
import { AdminInquiriesTab } from '../../components/admin/tabs/AdminInquiriesTab';

const TABS = [
  { id: 'profile', label: 'Company Profile', icon: Building2 },
  { id: 'hero', label: 'Banners & Hero', icon: Sparkles },
  { id: 'feature-cards', label: 'Feature Cards', icon: Columns },
  { id: 'solutions', label: 'Solutions', icon: Layers },
  { id: 'services', label: 'Services', icon: Code2 },
  { id: 'industries', label: 'Industries', icon: Building },
  { id: 'portfolio', label: 'Portfolio', icon: Trophy },
  { id: 'stats', label: 'Stats & Ticker', icon: TrendingUp },
  { id: 'testimonials', label: 'Reviews', icon: Star },
  { id: 'inquiries', label: 'Inquiries Inbox', icon: Mail },
];

export default function AdminDashboardPage() {
  const [activeTab, setActiveTab] = useState('profile');
  const [refreshKey, setRefreshKey] = useState(0);

  const handleRefresh = () => {
    setRefreshKey((k) => k + 1);
  };

  return (
    <AdminAuthGuard>
      <div className="min-h-screen bg-[#070e1c] text-slate-100 flex flex-col">
        <AdminHeader onRefreshAll={handleRefresh} />

        {/* Tab Navigation */}
        <div className="border-b border-slate-800 bg-slate-950/40 sticky top-[57px] z-30 px-4 sm:px-8">
          <div className="max-w-6xl mx-auto flex items-center gap-1 overflow-x-auto scrollbar-none py-2">
            {TABS.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-3.5 py-2 text-xs font-medium rounded-xl flex items-center gap-2 whitespace-nowrap transition-all ${
                    isActive
                      ? 'bg-gold text-slate-950 font-semibold shadow-md shadow-gold/20'
                      : 'text-slate-400 hover:text-white hover:bg-slate-900'
                  }`}
                >
                  <Icon size={14} />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Tab Content Body */}
        <main className="flex-1 p-4 sm:p-8 max-w-6xl mx-auto w-full" key={refreshKey}>
          {activeTab === 'profile' && <AdminProfileTab />}
          {activeTab === 'hero' && <AdminHeroBannersTab />}
          {activeTab === 'feature-cards' && <AdminFeatureCardsTab />}
          {activeTab === 'solutions' && <AdminSolutionsTab />}
          {activeTab === 'services' && <AdminServicesTab />}
          {activeTab === 'industries' && <AdminIndustriesTab />}
          {activeTab === 'portfolio' && <AdminPortfolioTab />}
          {activeTab === 'stats' && <AdminStatsAnnouncementsTab />}
          {activeTab === 'testimonials' && <AdminTestimonialsTab />}
          {activeTab === 'inquiries' && <AdminInquiriesTab />}
        </main>
      </div>
    </AdminAuthGuard>
  );
}

