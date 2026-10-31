import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Compass, Home, ArrowLeft } from 'lucide-react';
import { MODULES } from '../constants/uiTokens';

export default function NotFoundPage() {
  const navigate = useNavigate();

  return (
    <div
      className="min-h-[80vh] flex items-center justify-center p-6 text-center animate-fade-in"
      data-module={MODULES.project.id}
    >
      <div className="max-w-md w-full bg-surface border border-hairline rounded-tracker-lg p-8 shadow-sm space-y-6">
        <div className="w-16 h-16 mx-auto rounded-full bg-surface-1 border border-hairline flex items-center justify-center text-[var(--brand-solid)]">
          <Compass size={32} strokeWidth={1.75} />
        </div>

        <div className="space-y-2">
          <span className="inline-block px-3 py-1 text-xs font-semibold uppercase tracking-wider text-[var(--brand-solid)] bg-surface-1 rounded-full border border-hairline">
            Error 404
          </span>
          <h1 className="text-2xl font-bold tracking-tight text-ink">
            Page Not Found
          </h1>
          <p className="text-sm text-ink-muted leading-relaxed">
            The screen or resource you are looking for does not exist, has been archived, or you may not have sufficient role permissions to view it.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row gap-3 justify-center pt-2">
          <button
            type="button"
            onClick={() => navigate(-1)}
            className="inline-flex items-center justify-center gap-2 px-4 py-2 text-xs font-semibold rounded-tracker-md bg-surface-1 border border-hairline text-ink hover:bg-surface-2 transition-colors cursor-pointer"
          >
            <ArrowLeft size={14} />
            Go Back
          </button>
          <button
            type="button"
            onClick={() => navigate('/dashboard')}
            className="inline-flex items-center justify-center gap-2 px-4 py-2 text-xs font-semibold rounded-tracker-md bg-[var(--brand-solid)] text-white hover:opacity-90 transition-opacity cursor-pointer shadow-xs"
          >
            <Home size={14} />
            Dashboard
          </button>
        </div>
      </div>
    </div>
  );
}

