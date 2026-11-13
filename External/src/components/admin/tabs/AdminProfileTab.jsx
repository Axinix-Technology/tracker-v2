import React, { useState, useEffect } from 'react';
import { Building2, Save, Mail, Phone, MapPin, Globe, Sparkles } from 'lucide-react';
import { apiClient } from '../../../api/client';
import { useToast } from '../../../context/ToastContext';

export function AdminProfileTab() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [profile, setProfile] = useState({
    id: null,
    name: 'AXINIX Technologies',
    legal_name: 'Axinix Technologies Pvt. Ltd.',
    tagline: 'Powering Every Industry. Enabling Every Possibility.',
    about_text: '',
    logo_url: '/axinix-brand-mark.jpg',
    website: 'https://www.axinixtech.com',
    contact_email: 'prism@axinixtech.com',
    hr_email: 'hr@axinixtech.com',
    it_email: 'it@axinixtech.com',
    phone: '+91 98765 43210',
    address: { street: '', city: 'Coimbatore', state: 'Tamil Nadu', country: 'India', zip: '641001' },
    social_links: { linkedin: '', twitter: '', github: '', youtube: '' }
  });
  const { addToast } = useToast();

  const fetchProfile = async () => {
    setLoading(true);
    try {
      const res = await apiClient.populateRead('company_profile');
      const list = res.data?.data || [];
      if (list.length > 0) {
        setProfile(list[0]);
      }
    } catch (err) {
      console.error('Failed to load company profile:', err);
      addToast('Failed to load profile from database', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProfile();
  }, []);

  const handleChange = (field, val) => {
    setProfile(p => ({ ...p, [field]: val }));
  };

  const handleNestedChange = (parent, field, val) => {
    setProfile(p => ({
      ...p,
      [parent]: { ...(p[parent] || {}), [field]: val }
    }));
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      if (profile.id) {
        await apiClient.populateUpdate('company_profile', profile.id, profile);
      } else {
        await apiClient.populateCreate('company_profile', profile);
      }
      addToast('Company branding & contact information saved!', 'success');
      fetchProfile();
    } catch (err) {
      addToast(err.message || 'Failed to save company profile', 'error');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="py-12 text-center text-slate-400 text-sm">Loading Company Profile...</div>;
  }

  return (
    <form onSubmit={handleSave} className="space-y-6 max-w-4xl mx-auto">
      <div className="flex items-center justify-between pb-4 border-b border-slate-800">
        <div>
          <h2 className="text-lg font-semibold text-white">Company Identity & Contact Info</h2>
          <p className="text-xs text-slate-400">Manage branding, official addresses, support emails, and social links.</p>
        </div>
        <button
          type="submit"
          disabled={saving}
          className="px-5 py-2 text-xs font-semibold text-slate-950 bg-gold hover:bg-gold-hover rounded-lg transition-colors flex items-center gap-1.5 shadow-lg shadow-gold/20 disabled:opacity-50"
        >
          <Save size={14} />
          {saving ? 'Saving...' : 'Save Profile'}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1">Brand Name</label>
          <input
            type="text"
            value={profile.name || ''}
            onChange={(e) => handleChange('name', e.target.value)}
            required
            className="w-full px-3.5 py-2 text-sm bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-gold"
          />
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1">Legal Registered Name</label>
          <input
            type="text"
            value={profile.legal_name || ''}
            onChange={(e) => handleChange('legal_name', e.target.value)}
            required
            className="w-full px-3.5 py-2 text-sm bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-gold"
          />
        </div>

        <div className="md:col-span-2">
          <label className="block text-xs font-medium text-slate-300 mb-1">Company Tagline / Slogan</label>
          <input
            type="text"
            value={profile.tagline || ''}
            onChange={(e) => handleChange('tagline', e.target.value)}
            className="w-full px-3.5 py-2 text-sm bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-gold"
          />
        </div>

        <div className="md:col-span-2">
          <label className="block text-xs font-medium text-slate-300 mb-1">About Company Vision</label>
          <textarea
            rows={3}
            value={profile.about_text || ''}
            onChange={(e) => handleChange('about_text', e.target.value)}
            className="w-full px-3.5 py-2 text-sm bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-gold"
          />
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1">Official Website URL</label>
          <input
            type="url"
            value={profile.website || ''}
            onChange={(e) => handleChange('website', e.target.value)}
            className="w-full px-3.5 py-2 text-sm bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-gold"
          />
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1">Official Logo URL</label>
          <input
            type="text"
            value={profile.logo_url || ''}
            onChange={(e) => handleChange('logo_url', e.target.value)}
            className="w-full px-3.5 py-2 text-sm bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-gold"
          />
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1">Primary Contact Email</label>
          <input
            type="email"
            value={profile.contact_email || ''}
            onChange={(e) => handleChange('contact_email', e.target.value)}
            className="w-full px-3.5 py-2 text-sm bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-gold"
          />
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1">Official Phone Number</label>
          <input
            type="text"
            value={profile.phone || ''}
            onChange={(e) => handleChange('phone', e.target.value)}
            className="w-full px-3.5 py-2 text-sm bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-gold"
          />
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1">HR Email</label>
          <input
            type="email"
            value={profile.hr_email || ''}
            onChange={(e) => handleChange('hr_email', e.target.value)}
            className="w-full px-3.5 py-2 text-sm bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-gold"
          />
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1">IT Support Email</label>
          <input
            type="email"
            value={profile.it_email || ''}
            onChange={(e) => handleChange('it_email', e.target.value)}
            className="w-full px-3.5 py-2 text-sm bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-gold"
          />
        </div>
      </div>

      {/* Address */}
      <div className="pt-4 border-t border-slate-800">
        <h3 className="text-sm font-semibold text-slate-200 mb-3 flex items-center gap-2">
          <MapPin size={15} className="text-gold" /> Physical Headquarters Address
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div className="sm:col-span-3">
            <input
              type="text"
              placeholder="Street Address..."
              value={profile.address?.street || ''}
              onChange={(e) => handleNestedChange('address', 'street', e.target.value)}
              className="w-full px-3 py-1.5 text-xs bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-gold"
            />
          </div>
          <div>
            <input
              type="text"
              placeholder="City (e.g. Coimbatore)"
              value={profile.address?.city || ''}
              onChange={(e) => handleNestedChange('address', 'city', e.target.value)}
              className="w-full px-3 py-1.5 text-xs bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-gold"
            />
          </div>
          <div>
            <input
              type="text"
              placeholder="State (e.g. Tamil Nadu)"
              value={profile.address?.state || ''}
              onChange={(e) => handleNestedChange('address', 'state', e.target.value)}
              className="w-full px-3 py-1.5 text-xs bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-gold"
            />
          </div>
          <div>
            <input
              type="text"
              placeholder="Postal Code / PIN"
              value={profile.address?.zip || ''}
              onChange={(e) => handleNestedChange('address', 'zip', e.target.value)}
              className="w-full px-3 py-1.5 text-xs bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-gold"
            />
          </div>
        </div>
      </div>

      {/* Social Links */}
      <div className="pt-4 border-t border-slate-800">
        <h3 className="text-sm font-semibold text-slate-200 mb-3 flex items-center gap-2">
          <Globe size={15} className="text-gold" /> Social Media Links
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label className="block text-[11px] text-slate-400 mb-1">LinkedIn Profile</label>
            <input
              type="url"
              placeholder="https://linkedin.com/company/..."
              value={profile.social_links?.linkedin || ''}
              onChange={(e) => handleNestedChange('social_links', 'linkedin', e.target.value)}
              className="w-full px-3 py-1.5 text-xs bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-gold"
            />
          </div>
          <div>
            <label className="block text-[11px] text-slate-400 mb-1">Twitter / X Profile</label>
            <input
              type="url"
              placeholder="https://twitter.com/..."
              value={profile.social_links?.twitter || ''}
              onChange={(e) => handleNestedChange('social_links', 'twitter', e.target.value)}
              className="w-full px-3 py-1.5 text-xs bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-gold"
            />
          </div>
          <div>
            <label className="block text-[11px] text-slate-400 mb-1">GitHub Organization</label>
            <input
              type="url"
              placeholder="https://github.com/..."
              value={profile.social_links?.github || ''}
              onChange={(e) => handleNestedChange('social_links', 'github', e.target.value)}
              className="w-full px-3 py-1.5 text-xs bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-gold"
            />
          </div>
          <div>
            <label className="block text-[11px] text-slate-400 mb-1">YouTube Channel</label>
            <input
              type="url"
              placeholder="https://youtube.com/@..."
              value={profile.social_links?.youtube || ''}
              onChange={(e) => handleNestedChange('social_links', 'youtube', e.target.value)}
              className="w-full px-3 py-1.5 text-xs bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-gold"
            />
          </div>
        </div>
      </div>
    </form>
  );
}

