/**
 * MediKiosk — Clinical Intake Store (Zustand)
 * Manages collected patient history, complaints, pain severity, documents, and summary.
 */

import { create } from 'zustand';
import type {
  QuestionResponse,
  ClinicalSummary,
  DocumentTimelineEntry,
} from '@/lib/types';

export interface IntakeState {
  // Chief Complaint & Symptoms
  chiefComplaint: string;
  bodyRegion: string | null;
  painSeverity: number; // 0 to 10
  symptomsList: string[];

  // SOCRATES Answers
  socratesAnswers: Record<string, string>;

  // AYUSH Assessment
  ayushAnswers: Record<string, string>;

  // Active Adaptive Question
  activeQuestion: QuestionResponse | null;

  // Medical Documents & OCR
  uploadedDocuments: Array<{
    id: string;
    filename: string;
    type: string;
    status: string;
    previewUrl?: string;
  }>;
  recordsTimeline: DocumentTimelineEntry[];

  // Final Summary
  clinicalSummary: ClinicalSummary | null;

  // Actions
  setChiefComplaint: (complaint: string) => void;
  setBodyRegion: (region: string) => void;
  setPainSeverity: (severity: number) => void;
  addSymptom: (symptom: string) => void;
  removeSymptom: (symptom: string) => void;
  setSocratesAnswer: (key: string, val: string) => void;
  setAyushAnswer: (key: string, val: string) => void;
  setActiveQuestion: (q: QuestionResponse | null) => void;
  addUploadedDocument: (doc: {
    id: string;
    filename: string;
    type: string;
    status: string;
    previewUrl?: string;
  }) => void;
  setRecordsTimeline: (timeline: DocumentTimelineEntry[]) => void;
  setClinicalSummary: (summary: ClinicalSummary | null) => void;
  resetIntake: () => void;
}

export const useIntakeStore = create<IntakeState>((set) => ({
  chiefComplaint: '',
  bodyRegion: null,
  painSeverity: 0,
  symptomsList: [],
  socratesAnswers: {},
  ayushAnswers: {},
  activeQuestion: null,
  uploadedDocuments: [],
  recordsTimeline: [],
  clinicalSummary: null,

  setChiefComplaint: (chiefComplaint) => set({ chiefComplaint }),
  setBodyRegion: (bodyRegion) => set({ bodyRegion }),
  setPainSeverity: (painSeverity) => set({ painSeverity }),
  addSymptom: (symptom) =>
    set((state) => ({
      symptomsList: state.symptomsList.includes(symptom)
        ? state.symptomsList
        : [...state.symptomsList, symptom],
    })),
  removeSymptom: (symptom) =>
    set((state) => ({
      symptomsList: state.symptomsList.filter((s) => s !== symptom),
    })),
  setSocratesAnswer: (key, val) =>
    set((state) => ({
      socratesAnswers: { ...state.socratesAnswers, [key]: val },
    })),
  setAyushAnswer: (key, val) =>
    set((state) => ({
      ayushAnswers: { ...state.ayushAnswers, [key]: val },
    })),
  setActiveQuestion: (activeQuestion) => set({ activeQuestion }),
  addUploadedDocument: (doc) =>
    set((state) => ({
      uploadedDocuments: [...state.uploadedDocuments, doc],
    })),
  setRecordsTimeline: (recordsTimeline) => set({ recordsTimeline }),
  setClinicalSummary: (clinicalSummary) => set({ clinicalSummary }),
  resetIntake: () =>
    set({
      chiefComplaint: '',
      bodyRegion: null,
      painSeverity: 0,
      symptomsList: [],
      socratesAnswers: {},
      ayushAnswers: {},
      activeQuestion: null,
      uploadedDocuments: [],
      recordsTimeline: [],
      clinicalSummary: null,
    }),
}));
