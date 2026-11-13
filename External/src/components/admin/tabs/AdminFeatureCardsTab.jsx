import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  Save,
  Plus,
  Edit2,
  Trash2,
  ArrowUp,
  ArrowDown,
  Eye,
  EyeOff,
  Layers,
  CheckCircle2,
  Columns,
} from 'lucide-react';
import { apiClient } from '../../../api/client';
import { useToast } from '../../../context/ToastContext';
import { ItemEditModal } from '../ItemEditModal';
import { DEFAULT_FEATURE_CARDS } from '../../features';

const CARD_FIELDS = [
  { name: 'id', label: 'Section Anchor / ID', required: true, hint: 'e.g. dest-solutions, dest-industries' },
  { name: 'title', label: 'Card Title', required: true, placeholder: 'e.g. Enterprise Solutions, Industry Verticals' },
  { name: 'eyebrow', label: 'Eyebrow Tag', placeholder: 'e.g. Enterprise Core, Domain Tailored' },
  { name: 'description', label: 'Description', type: 'textarea', rows: 3 },
  { name: 'image', label: 'Preview Image URL / Path', placeholder: 'e.g. /hero_concept_2.jpg or https://...' },
  { name: 'benefits', label: 'Benefit Bullets (List)', type: 'array-strings', hint: 'Add key benefit bullets' },
  { name: 'cta_label', label: 'CTA Button Text', placeholder: 'e.g. Explore Solutions' },
  { name: 'cta_link', label: 'Destination Route or Anchor', placeholder: 'e.g. /solutions or #dest-solutions' },
  { name: 'is_active', label: 'Active on Website', type: 'switch', default: true },
];

export function AdminFeatureCardsTab() {
  const [loading, setLoading] = useState(true);
  const [savingHeader, setSavingHeader] = useState(false);
  const [sectionDoc, setSectionDoc] = useState(null);

  const [headerState, setHeaderState] = useState({
    eyebrow: 'Complete Ecosystem',
    title: 'Everything Your Business Needs. All in One Unified Platform.',
    description: 'Explore our enterprise software suites, industry-specific architectures, specialized engineering services, and packaged software products.',
  });

  const [cards, setCards] = useState([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingCard, setEditingCard] = useState(null);
  const [editingIndex, setEditingIndex] = useState(-1);
  const [isSavingCard, setIsSavingCard] = useState(false);

  const { addToast } = useToast();

  const fetchSectionData = async () => {
    setLoading(true);
    try {
      const res = await apiClient.populateRead('site_section_content');
      const list = res?.data?.data || [];
      const doc = list.find((s) => s.section_key === 'alternating_feature_cards');

      if (doc) {
        setSectionDoc(doc);
        setHeaderState({
          eyebrow: doc.badge || 'Complete Ecosystem',
          title: doc.title || 'Everything Your Business Needs. All in One Unified Platform.',
          description: doc.subtitle || 'Explore our enterprise software suites, industry-specific architectures, specialized engineering services, and packaged software products.',
        });

        const rawCards = doc.content?.cards;
        if (Array.isArray(rawCards) && rawCards.length > 0) {
          setCards(rawCards);
        } else {
          setCards(DEFAULT_FEATURE_CARDS);
        }
      } else {
        setCards(DEFAULT_FEATURE_CARDS);
      }
    } catch (err) {
      console.error('Failed to load alternating feature cards:', err);
      addToast('Failed to load cards from database. Using baseline defaults.', 'error');
      setCards(DEFAULT_FEATURE_CARDS);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSectionData();
  }, []);

  const persistToDatabase = async (updatedHeader, updatedCards) => {
    const payload = {
      section_key: 'alternating_feature_cards',
      badge: updatedHeader.eyebrow,
      title: updatedHeader.title,
      subtitle: updatedHeader.description,
      content: {
        cards: updatedCards,
      },
      is_active: true,
    };

    if (sectionDoc?.id) {
      await apiClient.populateUpdate('site_section_content', sectionDoc.id, payload);
    } else {
      const res = await apiClient.populateCreate('site_section_content', payload);
      if (res?.data?.data) {
        setSectionDoc(res.data.data);
      }
    }
  };

  const handleSaveHeader = async () => {
    setSavingHeader(true);
    try {
      await persistToDatabase(headerState, cards);
      addToast('Section header saved successfully!', 'success');
      fetchSectionData();
    } catch (err) {
      addToast(err.message || 'Failed to save header', 'error');
    } finally {
      setSavingHeader(false);
    }
  };

  const handleOpenAddCard = () => {
    setEditingCard({
      id: `dest-${cards.length + 1}`,
      title: '',
      eyebrow: '',
      description: '',
      image: '',
      benefits: ['', '', ''],
      cta_label: '',
      cta_link: '',
      is_active: true,
    });
    setEditingIndex(-1);
    setModalOpen(true);
  };

  const handleOpenEditCard = (card, idx) => {
    setEditingCard({
      id: card.id,
      title: card.title,
      eyebrow: card.eyebrow || '',
      description: card.description || '',
      image: card.image || '',
      benefits: Array.isArray(card.benefits) ? [...card.benefits] : [],
      cta_label: card.cta?.label || card.cta_label || '',
      cta_link: card.cta?.to || card.cta?.targetId || card.cta_link || '',
      is_active: card.is_active !== false,
    });
    setEditingIndex(idx);
    setModalOpen(true);
  };

  const handleSaveCardModal = async (formData) => {
    setIsSavingCard(true);
    try {
      const formattedCard = {
        id: formData.id || `dest-${Date.now()}`,
        title: formData.title,
        eyebrow: formData.eyebrow,
        description: formData.description,
        image: formData.image,
        benefits: (formData.benefits || []).filter((b) => b && b.trim().length > 0),
        cta: {
          label: formData.cta_label || 'Explore more',
          to: formData.cta_link?.startsWith('/') ? formData.cta_link : undefined,
          targetId: !formData.cta_link?.startsWith('/') ? formData.cta_link : undefined,
        },
        cta_label: formData.cta_label,
        cta_link: formData.cta_link,
        is_active: formData.is_active !== false,
        order: editingIndex >= 0 ? cards[editingIndex]?.order || editingIndex + 1 : cards.length + 1,
      };

      let newCards = [...cards];
      if (editingIndex >= 0) {
        newCards[editingIndex] = formattedCard;
      } else {
        newCards.push(formattedCard);
      }

      await persistToDatabase(headerState, newCards);
      setCards(newCards);
      setModalOpen(false);
      addToast(
        editingIndex >= 0
          ? `Card '${formattedCard.title}' updated successfully!`
          : `Card '${formattedCard.title}' added successfully!`,
        'success'
      );
    } catch (err) {
      addToast(err.message || 'Failed to save card', 'error');
    } finally {
      setIsSavingCard(false);
    }
  };

  const handleToggleCardActive = async (idx) => {
    try {
      const updatedCards = cards.map((c, i) =>
        i === idx ? { ...c, is_active: c.is_active === false ? true : false } : c
      );
      await persistToDatabase(headerState, updatedCards);
      setCards(updatedCards);
      addToast('Card visibility updated!', 'success');
    } catch (err) {
      addToast(err.message || 'Failed to update visibility', 'error');
    }
  };

  const handleDeleteCard = async (idx) => {
    const card = cards[idx];
    if (!window.confirm(`Are you sure you want to delete card '${card.title || 'Untitled'}'?`)) {
      return;
    }

    try {
      const updatedCards = cards.filter((_, i) => i !== idx);
      await persistToDatabase(headerState, updatedCards);
      setCards(updatedCards);
      addToast(`Card '${card.title}' deleted successfully!`, 'success');
    } catch (err) {
      addToast(err.message || 'Failed to delete card', 'error');
    }
  };

  const handleMove = async (idx, direction) => {
    const targetIdx = idx + direction;
    if (targetIdx < 0 || targetIdx >= cards.length) return;

    try {
      const updatedCards = [...cards];
      const temp = updatedCards[idx];
      updatedCards[idx] = updatedCards[targetIdx];
      updatedCards[targetIdx] = temp;

      // Update order indexes
      const reordered = updatedCards.map((c, i) => ({ ...c, order: i + 1 }));
      await persistToDatabase(headerState, reordered);
      setCards(reordered);
      addToast('Card sequence reordered (alternating layout adjusted)!', 'success');
    } catch (err) {
      addToast(err.message || 'Failed to reorder cards', 'error');
    }
  };

  if (loading) {
    return (
      <div className="py-12 text-center text-slate-400 text-sm">
        Loading Feature Cards CMS...
      </div>
    );
  }

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* 1. Header & Intro */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Columns className="text-gold" size={20} />
            <span>Alternating Feature Cards Showcase</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Manage the section header and the alternating split cards stream displayed on the website.
          </p>
        </div>

        <button
          onClick={handleOpenAddCard}
          className="px-4 py-2 bg-gold hover:bg-gold-hover text-slate-950 font-semibold text-xs rounded-xl flex items-center gap-2 shadow-md shadow-gold/15 transition-all self-start sm:self-auto"
        >
          <Plus size={15} />
          <span>Add Feature Card</span>
        </button>
      </div>

      {/* 2. Section Header Configuration Form */}
      <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <Sparkles className="text-gold" size={16} />
            <h3 className="font-semibold text-sm text-white">Section Header Settings</h3>
          </div>
          <button
            onClick={handleSaveHeader}
            disabled={savingHeader}
            className="px-4 py-1.5 text-xs font-semibold text-slate-950 bg-gold hover:bg-gold-hover rounded-lg transition-colors flex items-center gap-1.5 disabled:opacity-50"
          >
            <Save size={13} />
            {savingHeader ? 'Saving...' : 'Save Header'}
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              Eyebrow Badge Text
            </label>
            <input
              type="text"
              value={headerState.eyebrow}
              onChange={(e) => setHeaderState({ ...headerState, eyebrow: e.target.value })}
              className="w-full px-3 py-1.5 text-xs bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-gold"
              placeholder="e.g. Platform Capabilities"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              Primary Section Headline
            </label>
            <input
              type="text"
              value={headerState.title}
              onChange={(e) => setHeaderState({ ...headerState, title: e.target.value })}
              className="w-full px-3 py-1.5 text-xs bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-gold"
              placeholder="e.g. Engineered for Modern Enterprise Operations"
            />
          </div>

          <div className="sm:col-span-2">
            <label className="block text-xs font-medium text-slate-300 mb-1">
              Section Subtitle / Description
            </label>
            <textarea
              rows={2}
              value={headerState.description}
              onChange={(e) => setHeaderState({ ...headerState, description: e.target.value })}
              className="w-full px-3 py-1.5 text-xs bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-gold"
              placeholder="Contextual narrative explaining the platform feature stream..."
            />
          </div>
        </div>
      </div>

      {/* 3. Cards List with Alternating Position Previews */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
            <Layers size={16} className="text-gold" />
            <span>Configured Cards ({cards.length})</span>
          </h3>
          <span className="text-[11px] text-slate-400">
            Cards automatically alternate left and right down the page based on their position.
          </span>
        </div>

        {cards.length === 0 ? (
          <div className="p-8 text-center bg-slate-900 border border-slate-800 rounded-2xl text-slate-400 text-xs">
            No feature cards configured. Click &quot;Add Feature Card&quot; to create one.
          </div>
        ) : (
          <div className="space-y-3">
            {cards.map((card, idx) => {
              const isEven = idx % 2 === 0;
              const isPublished = card.is_active !== false;

              return (
                <div
                  key={card.id || idx}
                  className={`p-4 rounded-xl border transition-all ${
                    isPublished
                      ? 'bg-slate-900/90 border-slate-800 hover:border-slate-700'
                      : 'bg-slate-950/60 border-slate-800/60 opacity-60'
                  }`}
                >
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    {/* Left: Card Overview + Alternating Indicator */}
                    <div className="space-y-1.5 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="w-5 h-5 rounded-md bg-slate-800 text-slate-300 text-[10px] font-bold flex items-center justify-center">
                          {idx + 1}
                        </span>

                        <h4 className="font-semibold text-sm text-white truncate">
                          {card.title || 'Untitled Card'}
                        </h4>

                        {card.eyebrow && (
                          <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700">
                            {card.eyebrow}
                          </span>
                        )}

                        {/* Layout Orientation Badge */}
                        <span
                          className={`text-[10px] px-2 py-0.5 rounded-full font-mono border ${
                            isEven
                              ? 'bg-blue-500/10 text-blue-400 border-blue-500/20'
                              : 'bg-teal-500/10 text-teal-400 border-teal-500/20'
                          }`}
                        >
                          {isEven ? 'Layout: [Text Left | Panel Right]' : 'Layout: [Panel Left | Text Right]'}
                        </span>
                      </div>

                      <p className="text-xs text-slate-400 line-clamp-1">
                        {card.description || 'No description provided.'}
                      </p>

                      {/* Benefits count & CTA preview */}
                      <div className="flex items-center gap-3 text-[11px] text-slate-500 pt-1">
                        <span>
                          {Array.isArray(card.benefits) ? card.benefits.length : 0} Benefit Bullets
                        </span>
                        <span>•</span>
                        <span>
                          CTA: &quot;{card.cta?.label || card.cta_label || 'Explore'}&quot; →{' '}
                          {card.cta?.to || card.cta?.targetId || card.cta_link || 'Anchor'}
                        </span>
                      </div>
                    </div>

                    {/* Right: Actions */}
                    <div className="flex items-center gap-1.5 shrink-0 self-end md:self-center">
                      {/* Reorder Buttons */}
                      <button
                        onClick={() => handleMove(idx, -1)}
                        disabled={idx === 0}
                        title="Move Up (Flips alternating side)"
                        className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg disabled:opacity-20"
                      >
                        <ArrowUp size={14} />
                      </button>

                      <button
                        onClick={() => handleMove(idx, 1)}
                        disabled={idx === cards.length - 1}
                        title="Move Down (Flips alternating side)"
                        className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg disabled:opacity-20"
                      >
                        <ArrowDown size={14} />
                      </button>

                      {/* Toggle Visibility */}
                      <button
                        onClick={() => handleToggleCardActive(idx)}
                        title={isPublished ? 'Hide from website' : 'Publish to website'}
                        className={`p-1.5 rounded-lg transition-colors ${
                          isPublished
                            ? 'text-emerald-400 hover:bg-emerald-500/10'
                            : 'text-slate-500 hover:bg-slate-800'
                        }`}
                      >
                        {isPublished ? <Eye size={14} /> : <EyeOff size={14} />}
                      </button>

                      {/* Edit Card */}
                      <button
                        onClick={() => handleOpenEditCard(card, idx)}
                        className="p-1.5 text-slate-300 hover:text-gold hover:bg-slate-800 rounded-lg transition-colors"
                        title="Edit Card"
                      >
                        <Edit2 size={14} />
                      </button>

                      {/* Delete Card */}
                      <button
                        onClick={() => handleDeleteCard(idx)}
                        className="p-1.5 text-slate-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
                        title="Delete Card"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Edit Modal */}
      <ItemEditModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        onSave={handleSaveCardModal}
        title={editingIndex >= 0 ? `Edit Card: ${editingCard?.title}` : 'Add New Feature Card'}
        fields={CARD_FIELDS}
        initialData={editingCard}
        isSaving={isSavingCard}
      />
    </div>
  );
}

