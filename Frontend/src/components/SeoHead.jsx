import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

/**
 * Dynamic SEO Head & OpenGraph Engine for WorkHub ERP
 *
 * Automatically updates:
 * - document.title with branded title
 * - canonical URL tag
 * - meta description
 * - OpenGraph & Twitter tags
 * Eliminates generic "Vite App" / "React App" browser leakage.
 */
export default function SeoHead({
  title,
  description = 'WorkHub is an enterprise multi-tenant ERP platform consolidating HRMS, agile task tracking, tickets, billing, and assets.',
  image = '/vite.svg',
  type = 'website',
}) {
  const location = useLocation();
  const defaultBrand = 'WorkHub ERP';
  const fullTitle = title ? `${title} | ${defaultBrand}` : `WorkHub — Enterprise Resource Planning & Project Management`;
  const canonicalUrl = `${window.location.origin}${location.pathname}`;

  useEffect(() => {
    // 1. Dynamic Title
    document.title = fullTitle;

    // 2. Canonical Tag
    let canonicalTag = document.querySelector('link[rel="canonical"]');
    if (!canonicalTag) {
      canonicalTag = document.createElement('link');
      canonicalTag.setAttribute('rel', 'canonical');
      document.head.appendChild(canonicalTag);
    }
    canonicalTag.setAttribute('href', canonicalUrl);

    // 3. Meta Description
    let metaDesc = document.querySelector('meta[name="description"]');
    if (!metaDesc) {
      metaDesc = document.createElement('meta');
      metaDesc.setAttribute('name', 'description');
      document.head.appendChild(metaDesc);
    }
    metaDesc.setAttribute('content', description);

    // 4. OpenGraph Tags
    const setMetaTag = (property, content) => {
      let tag = document.querySelector(`meta[property="${property}"]`);
      if (!tag) {
        tag = document.createElement('meta');
        tag.setAttribute('property', property);
        document.head.appendChild(tag);
      }
      tag.setAttribute('content', content);
    };

    setMetaTag('og:title', fullTitle);
    setMetaTag('og:description', description);
    setMetaTag('og:url', canonicalUrl);
    setMetaTag('og:image', `${window.location.origin}${image}`);
    setMetaTag('og:type', type);

    // 5. Twitter Card Tags
    const setTwitterTag = (name, content) => {
      let tag = document.querySelector(`meta[name="${name}"]`);
      if (!tag) {
        tag = document.createElement('meta');
        tag.setAttribute('name', name);
        document.head.appendChild(tag);
      }
      tag.setAttribute('content', content);
    };

    setTwitterTag('twitter:title', fullTitle);
    setTwitterTag('twitter:description', description);
    setTwitterTag('twitter:image', `${window.location.origin}${image}`);
  }, [fullTitle, description, canonicalUrl, image, type]);

  return null;
}

