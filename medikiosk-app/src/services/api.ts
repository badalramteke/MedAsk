/**
 * MediKiosk — Axios API Client
 * Configured to communicate with the FastAPI backend at /api/v1.
 * Includes correlation ID injection and error normalization.
 */

import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { API_BASE_URL } from '@/lib/constants';
import type { ApiError } from '@/lib/types';

// ─── Axios Instance ──────────────────────────────────────────────────
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// ─── Request Interceptor: Correlation ID ─────────────────────────────
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  // Generate a unique correlation ID per request for tracing
  const correlationId = `kiosk-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
  config.headers.set('X-Correlation-ID', correlationId);

  // If payload is FormData, remove Content-Type so browser sets boundary
  if (typeof FormData !== 'undefined' && config.data instanceof FormData) {
    config.headers.delete('Content-Type');
  }

  return config;
});

// ─── Response Interceptor: Error Normalization ───────────────────────
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiError>) => {
    if (error.response?.data) {
      // Backend returns structured error per ERROR_CODES.md
      const apiError = error.response.data;
      console.warn(
        `[API Error] ${apiError.error_code}: ${apiError.message}`,
        apiError.correlation_id
      );
    } else if (error.code === 'ECONNABORTED') {
      console.warn('[API Warning] Request timeout');
    } else if (!error.response) {
      console.warn(
        `[API Notice] Network error — backend unreachable at ${API_BASE_URL}. Operating in offline kiosk resilience mode.`
      );
    }
    return Promise.reject(error);
  }
);

export default api;
