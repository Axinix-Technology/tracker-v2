import React, { useState, useEffect } from 'react';
import { Plus, Edit2, Trash2, Eye, EyeOff, Sparkles, TrendingUp } from 'lucide-react';
import { apiClient } from '../../../api/client';
import { useToast } from '../../../context/ToastContext';
import { ItemEditModal } from '../ItemEditModal';

const STAT_FIELDS = [
  { name: 'label', label: 'Metric Label', required: true, placeholder: 'e.g. Businesses Served' },
  { name: 'value', label: 'Display Value / Count', required: true, placeholder: 'e.g. 150+' },
  { name: 'change', label: 'Badge / YoY Change', placeholder: 'e.g. +24% YoY or 100% on-time' },
  { name: 'order', label: 'Display Order', type: 'number' },
  { name: 'is_active', label: 'Published / Visible', type: 'switch', default: true },
];

const ANNOUNCEMENT_FIELDS = [
  { name: 'title', label: 'Announcement Ticker Text', required: true, placeholder: 'e.g. Transform Your Business with AXINIX.' },
  { name: 'link_url', label: 'Optional Action Link', placeholder: '/solutions or /contact' },
  { name: 'order', label: 'Display Order', type: 'number' },
  { name: 'is_active', label: 'Active', type: 'switch', default: true },
];

export function AdminStatsAnnouncementsTab() {
  const [stats, setStats] = useState([]);
  const [announcements, setAnnouncements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [modalType, setModalType] = useState('stat'); // 'stat' | 'announcement'
  const [selectedItem, setSelectedItem] = useState(null);
  const [isSaving, setIsSaving] = useState(false);
  const { addToast } = useToast();

  const fetchData = async () => {
    setLoading(true);
    try {
      const [resStats, resAnn] = await Promise.all([
        apiClient.populateRead('showcase_stat'),
        apiClient.populateRead('showcase_announcement'),
      ]);
      setStats(resStats.data?.data || []);
      setAnnouncements(resAnn.data?.data || []);
    } catch (err) {
      console.error(err);
      addToast('Failed to load stats & announcements', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleToggleStat = async (item) => {
    try {
      const updated = !item.is_active;
      await apiClient.populateUpdate('showcase_stat', item.id, { is_active: updated });
      addToast(`Stat '${item.label}' ${updated ? 'Published' : 'Hidden'}`, 'success');
      setStats(prev => prev.map(s => s.id === item.id ? { ...s, is_active: updated } : s));
    } catch (err) {
      addToast(err.message || 'Failed to update', 'error');
    }
  };

  const handleDeleteStat = async (id, label) => {
    if (!window.confirm(`Delete metric '${label}'?`)) return;
    try {
      await apiClient.populateDelete('showcase_stat', id);
      addToast(`Deleted '${label}'`, 'success');
      setStats(prev => prev.filter(s => s.id !== id));
    } catch (err) {
      addToast(err.message || 'Failed to delete', 'error');
    }
  };

  const handleToggleAnnouncement = async (item) => {
    try {
      const updated = !item.is_active;
      await apiClient.populateUpdate('showcase_announcement', item.id, { is_active: updated });
      addToast(`Announcement updated`, 'success');
      setAnnouncements(prev => prev.map(a => a.id === item.id ? { ...a, is_active: updated } : a));
    } catch (err) {
      addToast(err.message || 'Failed to update', 'error');
    }
  };

  const handleDeleteAnnouncement = async (id) => {
    if (!window.confirm('Delete this announcement?')) return;
    try {
      await apiClient.populateDelete('showcase_announcement', id);
      addToast('Deleted announcement', 'success');
      setAnnouncements(prev => prev.filter(a => a.id !== id));
    } catch (err) {
      addToast(err.message || 'Failed to delete', 'error');
    }
  };

  const handleSaveModal = async (formData) => {
    setIsSaving(true);
    const model = modalType === 'stat' ? 'showcase_stat' : 'showcase_announcement';
    try {
      if (formData.id) {
        await apiClient.populateUpdate(model, formData.id, formData);
        addToast('Saved successfully', 'success');
      } else {
        await apiClient.populateCreate(model, formData);
        addToast('Created successfully', 'success');
      }
      setModalOpen(false);
      fetchData();
    } catch (err) {
      addToast(err.message || 'Failed to save', 'error');
    } finally {
      setIsSaving(false);
    }
  };

  if (loading) {
    return <div className="py-12 text-center text-slate-400 text-sm">Loading Stats & Announcements...</div>;
  }

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* 1. Ticker Announcements */}
      <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div>
            <h3 className="font-semibold text-sm text-white">Top Bar Ticker Announcements</h3>
            <p className="text-xs text-slate-400">Animated banner text rotating at the very top of the site.</p>
          </div>
          <button
            onClick={() => {
              setModalType('announcement');
              setSelectedItem({ title: '', link_url: '', order: announcements.length + 1, is_active: true });
              setModalOpen(true);
            }}
            className="px-3 py-1.5 text-xs font-semibold text-slate-950 bg-gold hover:bg-gold-hover rounded-lg transition-colors flex items-center gap-1.5"
          >
            <Plus size={13} /> Add Announcement
          </button>
        </div>

        <div className="space-y-2">
          {announcements.map((ann, idx) => (
            <div
              key={ann.id}
              className={`p-3 rounded-lg border flex items-center justify-between gap-3 text-xs ${
                ann.is_active ? 'bg-slate-950/70 border-slate-800 text-slate-200' : 'bg-slate-950/30 border-slate-800/40 opacity-50'
              }`}
            >
              <div className="flex items-center gap-2 flex-1">
                <span className="font-mono text-[10px] text-slate-500">#{idx + 1}</span>
                <span className="font-medium text-white">{ann.title}</span>
                {ann.link_url && <span className="text-[10px] text-gold font-mono">({ann.link_url})</span>}
              </div>

              <div className="flex items-center gap-1">
                <button
                  onClick={() => handleToggleAnnouncement(ann)}
                  className={`p-1 rounded ${ann.is_active ? 'text-emerald-400' : 'text-slate-500'}`}
                >
                  {ann.is_active ? <Eye size={14} /> : <EyeOff size={14} />}
                </button>
                <button
                  onClick={() => {
                    setModalType('announcement');
                    setSelectedItem(ann);
                    setModalOpen(true);
                  }}
                  className="p-1 text-slate-400 hover:text-white"
                >
                  <Edit2 size={13} />
                </button>
                <button
                  onClick={() => handleDeleteAnnouncement(ann.id)}
                  className="p-1 text-rose-400 hover:text-rose-300"
                >
                  <Trash2 size={13} />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 2. Company Stats / Metrics */}
      <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div>
            <h3 className="font-semibold text-sm text-white">Live Company Achievements & Metrics</h3>
            <p className="text-xs text-slate-400">Counters shown in the Stats section (Businesses Served, Satisfaction, etc.).</p>
          </div>
          <button
            onClick={() => {
              setModalType('stat');
              setSelectedItem({ label: '', value: '100+', change: '+20% YoY', order: stats.length + 1, is_active: true });
              setModalOpen(true);
            }}
            className="px-3 py-1.5 text-xs font-semibold text-slate-950 bg-gold hover:bg-gold-hover rounded-lg transition-colors flex items-center gap-1.5"
          >
            <Plus size={13} /> Add Metric
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {stats.map((item) => (
            <div
              key={item.id}
              className={`p-4 rounded-xl border flex flex-col justify-between ${
                item.is_active ? 'bg-slate-950/80 border-slate-800' : 'bg-slate-950/30 border-slate-800/40 opacity-50'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xl font-bold font-serif text-gold">{item.value}</span>
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => handleToggleStat(item)}
                    className={`p-1 rounded ${item.is_active ? 'text-emerald-400' : 'text-slate-500'}`}
                  >
                    {item.is_active ? <Eye size={14} /> : <EyeOff size={14} />}
                  </button>
                  <button
                    onClick={() => {
                      setModalType('stat');
                      setSelectedItem(item);
                      setModalOpen(true);
                    }}
                    className="p-1 text-slate-400 hover:text-white"
                  >
                    <Edit2 size={13} />
                  </button>
                  <button
                    onClick={() => handleDeleteStat(item.id, item.label)}
                    className="p-1 text-rose-400 hover:text-rose-300"
                  >
                    <Trash2 size={13} />
                  </button>
                </div>
              </div>

              <div>
                <p className="text-xs font-medium text-white">{item.label}</p>
                {item.change && <p className="text-[11px] text-emerald-400 font-mono mt-0.5">{item.change}</p>}
              </div>
            </div>
          ))}
        </div>
      </div>

      <ItemEditModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        onSave={handleSaveModal}
        title={
          modalType === 'stat'
            ? selectedItem?.id ? `Edit Metric: ${selectedItem.label}` : 'Add New Metric'
            : selectedItem?.id ? 'Edit Announcement' : 'Add New Announcement'
        }
        fields={modalType === 'stat' ? STAT_FIELDS : ANNOUNCEMENT_FIELDS}
        initialData={selectedItem}
        isSaving={isSaving}
      />
    </div>
  );
}

