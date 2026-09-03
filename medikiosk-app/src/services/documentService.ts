/**
 * MediKiosk — Medical Document Digitization Service
 * Connects to:
 * - POST /sessions/{id}/documents/upload
 * - GET /sessions/{id}/documents
 * - GET /sessions/{id}/documents/timeline
 * - GET /sessions/{id}/documents/{document_id}
 * - GET /sessions/{id}/documents/{document_id}/extraction
 */

import api from './api';
import type {
  DocumentUploadResult,
  DocumentTimelineEntry,
} from '@/lib/types';

export const documentService = {
  /**
   * Upload physical medical document (prescription, lab report, discharge summary).
   */
  async uploadDocument(
    sessionId: string,
    file: File | Blob,
    documentType: 'PRESCRIPTION' | 'LAB_REPORT' | 'DISCHARGE_SUMMARY' | 'IMAGING' | string
  ): Promise<DocumentUploadResult> {
    const formData = new FormData();
    formData.append('file', file);
    const backendDocType = documentType === 'IMAGING' ? 'IMAGING_SCAN' : documentType;
    formData.append('doc_type', backendDocType);
    formData.append('document_type', backendDocType);

    const { data } = await api.post<DocumentUploadResult>(
      `/sessions/${sessionId}/documents/upload`,
      formData
    );
    return data;
  },

  /**
   * List all documents uploaded for the intake session.
   */
  async listDocuments(sessionId: string) {
    const { data } = await api.get(`/sessions/${sessionId}/documents`);
    return data;
  },

  /**
   * Fetch structured chronological timeline of all prior records.
   */
  async getTimeline(sessionId: string): Promise<{
    timeline: DocumentTimelineEntry[];
    abnormal_count: number;
  }> {
    const { data } = await api.get<{
      timeline: DocumentTimelineEntry[];
      abnormal_count: number;
    }>(`/sessions/${sessionId}/documents/timeline`);
    return data;
  },

  /**
   * Get specific document details and extracted entities.
   */
  async getExtraction(sessionId: string, documentId: string) {
    const { data } = await api.get(
      `/sessions/${sessionId}/documents/${documentId}/extraction`
    );
    return data;
  },
};
