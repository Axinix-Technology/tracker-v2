import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  ShieldCheck, ExternalLink, LogOut, KeyRound,
  Database, RefreshCw, Sparkles, CheckCircle2
} from 'lucide-react';
import { useAdminAuth } from '../../context/AdminAuthContext';
import { ChangePasswordModal } from './ChangePasswordModal';

export function AdminHeader({ onRefreshAll, isRefreshing }) {
  const { user, logout } = useAdminAuth();
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/admin/login', { replace: true });
  };

  return (
    <>
      <header className="sticky top-0 z-40 w-full border-b border-slate-800 bg-slate-950/80 backdrop-blur-md px-4 sm:px-8 py-3 flex items-center justify-between text-slate-200">
        <div className="flex items-center gap-3">
          <Link to="/admin" className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-gold to-gold-hover flex items-center justify-center text-slate-950 font-bold shadow-md shadow-gold/20">
              A
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-semibold text-sm tracking-wide text-white">AXINIX CMS</span>
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                  LIVE DB
                </span>
              </div>
              <p className="text-[11px] text-slate-400">Content Management Portal</p>
            </div>
          </Link>
        </div>

        <div className="flex items-center gap-2 sm:gap-3">
          {onRefreshAll && (
            <button
              onClick={onRefreshAll}
              disabled={isRefreshing}
              title="Refresh data from database"
              className="px-2.5 py-1.5 text-xs text-slate-300 hover:text-white bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded-lg flex items-center gap-1.5 transition-colors disabled:opacity-50"
            >
              <RefreshCw size={13} className={isRefreshing ? 'animate-spin text-gold' : ''} />
              <span className="hidden sm:inline">Sync DB</span>
            </button>
          )}

          <a
            href="/"
            target="_blank"
            rel="noopener noreferrer"
            className="px-2.5 py-1.5 text-xs text-slate-300 hover:text-white bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded-lg flex items-center gap-1.5 transition-colors"
          >
            <ExternalLink size={13} />
            <span className="hidden sm:inline">View Public Website</span>
          </a>

          <div className="h-4 w-px bg-slate-800 mx-1 hidden sm:block"></div>

          <button
            onClick={() => setShowPasswordModal(true)}
            title="Change password"
            className="px-2.5 py-1.5 text-xs text-slate-300 hover:text-gold bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded-lg flex items-center gap-1.5 transition-colors"
          >
            <KeyRound size={13} />
            <span className="hidden sm:inline">Change Password</span>
          </button>

          <button
            onClick={handleLogout}
            title="Sign out"
            className="px-2.5 py-1.5 text-xs text-rose-400 hover:text-rose-300 bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/30 rounded-lg flex items-center gap-1.5 transition-colors"
          >
            <LogOut size={13} />
            <span className="hidden sm:inline">Sign Out</span>
          </button>
        </div>
      </header>

      <ChangePasswordModal
        isOpen={showPasswordModal}
        onClose={() => setShowPasswordModal(false)}
      />
    </>
  );
}

