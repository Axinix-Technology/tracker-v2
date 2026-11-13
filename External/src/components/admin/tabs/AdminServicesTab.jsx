import React, { useState, useEffect } from 'react';
import { Plus, Edit2, Trash2, Eye, EyeOff, Search, Code2 } from 'lucide-react';
import { apiClient } from '../../../api/client';
import { useToast } from '../../../context/ToastContext';
import { ItemEditModal } from '../ItemEditModal';

const SERVICE_FIELDS = [
  { name: 'slug', label: 'Slug / URL ID', required: true, hint: 'e.g. web, mobile, custom, cloud' },
  { name: 'title', label: 'Service Title', required: true, placeholder: 'e.g. Website Development' },
  { name: 'subtitle', label: 'Headline / Pitch', required: true },
  { name: 'description', label: 'Detailed Description', type: 'textarea', rows: 3 },
  { name: 'features', label: 'Key Capabilities / Features', type: 'array-strings' },
  { name: 'deliverables', label: 'Deliverables Included', type: 'array-strings' },
  { name: 'order', label: 'Display Order', type: 'number' },
  { name: 'is_active', label: 'Published / Visible on Website', type: 'switch', default: true },
];

export function AdminServicesTab() {
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const [isSaving, setIsSaving] = useState(false);
  const { addToast } = useToast();

  const fetchServices = async () => {
    setLoading(true);
    try {
      const res = await apiClient.populateRead('showcase_service');
      setServices(res.data?.data || []);
    } catch (err) {
      console.error(err);
      addToast('Failed to load services from database', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchServices();
  }, []);

  const handleToggleActive = async (item) => {
    try {
      const updated = !item.is_active;
      await apiClient.populateUpdate('showcase_service', item.id, { is_active: updated });
      addToast(`Service '${item.title}' is now ${updated ? 'Published' : 'Hidden'}`, 'success');
      setServices(prev => prev.map(s => s.id === item.id ? { ...s, is_active: updated } : s));
    } catch (err) {
      addToast(err.message || 'Failed to update status', 'error');
    }
  };

  const handleDelete = async (id, title) => {
    if (!window.confirm(`Are you sure you want to delete service '${title}'?`)) return;
    try {
      await apiClient.populateDelete('showcase_service', id);
      addToast(`Deleted service '${title}'`, 'success');
      setServices(prev => prev.filter(s => s.id !== id));
    } catch (err) {
      addToast(err.message || 'Failed to delete service', 'error');
    }
  };

  const handleSaveModal = async (formData) => {
    setIsSaving(true);
    try {
      if (formData.id) {
        await apiClient.populateUpdate('showcase_service', formData.id, formData);
        addToast(`Updated service '${formData.title}'`, 'success');
      } else {
        await apiClient.populateCreate('showcase_service', formData);
        addToast(`Created service '${formData.title}'`, 'success');
      }
      setModalOpen(false);
      fetchServices();
    } catch (err) {
      addToast(err.message || 'Failed to save service', 'error');
    } finally {
      setIsSaving(false);
    }
  };

  const filtered = services.filter(s =>
    s.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    s.slug?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    s.subtitle?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-4 max-w-5xl mx-auto">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-4 border-b border-slate-800">
        <div>
          <h2 className="text-lg font-semibold text-white">Professional IT & Software Services</h2>
          <p className="text-xs text-slate-400">Manage digital engineering, cloud architecture, and development services.</p>
        </div>
        <button
          onClick={() => {
            setSelectedItem({
              slug: '',
              title: '',
              subtitle: '',
              description: '',
              features: [''],
              deliverables: [''],
              order: services.length + 1,
              is_active: true
            });
            setModalOpen(true);
          }}
          className="px-4 py-2 text-xs font-semibold text-slate-950 bg-gold hover:bg-gold-hover rounded-lg transition-colors flex items-center gap-1.5 shadow-lg shadow-gold/20"
        >
          <Plus size={14} /> Add Service
        </button>
      </div>

      <div className="flex items-center gap-2 bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs">
        <Search size={14} className="text-slate-400 shrink-0" />
        <input
          type="text"
          placeholder="Search services by title or slug..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="bg-transparent w-full text-white placeholder-slate-500 focus:outline-none"
        />
      </div>

      {loading ? (
        <div className="py-12 text-center text-slate-400 text-sm">Loading Services from Database...</div>
      ) : filtered.length === 0 ? (
        <div className="py-12 text-center text-slate-500 text-sm border border-dashed border-slate-800 rounded-xl">
          No services found.
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
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-500/15 text-blue-400 border border-blue-500/30">
                  /{item.slug}
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
                    title="Edit Service"
                    className="p-1.5 rounded text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
                  >
                    <Edit2 size={14} />
                  </button>
                  <button
                    onClick={() => handleDelete(item.id, item.title)}
                    title="Delete Service"
                    className="p-1.5 rounded text-rose-400 hover:text-rose-300 hover:bg-rose-500/10 transition-colors"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>

              <h3 className="font-semibold text-sm text-white mb-1">{item.title}</h3>
              <p className="text-xs text-slate-400 line-clamp-2 mb-3">{item.subtitle}</p>

              <div className="text-[11px] text-slate-500 flex items-center justify-between pt-2 border-t border-slate-800/60">
                <span>{Array.isArray(item.features) ? item.features.length : 0} Features</span>
                <span>{Array.isArray(item.deliverables) ? item.deliverables.length : 0} Deliverables</span>
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
        title={selectedItem?.id ? `Edit Service: ${selectedItem.title}` : 'Add New Service'}
        fields={SERVICE_FIELDS}
        initialData={selectedItem}
        isSaving={isSaving}
      />
    </div>
  );
}

