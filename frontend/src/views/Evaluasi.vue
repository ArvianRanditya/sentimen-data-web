<script setup>
import { computed } from "vue";
import { useAppStore } from "../store";
import PipelineNav from "../components/PipelineNav.vue";

const store = useAppStore();

const report = computed(() => store.evaluationReport);
const cm = computed(() => store.confusionMatrix);
const cmLabels = computed(() => store.confusionMatrixLabels);
const testAcc = computed(() => store.testAccuracy);
const trainAcc = computed(() => store.trainAccuracy);

const fmt = (num) =>
  num !== undefined && num !== null ? Number(num).toFixed(4) : "-";
const pct = (num) =>
  num !== undefined && num !== null
    ? (Number(num) * 100).toFixed(1) + "%"
    : "-";

const labelName = (k) =>
  ({ 0: "Negatif", 1: "Netral", 2: "Positif" }[k] || `Kelas ${k}`);

const classesList = computed(() => {
  if (!report.value) return [];
  return Object.keys(report.value).filter(
    (k) => !["accuracy", "macro avg", "weighted avg"].includes(k)
  );
});

// Confusion matrix cell coloring
const cmMax = computed(() => {
  if (!cm.value) return 1;
  return Math.max(...cm.value.flat());
});

const isDark = computed(() => store.theme === "dark");

const cmCellStyle = (val, row, col) => {
  const intensity = val / cmMax.value;
  const isCorrect = row === col;
  if (isCorrect) {
    const textColor = intensity > 0.4 ? "#ffffff" : (isDark.value ? "#34d399" : "#047857");
    return `background: rgba(16, 185, 129, ${Math.max(0.1, intensity * 0.8)}); color: ${textColor};`;
  } else {
    const textColor = intensity > 0.4 ? "#ffffff" : (isDark.value ? "#94a3b8" : "#475569");
    return `background: rgba(148, 163, 184, ${Math.max(0.03, intensity * 0.35)}); color: ${textColor};`;
  }
};
</script>

<template>
  <div class="space-y-6">
    <!-- Title -->
    <div>
      <h1 class="text-2xl font-bold text-slate-800 dark:text-white mb-1 transition-colors">
        Evaluasi Performa Model
      </h1>
      <p class="text-slate-500 dark:text-slate-400 text-xs transition-colors">
        Metrik evaluasi lengkap model Random Forest berdasarkan data uji (testing).
      </p>
    </div>

    <!-- Empty State -->
    <div
      v-if="!report"
      class="bg-amber-50 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-500/20 rounded-2xl p-8 text-center"
    >
      <svg
        class="w-12 h-12 mx-auto mb-3 text-amber-500"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="1.5"
          d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
      <h3 class="text-sm font-bold text-amber-800 dark:text-amber-400 mb-1">Evaluasi Belum Tersedia</h3>
      <p class="text-xs text-slate-500 dark:text-slate-450 mb-3">
        Silakan lakukan pelatihan model terlebih dahulu di menu <strong>Training Model</strong>.
      </p>
    </div>

    <div v-else class="space-y-6">
      <!-- Accuracy Cards (Train vs Test) -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- Train accuracy -->
        <div
          class="bg-white dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800/80 rounded-2xl p-5 text-center shadow-sm transition-all"
        >
          <p class="text-slate-400 dark:text-slate-500 text-xs mb-1 uppercase tracking-wider font-semibold">
            Train Accuracy
          </p>
          <p class="text-3xl font-black text-blue-600 dark:text-blue-400">{{ pct(trainAcc) }}</p>
          <p class="text-[10px] text-slate-400 dark:text-slate-600 mt-1">(Data Latih)</p>
        </div>

        <!-- Test accuracy -->
        <div
          class="bg-white dark:bg-slate-900/50 border border-emerald-200 dark:border-emerald-500/20 rounded-2xl p-5 text-center shadow-sm transition-all"
        >
          <p class="text-emerald-600 dark:text-emerald-450 text-xs mb-1 uppercase tracking-wider font-semibold">
            Test Accuracy
          </p>
          <p class="text-3xl font-black text-emerald-600 dark:text-emerald-400">{{ pct(testAcc) }}</p>
          <p class="text-[10px] text-slate-400 dark:text-slate-600 mt-1">(Data Uji)</p>
        </div>

        <!-- F1 Score -->
        <div
          class="bg-white dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800/80 rounded-2xl p-5 text-center shadow-sm transition-all"
        >
          <p class="text-slate-400 dark:text-slate-500 text-xs mb-1 uppercase tracking-wider font-semibold">
            Weighted F1-Score
          </p>
          <p class="text-3xl font-black text-purple-600 dark:text-purple-400">
            {{ fmt(report["weighted avg"]?.["f1-score"]) }}
          </p>
          <p class="text-[10px] text-slate-400 dark:text-slate-600 mt-1">(Pembobotan Kelas)</p>
        </div>
      </div>

      <!-- Classification Report Table -->
      <div class="bg-white dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800/80 rounded-2xl p-6 shadow-sm transition-all duration-200">
        <h3 class="text-sm font-bold text-slate-800 dark:text-slate-200 mb-4 transition-colors">
          Classification Report
        </h3>
        
        <div
          class="overflow-x-auto rounded-xl border border-slate-200 dark:border-slate-800/60 bg-white dark:bg-slate-900"
        >
          <table class="w-full text-left text-xs text-slate-600 dark:text-slate-400">
            <thead
              class="sticky top-0 z-10 text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase bg-slate-50 dark:bg-slate-850/80 border-b border-slate-200 dark:border-slate-800/80"
            >
              <tr>
                <th class="px-6 py-4 border-b border-slate-200 dark:border-slate-800/80">Kelas</th>
                <th class="px-6 py-4 border-b border-slate-200 dark:border-slate-800/80">Precision</th>
                <th class="px-6 py-4 border-b border-slate-200 dark:border-slate-800/80">Recall</th>
                <th class="px-6 py-4 border-b border-slate-200 dark:border-slate-800/80">F1-Score</th>
                <th class="px-6 py-4 border-b border-slate-200 dark:border-slate-800/80">Support</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="key in classesList"
                :key="key"
                class="border-b border-slate-200 dark:border-slate-800/60 hover:bg-slate-50 dark:hover:bg-slate-800/30 text-[11px]"
              >
                <td class="px-6 py-4 font-bold text-slate-700 dark:text-slate-200">
                  {{ labelName(Number(key)) }}
                </td>
                <td class="px-6 py-4 font-medium">{{ fmt(report[key].precision) }}</td>
                <td class="px-6 py-4 font-medium">{{ fmt(report[key].recall) }}</td>
                <td class="px-6 py-4 font-medium">{{ fmt(report[key]["f1-score"]) }}</td>
                <td class="px-6 py-4 text-slate-400 dark:text-slate-500 font-mono">{{ report[key].support }}</td>
              </tr>
            </tbody>
            <tfoot class="bg-slate-55/65 dark:bg-slate-800/30 border-t border-slate-200 dark:border-slate-800 font-medium text-[11px]">
              <tr class="border-b border-slate-200/50 dark:border-slate-800/50">
                <td class="px-6 py-3 font-bold text-slate-700 dark:text-slate-200">Macro Avg</td>
                <td class="px-6 py-3">{{ fmt(report["macro avg"].precision) }}</td>
                <td class="px-6 py-3">{{ fmt(report["macro avg"].recall) }}</td>
                <td class="px-6 py-3">{{ fmt(report["macro avg"]["f1-score"]) }}</td>
                <td class="px-6 py-3 text-slate-400 dark:text-slate-500 font-mono">{{ report["macro avg"].support }}</td>
              </tr>
              <tr>
                <td class="px-6 py-3 font-bold text-slate-700 dark:text-slate-200">Weighted Avg</td>
                <td class="px-6 py-3">{{ fmt(report["weighted avg"].precision) }}</td>
                <td class="px-6 py-3">{{ fmt(report["weighted avg"].recall) }}</td>
                <td class="px-6 py-3">{{ fmt(report["weighted avg"]["f1-score"]) }}</td>
                <td class="px-6 py-3 text-slate-400 dark:text-slate-500 font-mono">{{ report["weighted avg"].support }}</td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>

      <!-- Confusion Matrix Heatmap -->
      <div
        v-if="cm && cmLabels"
        class="bg-white dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800/80 rounded-2xl p-6 shadow-sm transition-all duration-200"
      >
        <h3 class="text-sm font-bold text-slate-800 dark:text-slate-200 mb-4 transition-colors">
          Confusion Matrix Heatmap
        </h3>

        <div class="overflow-x-auto">
          <table class="mx-auto text-xs">
            <thead>
              <tr>
                <th class="px-4 py-2 text-slate-400 dark:text-slate-500 text-[10px]"></th>
                <th
                  class="px-1 py-2 text-slate-400 dark:text-slate-500 text-[10px] uppercase font-bold text-center tracking-wider"
                  :colspan="cmLabels.length"
                >
                  ← Predicted →
                </th>
              </tr>
              <tr>
                <th class="px-4 py-2 text-slate-400 dark:text-slate-500 text-[10px] uppercase font-bold text-right tracking-wider">
                  Actual ↓
                </th>
                <th
                  v-for="lbl in cmLabels"
                  :key="lbl"
                  class="px-6 py-3 text-slate-700 dark:text-slate-350 font-bold text-center text-xs"
                >
                  {{ labelName(lbl) }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, rIdx) in cm" :key="rIdx">
                <td
                  class="px-4 py-3 text-slate-700 dark:text-slate-300 font-bold text-right pr-4 text-xs"
                >
                  {{ labelName(cmLabels[rIdx]) }}
                </td>
                <td
                  v-for="(val, cIdx) in row"
                  :key="cIdx"
                  class="px-6 py-4 text-center font-bold text-[15px] rounded-xl m-1 transition-all"
                  :style="cmCellStyle(val, rIdx, cIdx)"
                >
                  {{ val }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    <PipelineNav :current="4" />
  </div>
</template>
