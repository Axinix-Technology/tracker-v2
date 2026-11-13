import axiosInstance from '../api/axiosInstance';

/**
 * Work Contribution & Shareholder Equity Service
 * Connects directly to the Populate Engine and the AI Parsing subsystem.
 */
export const contributionService = {
  // 1. Read contributions with dynamic filters and population
  async getContributions(filters = {}) {
    const payload = {
      filter: {
        lifecycle_status: 1,
        ...filters,
      },
      populate: ['user', 'primary_category', 'secondary_category', 'client', 'approved_by'],
      sort: { date: -1, created_at: -1 },
    };
    const res = await axiosInstance.post('/populate/read/work_contribution', payload)
      .catch(() => axiosInstance.post('/api/populate/read/work_contribution', payload));
    return res.data;
  },

  // 2. Fetch active category catalog
  async getCategories() {
    const payload = {
      filter: { status: 1 },
      sort: { scope: 1, base_points: -1, name: 1 },
    };
    const res = await axiosInstance.post('/populate/read/contribution_category', payload)
      .catch(() => axiosInstance.post('/api/populate/read/contribution_category', payload));
    return res.data?.data || [];
  },

  // 3. Fetch evaluation factors
  async getFactors() {
    const payload = {
      filter: { status: 1 },
      sort: { sort_order: 1 },
    };
    const res = await axiosInstance.post('/populate/read/contribution_factor', payload)
      .catch(() => axiosInstance.post('/api/populate/read/contribution_factor', payload));
    return res.data?.data || [];
  },

  // 4. AI WhatsApp text parse
  async aiParseText(text, date = null, memberId = null) {
    const res = await axiosInstance.post('/contributions/ai-parse/', {
      text,
      date,
      member_id: memberId,
    }).catch(() => axiosInstance.post('/api/contributions/ai-parse/', {
      text,
      date,
      member_id: memberId,
    }));
    return res.data;
  },

  // 5. Create single contribution
  async createContribution(data) {
    const res = await axiosInstance.post('/populate/create/work_contribution', data)
      .catch(() => axiosInstance.post('/api/populate/create/work_contribution', data));
    return res.data;
  },

  // 6. Bulk create contributions
  async bulkCreateContributions(items) {
    try {
      const res = await axiosInstance.post('/populate/bulk-create/work_contribution', { items })
        .catch(() => axiosInstance.post('/api/populate/bulk-create/work_contribution', { items }));
      return res.data;
    } catch {
      // Fallback: create sequentially if bulk-create payload differs
      const results = [];
      for (const it of items) {
        const r = await this.createContribution(it);
        results.push(r);
      }
      return { success: true, data: results };
    }
  },

  // 7. Update contribution (mark completed, adjust factors, resolve follow-up)
  async updateContribution(id, data) {
    const res = await axiosInstance.post(`/populate/update/work_contribution/${id}`, data)
      .catch(() => axiosInstance.put(`/api/populate/update/work_contribution/${id}`, data));
    return res.data;
  },

  // 8. Soft delete contribution
  async deleteContribution(id) {
    const res = await axiosInstance.post(`/populate/delete/work_contribution/${id}`, {})
      .catch(() => axiosInstance.delete(`/api/populate/delete/work_contribution/${id}`));
    return res.data;
  },
};

export default contributionService;

