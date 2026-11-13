/**
 * Centralized API Client & Network Transport
 * Implements correlation ID tracking (X-Request-ID), payload sanitization,
 * JWT/Token authorization, and Populate API endpoints.
 */

import { generateCorrelationId } from '../utils/formatters';

const STORAGE_AUDIT_KEY = 'axinix_api_audit_log';
const STORAGE_TOKEN_KEY = 'axinix_admin_token';
const STORAGE_USER_KEY = 'axinix_admin_user';

export function getAdminToken() {
  try {
    return localStorage.getItem(STORAGE_TOKEN_KEY);
  } catch (e) {
    return null;
  }
}

export function setAdminSession(token, user) {
  try {
    if (token) {
      localStorage.setItem(STORAGE_TOKEN_KEY, token);
    } else {
      localStorage.removeItem(STORAGE_TOKEN_KEY);
    }
    if (user) {
      localStorage.setItem(STORAGE_USER_KEY, JSON.stringify(user));
    } else {
      localStorage.removeItem(STORAGE_USER_KEY);
    }
  } catch (e) {
    console.warn('Storage unavailable for admin session:', e);
  }
}

export function getAdminUser() {
  try {
    const raw = localStorage.getItem(STORAGE_USER_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch (e) {
    return null;
  }
}

export function clearAdminSession() {
  try {
    localStorage.removeItem(STORAGE_TOKEN_KEY);
    localStorage.removeItem(STORAGE_USER_KEY);
  } catch (e) {
    // ignore
  }
}

export function recordAuditLog(entry) {
  try {
    const existing = JSON.parse(localStorage.getItem(STORAGE_AUDIT_KEY) || '[]');
    const record = {
      requestId: entry.requestId || generateCorrelationId(),
      timestamp: new Date().toISOString(),
      action: entry.action || 'READ',
      endpoint: entry.endpoint || '/api',
      payload: entry.payload ? sanitizePayload(entry.payload) : null,
      status: entry.status || 200,
    };
    existing.unshift(record);
    if (existing.length > 100) existing.pop();
    localStorage.setItem(STORAGE_AUDIT_KEY, JSON.stringify(existing));
  } catch (e) {
    console.warn('Audit logging storage unavailable:', e);
  }
}

export function sanitizePayload(payload) {
  if (!payload || typeof payload !== 'object') return payload;
  const sanitized = { ...payload };
  const sensitiveKeys = ['password', 'token', 'secret', 'creditCard', 'cvv', 'auth'];
  for (const key of Object.keys(sanitized)) {
    if (sensitiveKeys.some(s => key.toLowerCase().includes(s))) {
      sanitized[key] = '***REDACTED***';
    }
  }
  return sanitized;
}

const API_BASE = (import.meta.env.VITE_API_URL || '').replace(/\/+$/, '');

async function request(endpoint, options = {}) {
  const requestId = generateCorrelationId();
  const token = getAdminToken();

  const headers = {
    'Content-Type': 'application/json',
    'x-request-id': requestId,
    ...(options.headers || {}),
  };

  if (token && !headers['Authorization']) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const url = endpoint.startsWith('http') ? endpoint : `${API_BASE}${endpoint}`;

  try {
    const res = await fetch(url, {
      ...options,
      headers,
    });

    const contentType = res.headers.get('content-type') || '';
    let responseData = null;
    if (contentType.includes('application/json')) {
      responseData = await res.json();
    } else {
      responseData = await res.text();
    }

    recordAuditLog({
      action: options.method || 'GET',
      endpoint,
      requestId,
      payload: options.body ? JSON.parse(options.body) : null,
      status: res.status,
    });

    if (!res.ok) {
      const errorMsg =
        (responseData && (responseData.error || responseData.message || responseData.detail)) ||
        `Request failed with status ${res.status}`;
      const err = new Error(errorMsg);
      err.status = res.status;
      err.data = responseData;
      throw err;
    }

    return { data: responseData, success: true, requestId, status: res.status };
  } catch (error) {
    recordAuditLog({
      action: options.method || 'GET',
      endpoint,
      requestId,
      payload: options.body ? JSON.parse(options.body) : null,
      status: error.status || 500,
    });
    throw error;
  }
}

export const apiClient = {
  get(endpoint, params = {}) {
    let url = endpoint;
    const query = new URLSearchParams();
    for (const [k, v] of Object.entries(params)) {
      if (v !== undefined && v !== null) query.append(k, v);
    }
    const qStr = query.toString();
    if (qStr) url += (url.includes('?') ? '&' : '?') + qStr;

    return request(url, { method: 'GET' });
  },

  post(endpoint, payload = {}) {
    return request(endpoint, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  put(endpoint, payload = {}) {
    return request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(payload),
    });
  },

  delete(endpoint) {
    return request(endpoint, { method: 'DELETE' });
  },

  // Auth helper
  async login(username, password) {
    const res = await request('/api/auth/login/', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });

    const payload = res.data;
    const token = payload.accessToken || payload.token || payload.data?.token || payload.data?.accessToken;
    const user = payload.data?.user || payload.user;

    if (token) {
      setAdminSession(token, user);
    }

    return { token, user, success: true };
  },

  logout() {
    clearAdminSession();
    return Promise.resolve({ success: true });
  },

  async changePassword(oldPassword, newPassword) {
    return request('/api/auth/change-password/', {
      method: 'POST',
      body: JSON.stringify({ oldPassword, newPassword }),
    });
  },

  // Populate helper methods
  populateRead(model, options = {}) {
    return apiClient.get(`/api/populate/read/${model}`, options);
  },

  populateCreate(model, data) {
    return apiClient.post(`/api/populate/create/${model}`, data);
  },

  populateUpdate(model, id, data) {
    return apiClient.post(`/api/populate/update/${model}/${id}`, data);
  },

  populateDelete(model, id) {
    return apiClient.post(`/api/populate/delete/${model}/${id}`);
  },
};
