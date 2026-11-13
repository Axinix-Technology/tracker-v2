import React, { useState, useEffect } from 'react';
import { X, Save, Plus, Trash2 } from 'lucide-react';

export function ItemEditModal({
  isOpen,
  onClose,
  onSave,
  title = 'Edit Item',
  fields = [],
  initialData = {},
  isSaving = false,
}) {
  const [formData, setFormData] = useState({});

  useEffect(() => {
    if (initialData) {
      setFormData({ ...initialData });
    } else {
      setFormData({});
    }
  }, [initialData, isOpen]);

  if (!isOpen) return null;

  const handleChange = (name, value) => {
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleArrayAdd = (fieldName) => {
    const arr = Array.isArray(formData[fieldName]) ? [...formData[fieldName]] : [];
    arr.push('');
    handleChange(fieldName, arr);
  };

  const handleArrayChange = (fieldName, index, val) => {
    const arr = Array.isArray(formData[fieldName]) ? [...formData[fieldName]] : [];
    arr[index] = val;
    handleChange(fieldName, arr);
  };

  const handleArrayRemove = (fieldName, index) => {
    const arr = Array.isArray(formData[fieldName]) ? [...formData[fieldName]] : [];
    arr.splice(index, 1);
    handleChange(fieldName, arr);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-fadeIn">
      <div className="w-full max-w-2xl max-h-[90vh] bg-slate-900 border border-slate-700/80 rounded-2xl shadow-2xl flex flex-col overflow-hidden text-slate-100">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/70 shrink-0">
          <h3 className="font-semibold text-base text-white">{title}</h3>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white transition-colors"
          >
            <X size={18} />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-6 space-y-4">
          {fields.map((f) => {
            const val = formData[f.name];

            if (f.type === 'textarea') {
              return (
                <div key={f.name}>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    {f.label} {f.required && <span className="text-rose-400">*</span>}
                  </label>
                  <textarea
                    rows={f.rows || 3}
                    value={val || ''}
                    onChange={(e) => handleChange(f.name, e.target.value)}
                    placeholder={f.placeholder || ''}
                    required={f.required}
                    className="w-full px-3.5 py-2 text-sm bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-gold transition-colors"
                  />
                  {f.hint && <p className="text-[11px] text-slate-500 mt-1">{f.hint}</p>}
                </div>
              );
            }

            if (f.type === 'switch' || f.type === 'checkbox') {
              const checked = Boolean(val ?? f.default ?? true);
              return (
                <div key={f.name} className="flex items-center justify-between py-2 border-b border-slate-800/60">
                  <div>
                    <label className="text-sm font-medium text-slate-200">{f.label}</label>
                    {f.hint && <p className="text-[11px] text-slate-500">{f.hint}</p>}
                  </div>
                  <button
                    type="button"
                    onClick={() => handleChange(f.name, !checked)}
                    className={`w-11 h-6 rounded-full transition-colors relative flex items-center px-0.5 ${
                      checked ? 'bg-gold' : 'bg-slate-700'
                    }`}
                  >
                    <span
                      className={`w-5 h-5 rounded-full bg-slate-950 shadow-md transform transition-transform ${
                        checked ? 'translate-x-5' : 'translate-x-0'
                      }`}
                    />
                  </button>
                </div>
              );
            }

            if (f.type === 'array-strings') {
              const list = Array.isArray(val) ? val : [];
              return (
                <div key={f.name} className="space-y-2 pt-2 border-t border-slate-800/60">
                  <div className="flex items-center justify-between">
                    <label className="text-xs font-semibold text-slate-300">
                      {f.label} ({list.length})
                    </label>
                    <button
                      type="button"
                      onClick={() => handleArrayAdd(f.name)}
                      className="px-2 py-1 text-xs text-gold hover:text-gold-hover bg-gold/10 hover:bg-gold/20 rounded border border-gold/30 flex items-center gap-1 transition-colors"
                    >
                      <Plus size={12} /> Add Item
                    </button>
                  </div>
                  {list.map((item, idx) => (
                    <div key={idx} className="flex items-center gap-2">
                      <input
                        type="text"
                        value={item}
                        onChange={(e) => handleArrayChange(f.name, idx, e.target.value)}
                        placeholder={`Item ${idx + 1}...`}
                        className="flex-1 px-3 py-1.5 text-xs bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-gold"
                      />
                      <button
                        type="button"
                        onClick={() => handleArrayRemove(f.name, idx)}
                        className="text-slate-500 hover:text-rose-400 p-1 transition-colors"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  ))}
                  {f.hint && <p className="text-[11px] text-slate-500">{f.hint}</p>}
                </div>
              );
            }

            return (
              <div key={f.name}>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  {f.label} {f.required && <span className="text-rose-400">*</span>}
                </label>
                <input
                  type={f.type || 'text'}
                  value={val ?? ''}
                  onChange={(e) =>
                    handleChange(f.name, f.type === 'number' ? Number(e.target.value) : e.target.value)
                  }
                  placeholder={f.placeholder || ''}
                  required={f.required}
                  step={f.step}
                  className="w-full px-3.5 py-2 text-sm bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-gold transition-colors"
                />
                {f.hint && <p className="text-[11px] text-slate-500 mt-1">{f.hint}</p>}
              </div>
            );
          })}

          {/* Footer Buttons */}
          <div className="pt-4 border-t border-slate-800 flex items-center justify-end gap-3 sticky bottom-0 bg-slate-900 pb-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-xs font-medium text-slate-400 hover:text-white transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSaving}
              className="px-5 py-2 text-xs font-semibold text-slate-950 bg-gold hover:bg-gold-hover rounded-lg transition-colors flex items-center gap-1.5 shadow-lg shadow-gold/20 disabled:opacity-50"
            >
              <Save size={14} />
              {isSaving ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

