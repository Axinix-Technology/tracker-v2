import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { PageBanner } from '../../components/PageBanner';
import { ContentSection } from '../../components/ContentSection';
import { Button } from '../../components/ui/Button';
import { ContactInquiryForm } from '../../components/ContactInquiryForm';

export default function ContactCreatePage() {
  const navigate = useNavigate();

  return (
    <div className="w-full">
      <PageBanner
        badge="Get in Touch"
        title="Let's Build Something Powerful Together"
        subtitle="Tell us about your organization and requirements. Our technology specialists will help design the right solution."
        breadcrumbs={[
          { label: 'Contact', to: '/contact' },
          { label: 'Request Proposal' },
        ]}
        actions={
          <Button variant="outline" size="sm" onClick={() => navigate(-1)} className="gap-1.5">
            <ArrowLeft size={14} />
            <span>Back</span>
          </Button>
        }
      />

      <ContentSection containerClassName="max-w-6xl">
        <ContactInquiryForm />
      </ContentSection>
    </div>
  );
}
