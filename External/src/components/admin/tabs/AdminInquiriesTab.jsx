import React, { useState, useEffect } from 'react';
import { Mail, Phone, Building, Calendar, MessageSquare, Search, CheckCircle, Clock, Trash2 } from 'lucide-react';
import { apiClient } from '../../../api/client';
import { useToast } from '../../../context/ToastContext';

export function AdminInquiriesTab() {
  const [inquiries, setInquiries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  const [selectedInquiry, setSelectedInquiry] = useState(null);
  const { addToast } = useToast();

  const fetchInquiries = async () => {
    setLoading(true);
    try {
      const res = await apiClient.populateRead('website_inquiry');
      setInquiries(res.data?.data || []);
    } catch (err) {
      console.error(err);
      addToast('Failed to load inquiries', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInquiries();
  }, []);

  const handleStatusChange = async (inquiryId, newStatus) => {
    try {
      await apiClient.populateUpdate('website_inquiry', inquiryId, { status: newStatus });
      addToast(`Status updated to ${newStatus}`, 'success');
      setInquiries(prev => prev.map(inq => inq.id === inquiryId ? { ...inq, status: newStatus } : inq));
      if (selectedInquiry?.id === inquiryId) {
        setSelectedInquiry(prev => ({ ...prev, status: newStatus }));
      }
    } catch (err) {
      addToast(err.message || 'Failed to update status', 'error');
    }
  };

  const handleDelete = async (inquiryId, name) => {
    if (!window.confirm(`Delete inquiry from ${name}?`)) return;
    try {
      await apiClient.populateDelete('website_inquiry', inquiryId);
      addToast('Deleted inquiry', 'success');
      setInquiries(prev => prev.filter(i => i.id !== inquiryId));
      if (selectedInquiry?.id === inquiryId) setSelectedInquiry(null);
    } catch (err) {
      addToast(err.message || 'Failed to delete inquiry', 'error');
    }
  };

  const filtered = inquiries.filter((inq) => {
    const matchesSearch =
      inq.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      inq.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      inq.company?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      inq.service_needed?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'All' || inq.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  if (loading) {
    return <div className="py-12 text-center text-slate-400 text-sm">Loading Website Inquiries...</div>;
  }

  return (
    <div className="space-y-4 max-w-5xl mx-auto">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-4 border-b border-slate-800">
        <div>
          <h2 className="text-lg font-semibold text-white">Website Contact Inquiries</h2>
          <p className="text-xs text-slate-400">Prospective clients and leads submitted through the website contact form.</p>
        </div>
        <div className="flex items-center gap-2">
          {['All', 'New', 'Contacted', 'Qualified', 'Closed'].map((s) => (
            <button
              key={s}
              onClick={() => setStatusFilter(s)}
              className={`px-3 py-1 text-xs rounded-lg transition-colors font-medium ${
                statusFilter === s
                  ? 'bg-gold text-slate-950 font-semibold'
                  : 'bg-slate-900 text-slate-400 hover:text-white border border-slate-800'
              }`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      <div className="flex items-center gap-2 bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs">
        <Search size={14} className="text-slate-400 shrink-0" />
        <input
          type="text"
          placeholder="Search inquiries by lead name, email, company or service..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="bg-transparent w-full text-white placeholder-slate-500 focus:outline-none"
        />
      </div>

      {filtered.length === 0 ? (
        <div className="py-12 text-center text-slate-500 text-sm border border-dashed border-slate-800 rounded-xl">
          No inquiries found.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
          <div className="md:col-span-6 space-y-3">
            {filtered.map((item) => {
              const isSelected = selectedInquiry?.id === item.id;
              const isNew = item.status === 'New';
              return (
                <div
                  key={item.id}
                  onClick={() => setSelectedInquiry(item)}
                  className={`p-4 rounded-xl border cursor-pointer transition-all ${
                    isSelected
                      ? 'bg-slate-900 border-gold shadow-lg shadow-gold/10'
                      : isNew
                      ? 'bg-slate-900/90 border-slate-700 hover:border-slate-600'
                      : 'bg-slate-950/60 border-slate-800/80 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2 mb-1.5">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-sm text-white">{item.full_name}</span>
                      {isNew && (
                        <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-amber-500/20 text-amber-300 border border-amber-500/40">
                          NEW
                        </span>
                      )}
                    </div>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                      {item.status}
                    </span>
                  </div>

                  <p className="text-xs text-slate-400 mb-2 font-medium">
                    {item.company ? `${item.company} • ` : ''}{item.service_needed || 'General Inquiry'}
                  </p>

                  <p className="text-xs text-slate-300 line-clamp-2 mb-3">
                    {item.message}
                  </p>

                  <div className="flex items-center justify-between text-[11px] text-slate-500 pt-2 border-t border-slate-800/60 font-mono">
                    <span>{item.email}</span>
                    <span>{item.created_at ? new Date(item.created_at).toLocaleDateString() : 'Recent'}</span>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Details Column */}
          <div className="md:col-span-6">
            {selectedInquiry ? (
              <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl sticky top-20 space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                  <div>
                    <h3 className="font-semibold text-base text-white">{selectedInquiry.full_name}</h3>
                    <p className="text-xs text-slate-400">{selectedInquiry.company || 'Individual Client'}</p>
                  </div>
                  <button
                    onClick={() => handleDelete(selectedInquiry.id, selectedInquiry.full_name)}
                    className="p-1.5 text-rose-400 hover:text-rose-300 hover:bg-rose-500/10 rounded-lg transition-colors"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>

                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                    <span className="text-[10px] text-slate-500 block mb-0.5">Email Address</span>
                    <a href={`mailto:${selectedInquiry.email}`} className="text-gold hover:underline flex items-center gap-1 font-mono">
                      <Mail size={12} /> {selectedInquiry.email}
                    </a>
                  </div>

                  <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                    <span className="text-[10px] text-slate-500 block mb-0.5">Phone Number</span>
                    <a href={`tel:${selectedInquiry.phone}`} className="text-slate-200 hover:text-white flex items-center gap-1 font-mono">
                      <Phone size={12} /> {selectedInquiry.phone || 'N/A'}
                    </a>
                  </div>

                  <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                    <span className="text-[10px] text-slate-500 block mb-0.5">Industry Vertical</span>
                    <span className="text-slate-200">{selectedInquiry.industry || 'Not specified'}</span>
                  </div>

                  <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                    <span className="text-[10px] text-slate-500 block mb-0.5">Service Requested</span>
                    <span className="text-slate-200 font-medium">{selectedInquiry.service_needed || 'General Consultation'}</span>
                  </div>
                </div>

                <div>
                  <span className="text-xs font-semibold text-slate-300 block mb-1.5">Customer Message</span>
                  <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-200 leading-relaxed whitespace-pre-wrap">
                    {selectedInquiry.message}
                  </div>
                </div>

                <div className="pt-3 border-t border-slate-800">
                  <span className="text-xs font-medium text-slate-400 block mb-2">Update Lead Status</span>
                  <div className="flex items-center gap-2">
                    {['New', 'Contacted', 'Qualified', 'Closed'].map((st) => (
                      <button
                        key={st}
                        onClick={() => handleStatusChange(selectedInquiry.id, st)}
                        className={`flex-1 py-1.5 text-xs rounded-lg font-medium transition-colors border ${
                          selectedInquiry.status === st
                            ? 'bg-gold text-slate-950 border-gold font-semibold'
                            : 'bg-slate-950 text-slate-400 border-slate-800 hover:border-slate-700 hover:text-white'
                        }`}
                      >
                        {st}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="p-12 text-center text-slate-500 text-xs border border-dashed border-slate-800 rounded-2xl">
                Click on any inquiry from the left to view complete details, contact information, and update lead status.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

