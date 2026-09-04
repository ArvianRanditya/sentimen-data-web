import { defineStore } from "pinia";

const STORAGE_KEY = "sentimen_ai_store";

const loadFromStorage = () => {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    return saved ? JSON.parse(saved) : {};
  } catch {
    return {};
  }
};

const saveToStorage = (state) => {
  try {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        sessionId: state.sessionId,
        evaluationReport: state.evaluationReport,
        confusionMatrix: state.confusionMatrix,
        confusionMatrixLabels: state.confusionMatrixLabels,
        testAccuracy: state.testAccuracy,
        trainAccuracy: state.trainAccuracy,
        theme: state.theme,
      })
    );
  } catch {}
};

const saved = loadFromStorage();

export const useAppStore = defineStore("app", {
  state: () => ({
    sessionId: saved.sessionId ?? null,
    evaluationReport: saved.evaluationReport ?? null,
    confusionMatrix: saved.confusionMatrix ?? null,
    confusionMatrixLabels: saved.confusionMatrixLabels ?? null,
    testAccuracy: saved.testAccuracy ?? null,
    trainAccuracy: saved.trainAccuracy ?? null,
    theme: saved.theme ?? "dark",
  }),
  actions: {
    setSessionId(id) {
      this.sessionId = id;
      saveToStorage(this.$state);
    },
    setEvaluationReport(report) {
      this.evaluationReport = report;
      saveToStorage(this.$state);
    },
    setTrainingResults({ report, cm, cmLabels, testAcc, trainAcc }) {
      this.evaluationReport = report;
      this.confusionMatrix = cm;
      this.confusionMatrixLabels = cmLabels;
      this.testAccuracy = testAcc;
      this.trainAccuracy = trainAcc;
      saveToStorage(this.$state);
    },
    toggleTheme() {
      this.theme = this.theme === "dark" ? "light" : "dark";
      saveToStorage(this.$state);
    },
    clearSession() {
      this.sessionId = null;
      this.evaluationReport = null;
      this.confusionMatrix = null;
      this.confusionMatrixLabels = null;
      this.testAccuracy = null;
      this.trainAccuracy = null;
      localStorage.removeItem(STORAGE_KEY);
    },
  },
});
