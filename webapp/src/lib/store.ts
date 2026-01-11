import { create } from "zustand";
import { persist } from "zustand/middleware";

// ------------------------------
// 🧱 Types
// ------------------------------
interface AnalysisData {
  file_id: string;
  scam_class?: any;
  risk?: any;
  entities?: any[];
  osint_hits?: any[];
  url_qr_findings?: any[];
  analyzed_at?: string;
}

interface SatyaSetuAIState {
  // Core case data
  currentCaseId: string | null;
  analysisCache: Record<string, AnalysisData>;

  // UI state
  isLoading: boolean;
  notification: string | null;

  // Actions
  setCaseId: (id: string | null) => void;
  setAnalysis: (file_id: string, data: AnalysisData) => void;
  setLoading: (v: boolean) => void;
  setNotification: (msg: string | null) => void;

  // Utils
  clearCache: () => void;
  getCaseData: (id: string) => AnalysisData | null;
}

// ------------------------------
// ⚙️ Store Implementation
// ------------------------------
export const useSatyaSetuAIStore = create<SatyaSetuAIState>()(
  persist(
    (set, get) => ({
      // --- State defaults ---
      currentCaseId: null,
      analysisCache: {},
      isLoading: false,
      notification: null,

      // --- Actions ---
      setCaseId: (id) => set({ currentCaseId: id }),

      setAnalysis: (file_id, data) => {
        const cache = { ...get().analysisCache, [file_id]: data };
        set({ analysisCache: cache });
      },

      setLoading: (v) => set({ isLoading: v }),

      setNotification: (msg) => {
        set({ notification: msg });
        if (msg) {
          // Auto-clear after 3s
          setTimeout(() => set({ notification: null }), 3000);
        }
      },

      clearCache: () => set({ analysisCache: {}, currentCaseId: null }),

      getCaseData: (id) => get().analysisCache[id] || null,
    }),
    {
      name: "satya-setu-ai-storage", // 🔐 LocalStorage key
    }
  )
);
