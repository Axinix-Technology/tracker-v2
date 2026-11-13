import React, { useState, useEffect } from 'react';
import { Plus, Edit2, Trash2, Eye, EyeOff, Star, MessageSquare } from 'lucide-react';
import { apiClient } from '../../../api/client';
import { useToast } from '../../../context/ToastContext';
import { ItemEditModal } from '../ItemEditModal';

const TESTIMONIAL_FIELDS = [
  { name: 'client', label: 'Client / Company Name', required: true, placeholder: 'e.g. Rajesh Textiles' },
  { name: 'role', label: 'Designation / Business Role', placeholder: 'e.g. Managing Director' },
  { name: 'location', label: 'Location / City', placeholder: 'e.g. Surat, Gujarat' },
  { name: 'rating', label: 'Star Rating (1-5)', type: 'number', required: true },
  { name: 'quote', label: 'Client Quote / Feedback', type: 'textarea', rows: 3, required: true },
  { name: 'order', label: 'Display Order', type: 'number' },
  { name: 'is_active', label: 'Published / Visible', type: 'switch', default: true },
];

export function AdminTestimonialsTab() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const [isSaving, setIsSaving] = useState(false);
  const { addToast } = useToast();

  const fetchItems = async () => {
    setLoading(true);
    try {
      const res = await apiClient.populateRead('showcase_testimonial');
      setItems(res.data?.data || []);
    } catch (err) {
      console.error(err);
      addToast('Failed to load testimonials', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchItems();
  }, []);

  const handleToggle = async (item) => {
    try {
      const updated = !item.is_active;
      await apiClient.populateUpdate('showcase_testimonial', item.id, { is_active: updated });
      addToast(`Testimonial ${updated ? 'Published' : 'Hidden'}`, 'success');
      setItems(prev => prev.map(t => t.id === item.id ? { ...t, is_active: updated } : t));
    } catch (err) {
      addToast(err.message || 'Failed to update', 'error');
    }
  };

  const handleDelete = async (id, client) => {
    if (!window.confirm(`Delete testimonial from '${client}'?`)) return;
    try {
      await apiClient.populateDelete('showcase_testimonial', id);
      addToast(`Deleted review from '${client}'`, 'success');
      setItems(prev => prev.filter(t => t.id !== id));
    } catch (err) {
      addToast(err.message || 'Failed to delete', 'error');
    }
  };

  const handleSaveModal = async (formData) => {
    setIsSaving(true);
    try {
      if (formData.id) {
        await apiClient.populateUpdate('showcase_testimonial', formData.id, formData);
        addToast(`Updated review from '${formData.client}'`, 'success');
      } else {
        await apiClient.populateCreate('showcase_testimonial', formData);
        addToast(`Added review from '${formData.client}'`, 'success');
      }
      setModalOpen(false);
      fetchItems();
    } catch (err) {
      addToast(err.message || 'Failed to save', 'error');
    } finally {
      setIsSaving(false);
    }
  };

  if (loading) {
    return <div className="py-12 text-center text-slate-400 text-sm">Loading Testimonials...</div>;
  }

  return (
    <div className="space-y-4 max-w-5xl mx-auto">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-4 border-b border-slate-800">
        <div>
          <h2 className="text-lg font-semibold text-white">Customer Reviews & Testimonials</h2>
          <p className="text-xs text-slate-400">Manage client quotes, verification badges, and star ratings.</p>
        </div>
        <button
          onClick={() => {
            setSelectedItem({
              client: '',
              role: '',
              location: '',
              rating: 5,
              quote: '',
              order: items.length + 1,
              is_active: true
            });
            setModalOpen(true);
          }}
          className="px-4 py-2 text-xs font-semibold text-slate-950 bg-gold hover:bg-gold-hover rounded-lg transition-colors flex items-center gap-1.5 shadow-lg shadow-gold/20"
        >
          <Plus size={14} /> Add Testimonial
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {items.map((item) => (
          <div
            key={item.id}
            className={`p-5 rounded-xl border flex flex-col justify-between ${
              item.is_active ? 'bg-slate-900/90 border-slate-800' : 'bg-slate-950/40 border-slate-800/40 opacity-50'
            }`}
          >
            <div>
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-1 text-gold">
                  {[...Array(item.rating || 5)].map((_, i) => (
                    <Star key={i} size={14} className="fill-gold" />
                  ))}
                </div>
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => handleToggle(item)}
                    className={`p-1.5 rounded ${item.is_active ? 'text-emerald-400' : 'text-slate-500'}`}
                  >
                    {item.is_active ? <Eye size={14} /> : <EyeOff size={14} />}
                  </button>
                  <button
                    onClick={() => {
                      setSelectedItem(item);
                      setModalOpen(true);
                    }}
                    className="p-1.5 rounded text-slate-400 hover:text-white"
                  >
                    <Edit2 size={13} />
                  </button>
                  <button
                    onClick={() => handleDelete(item.id, item.client)}
                    className="p-1.5 rounded text-rose-400 hover:text-rose-300"
                  >
                    <Trash2 size={13} />
                  </button>
                </div>
              </div>

              <p className="text-xs text-slate-300 italic mb-4 leading-relaxed">
                "{item.quote}"
              </p>
            </div>

            <div className="pt-3 border-t border-slate-800/60 flex items-center justify-between text-xs">
              <div>
                <p className="font-semibold text-white">{item.client}</p>
                <p className="text-[11px] text-slate-400">{item.role}</p>
              </div>
              {item.location && (
                <span className="text-[11px] font-mono text-slate-500">{item.location}</span>
              )}
            </div>
          </div>
        ))}
      </div>

      <ItemEditModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        onSave={handleSaveModal}
        title={selectedItem?.id ? `Edit Review from ${selectedItem.client}` : 'Add New Testimonial'}
        fields={TESTIMONIAL_FIELDS}
        initialData={selectedItem}
        isSaving={isSaving}
      />
    </div>
  );
}

