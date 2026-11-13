import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Briefcase,
  Code2,
  Cpu,
  Layers,
  Sparkles,
  ArrowRight,
  MapPin,
  Clock,
  ShieldCheck,
  Zap,
  Users,
  Compass,
  CheckCircle2,
  Send
} from 'lucide-react';
import { PageBanner } from '../../components/PageBanner';
import { ContentSection } from '../../components/ContentSection';
import { Card } from '../../components/ui/Card';
import { Badge } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';
import { CtaBanner } from '../../components/CtaBanner';

const OPEN_POSITIONS = [
  {
    id: 'fullstack-sr',
    title: 'Senior Full-Stack Engineer',
    department: 'Engineering',
    location: 'Bengaluru / Hybrid or Remote',
    type: 'Full-Time',
    experience: '4+ Years',
    description:
      'Lead architecture and full-lifecycle engineering for our modular enterprise ERP suites, real-time analytics engines, and high-concurrency microservices.',
    skills: ['React 19', 'Node.js', 'PostgreSQL', 'Redis', 'REST & GraphQL'],
    featured: true,
  },
  {
    id: 'cloud-devops',
    title: 'Cloud & Infrastructure Architect',
    department: 'DevOps & Cloud',
    location: 'Bengaluru / Remote',
    type: 'Full-Time',
    experience: '5+ Years',
    description:
      'Design, orchestrate, and maintain resilient multi-region cloud deployments, automated CI/CD pipelines, and zero-downtime database replication across enterprise clients.',
    skills: ['AWS', 'Kubernetes', 'Docker', 'Terraform', 'Security Compliance'],
    featured: true,
  },
  {
    id: 'uiux-systems',
    title: 'Lead UI/UX Systems Designer',
    department: 'Product & Design',
    location: 'Hybrid / Remote',
    type: 'Full-Time',
    experience: '3+ Years',
    description:
      'Own the end-to-end design language and component systems powering Axinix enterprise products, client portals, and responsive business intelligence dashboards.',
    skills: ['Design Systems', 'Figma', 'Interactive Prototyping', 'User Research', 'Data Visualization'],
    featured: false,
  },
  {
    id: 'solutions-consultant',
    title: 'Enterprise Solutions Consultant',
    department: 'Client Architecture',
    location: 'Bengaluru / Hybrid',
    type: 'Full-Time',
    experience: '3+ Years',
    description:
      'Bridge the gap between enterprise operational workflows and Axinix software suites. Guide client technical discovery, onboarding, and workflow modernization.',
    skills: ['ERP Workflows', 'Requirements Analysis', 'Technical Demos', 'Client Stakeholder Management'],
    featured: false,
  },
  {
    id: 'mobile-engineer',
    title: 'Mobile Applications Engineer',
    department: 'Engineering',
    location: 'Remote',
    type: 'Full-Time',
    experience: '2+ Years',
    description:
      'Build performant, offline-capable mobile applications for retail POS terminals, field inventory scanners, and mobile executive dashboards.',
    skills: ['React Native / Flutter', 'Offline Sync', 'Hardware Peripherals', 'App Store / Play Store Deployment'],
    featured: false,
  },
];

const PERKS = [
  {
    icon: Zap,
    title: 'Autonomous Ownership',
    desc: 'Zero micromanagement. You own your features from technical RFC to production deployment and client feedback.',
  },
  {
    icon: Code2,
    title: 'Modern Tech Stack',
    desc: 'We refuse legacy spaghetti. Work with modern React, Tailwind, microservices, containerization, and modern cloud infrastructure.',
  },
  {
    icon: Users,
    title: 'Culture of Builders',
    desc: 'Work alongside deeply curious engineers and product minds who care about crafting elegant, robust, real-world systems.',
  },
  {
    icon: ShieldCheck,
    title: 'Competitive Rewards',
    desc: 'Above-market base salary, annual performance incentives, top-tier workstation stipends, and comprehensive health coverage.',
  },
  {
    icon: Compass,
    title: 'Continuous Mastery',
    desc: 'Dedicated annual budget for books, technical certifications, conferences, and specialized cloud tooling.',
  },
  {
    icon: Sparkles,
    title: 'Flexible & Ergonomic',
    desc: 'Flexible working hours, async-first team communication, and ergonomic workspace support for hybrid or remote staff.',
  },
];

export default function CareersPage() {
  const [selectedDept, setSelectedDept] = useState('All');

  const departments = ['All', 'Engineering', 'DevOps & Cloud', 'Product & Design', 'Client Architecture'];

  const filteredRoles = OPEN_POSITIONS.filter(
    role => selectedDept === 'All' || role.department === selectedDept
  );

  return (
    <div className="w-full">
      {/* 1. Page Header */}
      <PageBanner
        title="Build the Future of Enterprise Systems"
        subtitle="Join an engineering-first team creating high-performance software, automated ERP infrastructure, and modern digital ecosystems for growing businesses worldwide."
        breadcrumbs={[{ label: 'Careers & Opportunities' }]}
        badge="Join AXINIX"
      />

      {/* 2. Perks & Culture Section */}
      <ContentSection
        centered
        badge="Life At AXINIX"
        title="Why You'll Love Building With Us"
        subtitle="We value technical curiosity, clear communication, craftsmanship, and a relentless focus on creating tools that genuinely empower businesses."
      >
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {PERKS.map((perk, idx) => {
            const Icon = perk.icon;
            return (
              <Card
                key={idx}
                interactive
                className="p-6 bg-card/60 backdrop-blur-sm border border-border/80 hover:border-gold/50 transition-all group"
              >
                <div className="w-11 h-11 rounded-xl bg-gold/15 text-gold flex items-center justify-center mb-4 border border-gold/30 group-hover:scale-105 transition-transform">
                  <Icon size={22} />
                </div>
                <h3 className="text-lg font-serif font-bold text-foreground group-hover:text-gold transition-colors mb-2">
                  {perk.title}
                </h3>
                <p className="text-xs sm:text-sm text-muted leading-relaxed">
                  {perk.desc}
                </p>
              </Card>
            );
          })}
        </div>
      </ContentSection>

      {/* 3. Open Positions Section */}
      <ContentSection
        bg="card"
        badge="Open Positions"
        title="Explore Opportunities"
        subtitle="We are actively expanding across core software engineering, cloud architecture, product design, and client consulting."
      >
        {/* Department Filters */}
        <div className="flex flex-wrap items-center justify-center gap-2 mb-8">
          {departments.map(dept => (
            <button
              key={dept}
              onClick={() => setSelectedDept(dept)}
              className={`px-4 py-2 rounded-full text-xs font-semibold tracking-wide transition-all ${
                selectedDept === dept
                  ? 'bg-gold text-deep shadow-md shadow-gold/20'
                  : 'bg-background hover:bg-white/10 text-muted hover:text-foreground border border-border/60'
              }`}
            >
              {dept}
            </button>
          ))}
        </div>

        {/* Job Listings Grid */}
        <div className="space-y-4 max-w-5xl mx-auto">
          {filteredRoles.map(job => (
            <Card
              key={job.id}
              interactive
              className="p-6 bg-background/80 border border-border/80 hover:border-gold/50 transition-all flex flex-col md:flex-row md:items-center justify-between gap-6 group"
            >
              <div className="space-y-2.5 max-w-2xl">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-xs font-mono font-semibold uppercase tracking-wider px-2 py-0.5 rounded bg-royal/15 text-royal-light border border-royal/30">
                    {job.department}
                  </span>
                  <span className="text-xs font-mono text-muted flex items-center gap-1">
                    <Clock size={12} /> {job.type}
                  </span>
                  <span className="text-xs font-mono text-muted flex items-center gap-1">
                    <MapPin size={12} /> {job.location}
                  </span>
                  {job.featured && (
                    <Badge variant="gold" size="sm">
                      Urgent Hire
                    </Badge>
                  )}
                </div>

                <h3 className="text-xl font-serif font-bold text-foreground group-hover:text-gold transition-colors">
                  {job.title}
                </h3>

                <p className="text-xs sm:text-sm text-muted leading-relaxed">
                  {job.description}
                </p>

                {/* Key Skills */}
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {job.skills.map(skill => (
                    <span
                      key={skill}
                      className="text-[11px] px-2 py-0.5 rounded bg-white/5 text-muted border border-border/60"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>

              {/* Action Button */}
              <div className="shrink-0 flex items-center">
                <Link
                  to={`/contact?subject=${encodeURIComponent(`Job Application: ${job.title}`)}&service=Careers`}
                  className="w-full sm:w-auto"
                >
                  <Button variant="gold" size="md" className="w-full sm:w-auto gap-2 group-hover:shadow-gold/30">
                    <span>Apply Now</span>
                    <ArrowRight size={14} className="group-hover:translate-x-1 transition-transform" />
                  </Button>
                </Link>
              </div>
            </Card>
          ))}
        </div>
      </ContentSection>

      {/* 4. General Open Application Section */}
      <ContentSection containerClassName="max-w-4xl">
        <div className="p-8 sm:p-10 rounded-2xl bg-gradient-to-r from-deep via-navy to-deep border border-gold/30 text-white flex flex-col md:flex-row items-center justify-between gap-6 shadow-2xl relative overflow-hidden">
          <div className="space-y-3 relative z-10">
            <span className="inline-flex items-center gap-1.5 text-xs uppercase tracking-widest text-gold font-mono font-bold">
              <Sparkles size={14} /> Open Call for Builders
            </span>
            <h3 className="text-2xl sm:text-3xl font-serif font-bold">
              Don't see your specific discipline listed?
            </h3>
            <p className="text-xs sm:text-sm text-slate-300 max-w-xl leading-relaxed">
              We are constantly seeking brilliant engineers, UI/UX systems developers, and enterprise specialists. Send us your CV or portfolio and pitch what you’d like to build with us.
            </p>
          </div>

          <Link
            to="/contact?subject=General%20Career%20Inquiry&service=Careers"
            className="shrink-0 relative z-10 w-full sm:w-auto"
          >
            <Button variant="outline" size="lg" className="w-full sm:w-auto text-white border-white/40 hover:border-gold hover:text-gold hover:bg-white/10 gap-2 font-semibold">
              <Send size={15} />
              <span>Submit General CV</span>
            </Button>
          </Link>
        </div>
      </ContentSection>

      {/* 5. Standard Footer CTA */}
      <CtaBanner
        badge="Have Questions?"
        title="Want to Learn More About Working at AXINIX?"
        subtitle="Connect with our talent acquisition and engineering leadership team to discuss culture, technical stacks, or future initiatives."
        primaryAction={{ label: 'Contact Talent Team', to: '/contact?subject=Talent%20Inquiry' }}
        secondaryAction={{ label: 'Explore Our Solutions', to: '/solutions' }}
      />
    </div>
  );
}

