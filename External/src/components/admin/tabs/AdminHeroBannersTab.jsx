import React, { useState, useEffect } from 'react';
import { Sparkles, Save, Edit, Layers, Compass, CheckCircle2 } from 'lucide-react';
import { apiClient } from '../../../api/client';
import { useToast } from '../../../context/ToastContext';

export function AdminHeroBannersTab() {
  const [loading, setLoading] = useState(true);
  const [savingKey, setSavingKey] = useState(null);
  const [sections, setSections] = useState({});
  const { addToast } = useToast();

  const fetchSections = async () => {
    setLoading(true);
    try {
      const res = await apiClient.populateRead('site_section_content');
      const list = res.data?.data || [];
      const map = {};
      list.forEach((s) => {
        map[s.section_key] = s;
      });
      setSections(map);
    } catch (err) {
      console.error('Failed to load site section content:', err);
      addToast('Failed to load banners from database', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSections();
  }, []);

  const handleFieldChange = (sectionKey, field, val) => {
    setSections((prev) => ({
      ...prev,
      [sectionKey]: {
        ...(prev[sectionKey] || { section_key: sectionKey }),
        [field]: val,
      },
    }));
  };

  const handleNestedChange = (sectionKey, path, val) => {
    setSections((prev) => {
      const sec = prev[sectionKey] || { section_key: sectionKey, content: {} };
      const content = { ...(sec.content || {}) };
      content[path] = val;
      return {
        ...prev,
        [sectionKey]: {
          ...sec,
          content,
        },
      };
    });
  };

  const saveSection = async (sectionKey) => {
    setSavingKey(sectionKey);
    try {
      const data = sections[sectionKey];
      if (data?.id) {
        await apiClient.populateUpdate('site_section_content', data.id, data);
      } else {
        await apiClient.populateCreate('site_section_content', data);
      }
      addToast(`Section '${sectionKey}' saved successfully!`, 'success');
      fetchSections();
    } catch (err) {
      addToast(err.message || 'Failed to save section', 'error');
    } finally {
      setSavingKey(null);
    }
  };

  if (loading) {
    return <div className="py-12 text-center text-slate-400 text-sm">Loading Site Content Banners...</div>;
  }

  const hero = sections['home_hero'] || {};
  const cta = sections['home_cta'] || {};
  const footer = sections['footer_meta'] || {};

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      {/* 1. Home Hero Banner */}
      <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gold/15 text-gold flex items-center justify-center">
              <Sparkles size={16} />
            </div>
            <div>
              <h3 className="font-semibold text-sm text-white">Homepage Hero Banner</h3>
              <p className="text-xs text-slate-400">The primary headline and value proposition visitors see first.</p>
            </div>
          </div>
          <button
            onClick={() => saveSection('home_hero')}
            disabled={savingKey === 'home_hero'}
            className="px-4 py-1.5 text-xs font-semibold text-slate-950 bg-gold hover:bg-gold-hover rounded-lg transition-colors flex items-center gap-1.5 disabled:opacity-50"
          >
            <Save size={13} />
            {savingKey === 'home_hero' ? 'Saving...' : 'Save Hero'}
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Eyebrow Badge Text</label>
            <input
              type="text"
              value={hero.badge || ''}
              onChange={(e) => handleFieldChange('home_hero', 'badge', e.target.value)}
              className="w-full px-3 py-1.5 text-xs bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-gold"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Gradient Highlight Text</label>
            <input
              type="text"
              value={hero.content?.highlight || ''}
              onChange={(e) => handleNestedChange('home_hero', 'highlight', e.target.value)}
              className="w-full px-3 py-1.5 text-xs bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-gold"
            />
          </div>

          <div className="sm:col-span-2">
            <label className="block text-xs font-medium text-slate-300 mb-1">Main Headline</label>
            <input
              type="text"
              value={hero.title || ''}
              onChange={(e) => handleFieldChange('home_hero', 'title', e.target.value)}
              className="w-full px-3 py-1.5 text-xs bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-gold font-medium"
            />
          </div>

          <div className="sm:col-span-2">
            <label className="block text-xs font-medium text-slate-300 mb-1">Subtitle / Descriptive Paragraph</label>
            <textarea
              rows={3}
              value={hero.subtitle || ''}
              onChange={(e) => handleFieldChange('home_hero', 'subtitle', e.target.value)}
              className="w-full px-3 py-1.5 text-xs bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-gold"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Primary CTA Button Label</label>
            <input
              type="text"
              value={hero.content?.primaryAction?.label || ''}
              onChange={(e) => {
                const prev = hero.content?.primaryAction || {};
                handleNestedChange('home_hero', 'primaryAction', { ...prev, label: e.target.value });
              }}
              className="w-full px-3 py-1.5 text-xs bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-gold"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Secondary CTA Button Label</label>
            <input
              type="text"
              value={hero.content?.secondaryAction?.label || ''}
              onChange={(e) => {
                const prev = hero.content?.secondaryAction || {};
                handleNestedChange('home_hero', 'secondaryAction', { ...prev, label: e.target.value });
              }}
              className="w-full px-3 py-1.5 text-xs bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-gold"
            />
          </div>
        </div>
      </div>

      {/* 2. Global CTA Banner */}
      <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-emerald-500/15 text-emerald-400 flex items-center justify-center">
              <CheckCircle2 size={16} />
            </div>
            <div>
              <h3 className="font-semibold text-sm text-white">Call-To-Action (CTA) Banner</h3>
              <p className="text-xs text-slate-400">Bottom conversion banner displayed across solutions and home.</p>
            </div>
          </div>
          <button
            onClick={() => saveSection('home_cta')}
            disabled={savingKey === 'home_cta'}
            className="px-4 py-1.5 text-xs font-semibold text-slate-950 bg-gold hover:bg-gold-hover rounded-lg transition-colors flex items-center gap-1.5 disabled:opacity-50"
          >
            <Save size={13} />
            {savingKey === 'home_cta' ? 'Saving...' : 'Save CTA'}
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="sm:col-span-2">
            <label className="block text-xs font-medium text-slate-300 mb-1">Banner Headline</label>
            <input
              type="text"
              value={cta.title || ''}
              onChange={(e) => handleFieldChange('home_cta', 'title', e.target.value)}
              className="w-full px-3 py-1.5 text-xs bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-gold"
            />
          </div>

          <div className="sm:col-span-2">
            <label className="block text-xs font-medium text-slate-300 mb-1">Banner Description</label>
            <textarea
              rows={2}
              value={cta.subtitle || ''}
              onChange={(e) => handleFieldChange('home_cta', 'subtitle', e.target.value)}
              className="w-full px-3 py-1.5 text-xs bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-gold"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Button 1 Label</label>
            <input
              type="text"
              value={cta.content?.primaryAction?.label || ''}
              onChange={(e) => {
                const prev = cta.content?.primaryAction || {};
                handleNestedChange('home_cta', 'primaryAction', { ...prev, label: e.target.value });
              }}
              className="w-full px-3 py-1.5 text-xs bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-gold"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Button 2 Label</label>
            <input
              type="text"
              value={cta.content?.secondaryAction?.label || ''}
              onChange={(e) => {
                const prev = cta.content?.secondaryAction || {};
                handleNestedChange('home_cta', 'secondaryAction', { ...prev, label: e.target.value });
              }}
              className="w-full px-3 py-1.5 text-xs bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-gold"
            />
          </div>
        </div>
      </div>

      {/* 3. Footer Meta */}
      <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div>
            <h3 className="font-semibold text-sm text-white">Footer Copyright & Operational Hours</h3>
            <p className="text-xs text-slate-400">Shown in the global footer on all pages.</p>
          </div>
          <button
            onClick={() => saveSection('footer_meta')}
            disabled={savingKey === 'footer_meta'}
            className="px-4 py-1.5 text-xs font-semibold text-slate-950 bg-gold hover:bg-gold-hover rounded-lg transition-colors flex items-center gap-1.5 disabled:opacity-50"
          >
            <Save size={13} />
            {savingKey === 'footer_meta' ? 'Saving...' : 'Save Footer'}
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="sm:col-span-2">
            <label className="block text-xs font-medium text-slate-300 mb-1">Copyright Line</label>
            <input
              type="text"
              value={footer.content?.copyright || ''}
              onChange={(e) => handleNestedChange('footer_meta', 'copyright', e.target.value)}
              className="w-full px-3 py-1.5 text-xs bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-gold"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Support Hotline</label>
            <input
              type="text"
              value={footer.content?.supportHotline || ''}
              onChange={(e) => handleNestedChange('footer_meta', 'supportHotline', e.target.value)}
              className="w-full px-3 py-1.5 text-xs bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-gold"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Office Hours</label>
            <input
              type="text"
              value={footer.content?.officeHours || ''}
              onChange={(e) => handleNestedChange('footer_meta', 'officeHours', e.target.value)}
              className="w-full px-3 py-1.5 text-xs bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-gold"
            />
          </div>
        </div>
      </div>
    </div>
  );
}

