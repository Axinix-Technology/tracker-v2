import React from 'react';
import {
  Zap,
  ShieldCheck,
  FileText,
  Layers,
  Smartphone,
  Lock,
  Printer,
  RefreshCw,
  Building,
  TrendingUp,
} from 'lucide-react';

const CAPABILITIES = [
  { icon: Zap, label: 'Sub-Second POS Checkout', tag: 'Fast' },
  { icon: ShieldCheck, label: '99.99% Cloud Uptime SLA', tag: 'Enterprise' },
  { icon: FileText, label: 'Automated GST & E-Way Invoicing', tag: 'Compliant' },
  { icon: Building, label: 'Multi-Branch Inventory Sync', tag: 'Unified' },
  { icon: Smartphone, label: 'Mobile Barcode & RFID Scanners', tag: 'Hardware' },
  { icon: Lock, label: 'Encrypted Daily Cloud Backups', tag: 'Security' },
  { icon: Printer, label: 'ESC/POS Thermal Printing Drivers', tag: 'Hardware' },
  { icon: RefreshCw, label: 'Automated FIFO Expiry Tracking', tag: 'Automated' },
  { icon: Layers, label: 'Role-Based Access Control (RBAC)', tag: 'Security' },
  { icon: TrendingUp, label: 'Executive BI Analytics', tag: 'Intelligence' },
];

export function CapabilitiesMarquee() {
  // Duplicate array for seamless infinite looping
  const items = [...CAPABILITIES, ...CAPABILITIES];

  return (
    <div className="w-full py-4 bg-[#061126]/40 dark:bg-[#040A18]/60 border-y border-white/10 overflow-hidden relative select-none">
      {/* Left/Right Edge Gradient Fades for Smooth Appearance */}
      <div className="absolute left-0 top-0 bottom-0 w-20 bg-gradient-to-r from-background to-transparent z-10 pointer-events-none"></div>
      <div className="absolute right-0 top-0 bottom-0 w-20 bg-gradient-to-l from-background to-transparent z-10 pointer-events-none"></div>

      <div className="animate-marquee flex items-center gap-4">
        {items.map((item, idx) => {
          const Icon = item.icon;
          return (
            <div
              key={idx}
              className="flex items-center gap-2.5 px-4 py-2 rounded-full bg-white/5 dark:bg-white/5 border border-white/10 hover:border-gold/50 backdrop-blur-sm transition-all whitespace-nowrap cursor-pointer group"
            >
              <div className="w-6 h-6 rounded-full bg-gold/15 text-gold flex items-center justify-center shrink-0 group-hover:scale-110 transition-transform">
                <Icon size={13} />
              </div>
              <span className="text-xs font-semibold text-slate-800 dark:text-slate-200 group-hover:text-gold transition-colors">
                {item.label}
              </span>
              <span className="text-[9px] px-1.5 py-0.2 rounded bg-white/10 text-gold font-mono uppercase tracking-wider">
                {item.tag}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

