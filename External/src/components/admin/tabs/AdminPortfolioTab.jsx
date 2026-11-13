import React, { useState, useEffect } from 'react';
import { Plus, Edit2, Trash2, Eye, EyeOff, Search, Trophy } from 'lucide-react';
import { apiClient } from '../../../api/client';
import { useToast } from '../../../context/ToastContext';
import { ItemEditModal } from '../ItemEditModal';

const PORTFOLIO_FIELDS = [
  { name: 'slug', label: 'Slug / URL ID', required: true, hint: 'e.g. textile-erp-rollout' },
  { name: 'title', label: 'Project / Case Study Title', required: true },
  { name: 'client', label: 'Client Name', required: true, placeholder: 'e.g. Premier Textile Mills' },
  { name: 'category', label: 'Case Study Category', placeholder: 'e.g. ERP Implementations' },
  { name: 'industry', label: 'Industry Name', placeholder: 'e.g. Textile & Fashion' },
  { name: 'tags', label: 'Tags', type: 'array-strings', hint: 'e.g. ERP, POS, Cloud' },
  { name: 'challenge', label: 'Operational Challenge Solved', type: 'textarea', rows: 2 },
  { name: 'solution', label: 'AXINIX Solution Deployed', type: 'textarea', rows: 2 },
  { name: 'results', label: 'Measurable ROI Results', type: 'array-strings' },
  { name: 'order', label: 'Display Order', type: 'number' },
  { name: 'is_active', label: 'Published / Visible on Website', type: 'switch', default: true },
];

export function AdminPortfolioTab() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const [isSaving, setIsSaving] = useState(false);
  const { addToast } = useToast();

  const fetchItems = async () => {
    setLoading(true);
    try {
      const res = await apiClient.populateRead('showcase_portfolio');
      setItems(res.data?.data || []);
    } catch (err) {
      console.error(err);
      addToast('Failed to load portfolio items', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchItems();
  }, []);

  const handleToggleActive = async (item) => {
    try {
      const updated = !item.is_active;
      await apiClient.populateUpdate('showcase_portfolio', item.id, { is_active: updated });
      addToast(`Portfolio item '${item.title}' is now ${updated ? 'Published' : 'Hidden'}`, 'success');
      setItems(prev => prev.map(s => s.id === item.id ? { ...s, is_active: updated } : s));
    } catch (err) {
      addToast(err.message || 'Failed to update status', 'error');
    }
  };

  const handleDelete = async (id, title) => {
    if (!window.confirm(`Are you sure you want to delete portfolio item '${title}'?`)) return;
    try {
      await apiClient.populateDelete('showcase_portfolio', id);
      addToast(`Deleted portfolio item '${title}'`, 'success');
      setItems(prev => prev.filter(s => s.id !== id));
    } catch (err) {
      addToast(err.message || 'Failed to delete item', 'error');
    }
  };

  const handleSaveModal = async (formData) => {
    setIsSaving(true);
    try {
      if (formData.id) {
        await apiClient.populateUpdate('showcase_portfolio', formData.id, formData);
        addToast(`Updated case study '${formData.title}'`, 'success');
      } else {
        await apiClient.populateCreate('showcase_portfolio', formData);
        addToast(`Created case study '${formData.title}'`, 'success');
      }
      setModalOpen(false);
      fetchItems();
    } catch (err) {
      addToast(err.message || 'Failed to save item', 'error');
    } finally {
      setIsSaving(false);
    }
  };

  const filtered = items.filter(s =>
    s.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    s.client?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    s.industry?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-4 max-w-5xl mx-auto">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-4 border-b border-slate-800">
        <div>
          <h2 className="text-lg font-semibold text-white">Portfolio & Case Studies</h2>
          <p className="text-xs text-slate-400">Showcase customer success stories, challenges, solutions, and tangible ROI metrics.</p>
        </div>
        <button
          onClick={() => {
            setSelectedItem({
              slug: '',
              title: '',
              client: '',
              category: 'ERP Implementations',
              industry: 'Retail & Manufacturing',
              tags: ['ERP'],
              challenge: '',
              solution: '',
              results: [''],
              order: items.length + 1,
              is_active: true
            });
            setModalOpen(true);
          }}
          className="px-4 py-2 text-xs font-semibold text-slate-950 bg-gold hover:bg-gold-hover rounded-lg transition-colors flex items-center gap-1.5 shadow-lg shadow-gold/20"
        >
          <Plus size={14} /> Add Case Study
        </button>
      </div>

      <div className="flex items-center gap-2 bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs">
        <Search size={14} className="text-slate-400 shrink-0" />
        <input
          type="text"
          placeholder="Search case studies by title, client or industry..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="bg-transparent w-full text-white placeholder-slate-500 focus:outline-none"
        />
      </div>

      {loading ? (
        <div className="py-12 text-center text-slate-400 text-sm">Loading Portfolio from Database...</div>
      ) : filtered.length === 0 ? (
        <div className="py-12 text-center text-slate-500 text-sm border border-dashed border-slate-800 rounded-xl">
          No case studies found.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filtered.map((item) => (
            <div
              key={item.id}
              className={`p-5 rounded-xl border transition-all ${
                item.is_active
                  ? 'bg-slate-900/90 border-slate-800 hover:border-slate-700'
                  : 'bg-slate-950/60 border-slate-800/40 opacity-60'
              }`}
            >
              <div className="flex items-start justify-between gap-3 mb-2">
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/15 text-amber-400 border border-amber-500/30">
                  {item.client || item.category}
                </span>
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => handleToggleActive(item)}
                    title={item.is_active ? 'Hide from public site' : 'Publish to public site'}
                    className={`p-1.5 rounded transition-colors ${
                      item.is_active ? 'text-emerald-400 hover:bg-emerald-500/10' : 'text-slate-500 hover:bg-slate-800'
                    }`}
                  >
                    {item.is_active ? <Eye size={15} /> : <EyeOff size={15} />}
                  </button>
                  <button
                    onClick={() => {
                      setSelectedItem(item);
                      setModalOpen(true);
                    }}
                    title="Edit Case Study"
                    className="p-1.5 rounded text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
                  >
                    <Edit2 size={14} />
                  </button>
                  <button
                    onClick={() => handleDelete(item.id, item.title)}
                    title="Delete Case Study"
                    className="p-1.5 rounded text-rose-400 hover:text-rose-300 hover:bg-rose-500/10 transition-colors"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>

              <h3 className="font-semibold text-sm text-white mb-1">{item.title}</h3>
              <p className="text-xs text-slate-400 line-clamp-2 mb-3">{item.solution || item.challenge}</p>

              <div className="text-[11px] text-slate-500 flex items-center justify-between pt-2 border-t border-slate-800/60">
                <span>{item.industry || 'General'}</span>
                <span>{Array.isArray(item.results) ? item.results.length : 0} Measurable Results</span>
                <span>Order #{item.order || 0}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      <ItemEditModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        onSave={handleSaveModal}
        title={selectedItem?.id ? `Edit Case Study: ${selectedItem.title}` : 'Add New Case Study'}
        fields={PORTFOLIO_FIELDS}
        initialData={selectedItem}
        isSaving={isSaving}
      />
    </div>
  );
}

