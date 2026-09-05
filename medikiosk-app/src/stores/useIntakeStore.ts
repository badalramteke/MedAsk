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

export type SymptomsTab = 'COMPLAINT' | 'BODY_MAP' | 'PAIN_SCALE' | 'ADAPTIVE_QUESTION';

export interface IntakeState {
  // Chief Complaint & Symptoms
  symptomsTab: SymptomsTab;
  chiefComplaint: string;
  bodyRegion: string | null;
  painSeverity: number; // 0 to 10
  symptomsList: string[];

  // SOCRATES Answers
  socratesAnswers: Record<string, string>;

  // AYUSH Assessment
  ayushAnswers: Record<string, string | string[]>;

  // Active Adaptive Question & History Stack
  activeQuestion: QuestionResponse | null;
  questionHistory: QuestionResponse[];
  freeTextAnswer: string;
  selectedOptionCode: string | null;
  selectedMultiCodes: string[];

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
  setSymptomsTab: (tab: SymptomsTab) => void;
  setChiefComplaint: (complaint: string) => void;
  setBodyRegion: (region: string) => void;
  setPainSeverity: (severity: number) => void;
  addSymptom: (symptom: string) => void;
  removeSymptom: (symptom: string) => void;
  setSocratesAnswer: (key: string, val: string) => void;
  setAyushAnswer: (key: string, val: string | string[]) => void;
  setActiveQuestion: (q: QuestionResponse | null) => void;
  pushQuestionHistory: (q: QuestionResponse) => void;
  popQuestionHistory: () => QuestionResponse | undefined;
  setFreeTextAnswer: (text: string) => void;
  setSelectedOptionCode: (code: string | null) => void;
  setSelectedMultiCodes: (codes: string[]) => void;
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
  symptomsTab: 'COMPLAINT',
  chiefComplaint: '',
  bodyRegion: null,
  painSeverity: 0,
  symptomsList: [],
  socratesAnswers: {},
  ayushAnswers: {},
  activeQuestion: null,
  questionHistory: [],
  freeTextAnswer: '',
  selectedOptionCode: null,
  selectedMultiCodes: [],
  uploadedDocuments: [],
  recordsTimeline: [],
  clinicalSummary: null,

  setSymptomsTab: (symptomsTab) => set({ symptomsTab }),
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
  pushQuestionHistory: (q) =>
    set((state) => ({
      questionHistory: [...state.questionHistory, q],
    })),
  popQuestionHistory: () => {
    let popped: QuestionResponse | undefined;
    set((state) => {
      if (state.questionHistory.length === 0) return state;
      const historyCopy = [...state.questionHistory];
      popped = historyCopy.pop();
      return { questionHistory: historyCopy };
    });
    return popped;
  },
  setFreeTextAnswer: (freeTextAnswer) => set({ freeTextAnswer }),
  setSelectedOptionCode: (selectedOptionCode) => set({ selectedOptionCode }),
  setSelectedMultiCodes: (selectedMultiCodes) => set({ selectedMultiCodes }),
  addUploadedDocument: (doc) =>
    set((state) => ({
      uploadedDocuments: [...state.uploadedDocuments, doc],
    })),
  setRecordsTimeline: (recordsTimeline) => set({ recordsTimeline }),
  setClinicalSummary: (clinicalSummary) => set({ clinicalSummary }),
  resetIntake: () =>
    set({
      symptomsTab: 'COMPLAINT',
      chiefComplaint: '',
      bodyRegion: null,
      painSeverity: 0,
      symptomsList: [],
      socratesAnswers: {},
      ayushAnswers: {},
      activeQuestion: null,
      questionHistory: [],
      freeTextAnswer: '',
      selectedOptionCode: null,
      selectedMultiCodes: [],
      uploadedDocuments: [],
      recordsTimeline: [],
      clinicalSummary: null,
    }),
}));
