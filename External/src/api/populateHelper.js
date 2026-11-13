/**
 * Standardized Populate Helper Client
 * Interconnects with the Django Populate Engine (`/api/populate/read/:model`).
 * Implements Resilient Smart Hydration:
 * Fetches live data from backend with fallback to baseline domain data (`data.js`).
 */

import {
  SOLUTIONS,
  INDUSTRIES,
  SERVICES,
  PORTFOLIO,
  INSIGHTS,
  TESTIMONIALS,
  COMPANY_STATS,
  ANNOUNCEMENTS,
  CATEGORIES,
  PRODUCTS,
} from './data';
import { apiClient, recordAuditLog } from './client';
import { generateCorrelationId } from '../utils/formatters';

const memoryCache = new Map();

const MODEL_BACKEND_MAP = {
  solutions: 'showcase_solution',
  solution: 'showcase_solution',
  industries: 'showcase_industry',
  industry: 'showcase_industry',
  services: 'showcase_service',
  service: 'showcase_service',
  portfolio: 'showcase_portfolio',
  testimonials: 'showcase_testimonial',
  testimonial: 'showcase_testimonial',
  stats: 'showcase_stat',
  announcements: 'showcase_announcement',
  categories: 'showcase_category',
  category: 'showcase_category',
  products: 'showcase_product',
  product: 'showcase_product',
  company: 'company_profile',
  profile: 'company_profile',
  sections: 'site_section_content',
  modules: 'module',
  module: 'module',
};

function getBaselineData(model) {
  switch (model) {
    case 'solutions':
    case 'solution':
      return [...SOLUTIONS];
    case 'industries':
    case 'industry':
      return [...INDUSTRIES];
    case 'services':
    case 'service':
      return [...SERVICES];
    case 'portfolio':
      return [...PORTFOLIO];
    case 'testimonials':
    case 'testimonial':
      return [...TESTIMONIALS];
    case 'stats':
      return [...COMPANY_STATS];
    case 'announcements':
      return [...ANNOUNCEMENTS];
    case 'categories':
    case 'category':
      return [...CATEGORIES];
    case 'products':
    case 'product':
      return [...PRODUCTS];
    case 'insights':
      return [...INSIGHTS];
    default:
      return [];
  }
}

export const populateHelper = {
  /**
   * Universal populate query interface
   * @param {string} model - target entity
   * @param {Object} options - { filter, search, depth = 1, page = 1, limit = 50, forceFresh = false }
   */
  async query(model, options = {}) {
    const requestId = generateCorrelationId();
    const {
      filter = {},
      search = '',
      depth = 1,
      page = 1,
      limit = Math.min(options.limit || 50, 50),
      forceFresh = false,
    } = options;

    const safeDepth = Math.min(depth, 3);
    const cacheKey = `${model}:${JSON.stringify(options)}`;

    if (!forceFresh && memoryCache.has(cacheKey)) {
      return memoryCache.get(cacheKey);
    }

    let dataset = [];
    const backendModel = MODEL_BACKEND_MAP[model] || model;

    // Attempt live fetch from Tracker backend with 1500ms timeout
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 1500);

      const res = await apiClient.populateRead(backendModel, {
        signal: controller.signal,
      });
      clearTimeout(timeoutId);

      const liveList = res?.data?.data;
      if (Array.isArray(liveList) && liveList.length > 0) {
        // Normalize fields if needed (e.g. slug -> id)
        dataset = liveList.map(item => ({
          ...item,
          id: item.slug || item.id,
        }));
      } else {
        dataset = getBaselineData(model);
      }
    } catch (err) {
      // Backend unavailable or timed out: fall back seamlessly to baseline data
      dataset = getBaselineData(model);
    }

    // Apply AST / property filters
    let results = dataset.filter((item) => {
      for (const [key, val] of Object.entries(filter)) {
        if (val !== undefined && val !== 'All' && item[key] !== val) {
          return false;
        }
      }
      return true;
    });

    // Apply text search
    if (search && search.trim()) {
      const q = search.toLowerCase().trim();
      results = results.filter((item) => {
        const titleMatch =
          item.title?.toLowerCase().includes(q) || item.name?.toLowerCase().includes(q);
        const descMatch =
          item.description?.toLowerCase().includes(q) ||
          item.subtitle?.toLowerCase().includes(q);
        const tagsMatch = item.tags?.some((t) => t.toLowerCase().includes(q));
        const featuresMatch = item.features?.some((f) =>
          typeof f === 'string' ? f.toLowerCase().includes(q) : false
        );
        return titleMatch || descMatch || tagsMatch || featuresMatch;
      });
    }

    // Pagination
    const total = results.length;
    const startIndex = (page - 1) * limit;
    const paginated = results.slice(startIndex, startIndex + limit);

    const response = {
      model,
      total,
      page,
      limit,
      depth: safeDepth,
      data: paginated,
      requestId,
    };

    memoryCache.set(cacheKey, response);
    recordAuditLog({
      action: 'POPULATE_QUERY',
      endpoint: `/api/populate/read/${backendModel}`,
      requestId,
      payload: { model, count: total },
      status: 200,
    });

    return response;
  },

  /**
   * Clears the in-memory cache
   */
  clearCache() {
    memoryCache.clear();
  },
};

export default populateHelper;
