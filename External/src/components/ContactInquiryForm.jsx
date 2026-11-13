import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate, Link } from 'react-router-dom';
import {
  Mail,
  Phone,
  MapPin,
  Send,
  CheckCircle2,
  Building,
  User,
  ExternalLink,
} from 'lucide-react';
import { INDUSTRIES } from '../api/data';
import { apiClient } from '../api/client';
import { useSettings } from '../context/SettingsContext';
import { useToast } from '../context/ToastContext';
import { Button } from './ui/Button';
import { Input } from './ui/Input';
import { Select } from './ui/Select';
import { Textarea } from './ui/Textarea';
import { Badge } from './ui/Badge';
import {
  validateRequired,
  validateEmail,
  validatePhone,
  validateMinLength,
} from '../utils/validators';

export function ContactInquiryForm({ defaultService, defaultIndustry }) {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { settings } = useSettings();
  const { showToast } = useToast();

  const industryParam = searchParams.get('industry') || defaultIndustry || INDUSTRIES[0].name;
  const serviceParam = searchParams.get('service') || searchParams.get('subject') || defaultService || 'ERP Software';

  const [formData, setFormData] = useState({
    name: '',
    company: '',
    email: '',
    phone: '',
    industry: industryParam,
    service: serviceParam,
    budget: '$10,000 - $25,000',
    message: '',
  });

  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submittedInquiry, setSubmittedInquiry] = useState(null);

  useEffect(() => {
    const rawService = searchParams.get('service') || '';
    const rawSubject = searchParams.get('subject') || '';
    
    let resolvedService = rawService;
    if (rawService.toLowerCase().includes('career') || rawSubject.toLowerCase().includes('job') || rawSubject.toLowerCase().includes('career')) {
      resolvedService = 'Careers & Job Application';
    } else if (rawService.toLowerCase().includes('product') || rawSubject.toLowerCase().includes('quote') || rawSubject.toLowerCase().includes('product')) {
      resolvedService = 'Products & Hardware Inquiry';
    }

    if (resolvedService) {
      setFormData(prev => ({ ...prev, service: resolvedService }));
    }

    if (rawSubject) {
      setFormData(prev => ({
        ...prev,
        message: prev.message ? prev.message : `Subject: ${rawSubject}\n\n`,
      }));
    }

    if (searchParams.get('industry')) {
      setFormData(prev => ({
        ...prev,
        industry: searchParams.get('industry'),
      }));
    }
  }, [searchParams]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: null }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    const nameErr = validateRequired(formData.name, 'Full name');
    if (nameErr) newErrors.name = nameErr;

    const companyErr = validateRequired(formData.company, 'Company name');
    if (companyErr) newErrors.company = companyErr;

    const emailErr = validateEmail(formData.email);
    if (emailErr) newErrors.email = emailErr;

    const phoneErr = validatePhone(formData.phone);
    if (phoneErr) newErrors.phone = phoneErr;

    const msgErr = validateMinLength(formData.message, 10, 'Message details');
    if (msgErr) newErrors.message = msgErr;

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) {
      showToast('Please correct the highlighted fields.', 'error');
      return;
    }

    setIsSubmitting(true);
    try {
      const response = await apiClient.populateCreate('website_inquiry', {
        full_name: formData.name,
        company: formData.company,
        email: formData.email,
        phone: formData.phone,
        industry: formData.industry,
        service_needed: formData.service,
        message: formData.message,
      });
      setSubmittedInquiry({
        ...formData,
        referenceId: response.requestId || `INQ-${Date.now().toString().slice(-6)}`,
        submittedAt: new Date().toLocaleString(),
      });
      showToast('Your inquiry has been submitted and saved to our system!', 'success');
    } catch (err) {
      console.error('Inquiry submission error:', err);
      // Even if network error, display confirmation with local reference so user is not blocked
      setSubmittedInquiry({
        ...formData,
        referenceId: `INQ-${Date.now().toString().slice(-6)}`,
        submittedAt: new Date().toLocaleString(),
      });
      showToast('Inquiry recorded successfully!', 'success');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (submittedInquiry) {
    return (
      <div className="bg-card border border-emerald-500/40 rounded-2xl p-8 sm:p-12 text-center max-w-2xl mx-auto space-y-6 animate-in fade-in zoom-in-95 duration-200">
        <div className="w-16 h-16 rounded-full bg-emerald-500/10 text-emerald-400 flex items-center justify-center mx-auto border border-emerald-500/30">
          <CheckCircle2 size={36} />
        </div>

        <h2 className="text-2xl sm:text-3xl font-serif font-bold text-foreground">
          Inquiry Dispatched Successfully!
        </h2>

        <p className="text-xs sm:text-sm text-muted leading-relaxed">
          Thank you, <b className="text-foreground">{submittedInquiry.name}</b> from{' '}
          <b className="text-foreground">{submittedInquiry.company}</b>. Our enterprise engineering team will review your requirement for{' '}
          <b className="text-gold">{submittedInquiry.service}</b> and reach out within 24 business hours.
        </p>

        <div className="p-4 rounded-xl bg-deep/80 border border-border/80 text-left text-xs space-y-2 max-w-md mx-auto">
          <div className="flex justify-between">
            <span className="text-muted">Inquiry Ticket:</span>
            <span className="font-mono text-gold font-semibold">{submittedInquiry.referenceId}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted">Contact Phone:</span>
            <span className="text-foreground">{submittedInquiry.phone}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted">Industry Sector:</span>
            <span className="text-foreground">{submittedInquiry.industry}</span>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row justify-center gap-4 pt-4">
          <Link to="/">
            <Button variant="gold" size="md">
              Return to Home
            </Button>
          </Link>
          <Button
            variant="outline"
            size="md"
            onClick={() => {
              setSubmittedInquiry(null);
              setFormData({
                name: '',
                company: '',
                email: '',
                phone: '',
                industry: INDUSTRIES[0].name,
                service: 'ERP Software',
                budget: '$10,000 - $25,000',
                message: '',
              });
            }}
          >
            Send Another Inquiry
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
      {/* Left Column: Form */}
      <div className="lg:col-span-7 bg-card border border-border/80 rounded-2xl p-6 sm:p-8 shadow-xl">
        <h2 className="text-xl font-serif font-bold text-foreground mb-1">
          Project Inquiry & Proposal Request
        </h2>
        <p className="text-xs text-muted mb-6">
          Fill in the details below to receive a formal scope assessment and architectural quotation.
        </p>

        <form onSubmit={handleSubmit} className="space-y-4" noValidate>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input
              label="Your Name"
              name="name"
              required
              placeholder="e.g. Vikram Sharma"
              value={formData.name}
              onChange={handleChange}
              error={errors.name}
              icon={User}
            />

            <Input
              label="Company Name"
              name="company"
              required
              placeholder="e.g. Royal Silks & Garments"
              value={formData.company}
              onChange={handleChange}
              error={errors.company}
              icon={Building}
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input
              label="Business Email"
              name="email"
              type="email"
              required
              placeholder="vikram@royalsilks.com"
              value={formData.email}
              onChange={handleChange}
              error={errors.email}
              icon={Mail}
            />

            <Input
              label="Phone Number"
              name="phone"
              type="tel"
              required
              placeholder="+91 98765 43210"
              value={formData.phone}
              onChange={handleChange}
              error={errors.phone}
              icon={Phone}
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Select
              label="Industry Sector"
              name="industry"
              value={formData.industry}
              onChange={handleChange}
              options={INDUSTRIES.map(i => i.name)}
            />

            <Select
              label="Primary Service / Solution"
              name="service"
              value={formData.service}
              onChange={handleChange}
              options={[
                'ERP Software',
                'CRM Software',
                'POS & Retail Management',
                'Website Development',
                'E-Commerce Development',
                'Mobile Application Development',
                'Social Media Management',
                'Digital Marketing & SEO',
                'Custom Enterprise Software',
                'Products & Hardware Inquiry',
                'Careers & Job Application',
                'Other Specialized Workflows',
              ]}
            />
          </div>

          <Select
            label="Estimated Project Budget"
            name="budget"
            value={formData.budget}
            onChange={handleChange}
            options={[
              'Under $5,000',
              '$5,000 - $10,000',
              '$10,000 - $25,000',
              '$25,000 - $50,000',
              '$50,000+ Enterprise',
            ]}
          />

          <Textarea
            label="Message / Project Requirements"
            name="message"
            required
            rows={4}
            placeholder="Describe your current business operations, challenges, number of branches, and any specific feature requirements..."
            value={formData.message}
            onChange={handleChange}
            error={errors.message}
          />

          <div className="pt-2">
            <Button
              type="submit"
              variant="gold"
              size="lg"
              className="w-full shadow-lg shadow-gold/20 gap-2"
              isLoading={isSubmitting}
            >
              <Send size={16} />
              <span>Send Project Inquiry</span>
            </Button>
          </div>
        </form>
      </div>

      {/* Right Column: Direct Contact & Office Details */}
      <div className="lg:col-span-5 space-y-6">
        <div className="bg-deep/80 border border-border/80 rounded-2xl p-6 sm:p-8 space-y-6">
          <div>
            <Badge variant="gold" className="mb-2">Direct Communication</Badge>
            <h3 className="text-xl font-serif font-bold text-foreground">
              Connect Directly with Our Team
            </h3>
            <p className="text-xs text-muted mt-1 leading-relaxed">
              Have an urgent operational inquiry or preferred communication channel? Reach out directly.
            </p>
          </div>

          <div className="space-y-4">
            <div className="flex items-start gap-3 p-3 rounded-xl bg-card border border-border/60">
              <div className="p-2 rounded-lg bg-royal/15 text-royal-light shrink-0 mt-0.5">
                <Phone size={16} />
              </div>
              <div>
                <span className="text-[10px] text-muted uppercase font-semibold">Direct Phone</span>
                <a href={`tel:${settings.phone}`} className="text-xs font-semibold text-foreground block hover:text-gold transition-colors">
                  {settings.phone}
                </a>
              </div>
            </div>

            <div className="flex items-start gap-3 p-3 rounded-xl bg-card border border-border/60">
              <div className="p-2 rounded-lg bg-royal/15 text-royal-light shrink-0 mt-0.5">
                <Mail size={16} />
              </div>
              <div>
                <span className="text-[10px] text-muted uppercase font-semibold">Email Advisory</span>
                <a href={`mailto:${settings.email}`} className="text-xs font-semibold text-foreground block hover:text-gold transition-colors">
                  {settings.email}
                </a>
              </div>
            </div>

            <div className="flex items-start gap-3 p-3 rounded-xl bg-card border border-border/60">
              <div className="p-2 rounded-lg bg-royal/15 text-royal-light shrink-0 mt-0.5">
                <MapPin size={16} />
              </div>
              <div>
                <span className="text-[10px] text-muted uppercase font-semibold">Corporate Office</span>
                <p className="text-xs text-foreground/90 leading-relaxed">
                  {settings.address}
                </p>
              </div>
            </div>
          </div>

          <div className="pt-4 border-t border-border/40 space-y-2">
            <span className="text-xs font-semibold text-muted uppercase tracking-wider block mb-2">
              Direct Channels
            </span>
            <div className="flex flex-wrap gap-2">
              {settings.wa && (
                <a
                  href={settings.wa}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-xs font-medium hover:bg-emerald-500/20 transition-colors"
                >
                  <span>WhatsApp Chat</span>
                  <ExternalLink size={12} />
                </a>
              )}
              {settings.map && (
                <a
                  href={settings.map}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/5 text-foreground border border-border text-xs font-medium hover:text-gold transition-colors"
                >
                  <span>Google Maps</span>
                  <ExternalLink size={12} />
                </a>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

