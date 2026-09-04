<script setup>
import { ref, computed } from "vue";
import api from "../utils/api";
import { useAppStore } from "../store";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Bar } from "vue-chartjs";
import PipelineNav from "../components/PipelineNav.vue";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const store = useAppStore();

const isLoading = ref(false);
const errorMsg = ref("");
const successMsg = ref("");
const previewData = ref(null);
const chartData = ref(null);

const isDark = computed(() => store.theme === "dark");

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: { 
    legend: { display: false },
    tooltip: {
      backgroundColor: isDark.value ? "#1e293b" : "#ffffff",
      titleColor: isDark.value ? "#ffffff" : "#0f172a",
      bodyColor: isDark.value ? "#cbd5e1" : "#334155",
      borderColor: isDark.value ? "#334155" : "#e2e8f0",
      borderWidth: 1,
    }
  },
  scales: {
    x: { 
      ticks: { color: isDark.value ? "#94a3b8" : "#475569" }, 
      grid: { display: false } 
    },
    y: { 
      ticks: { color: isDark.value ? "#94a3b8" : "#475569" }, 
      grid: { color: isDark.value ? "#334155" : "#e2e8f0" } 
    },
  },
}));

const handleLabeling = async () => {
  if (!store.sessionId) {
    errorMsg.value =
      "Sesi tidak ditemukan. Pastikan Anda sudah melewati proses input data.";
    return;
  }

  isLoading.value = true;
  errorMsg.value = "";
  successMsg.value = "";

  try {
    const response = await api.post(
      "/api/sentiment/predict",
      {
        session_id: store.sessionId,
      }
    );

    previewData.value = response.data.preview;
    const dist = response.data.distribution;

    const labelNames = { 0: "Negatif", 1: "Netral", 2: "Positif" };
    // Minimalist flat colors
    const colors = { 0: "#ef4444", 1: "#64748b", 2: "#10b981" };

    const labels = Object.keys(dist).map((k) => labelNames[k] || k);
    const counts = Object.values(dist);
    const bgColors = Object.keys(dist).map((k) => colors[k] || "#3b82f6");

    chartData.value = {
      labels,
      datasets: [
        {
          label: "Jumlah Ulasan",
          backgroundColor: bgColors,
          data: counts,
          borderRadius: 6,
        },
      ],
    };

    const total = Object.values(dist).reduce((a, b) => a + b, 0);
    successMsg.value = `Klasifikasi sentimen selesai! Total ${total} ulasan berlabel — Positif: ${
      dist[2] || 0
    }, Netral: ${dist[1] || 0}, Negatif: ${dist[0] || 0}`;
  } catch (error) {
    errorMsg.value =
      "Gagal melakukan prediksi sentimen: " +
      (error.response?.data?.detail || error.message);
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <div class="space-y-6">
    <!-- Title -->
    <div>
      <h1 class="text-2xl font-bold text-slate-800 dark:text-white mb-1 transition-colors">Klasifikasi Sentimen</h1>
      <p class="text-slate-500 dark:text-slate-400 text-xs transition-colors">
        Lakukan klasifikasi sentimen otomatis pada ulasan dataset aktif menggunakan model Random Forest terlatih.
      </p>
    </div>

    <!-- Feedback -->
    <div
      v-if="errorMsg"
      class="p-4 bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20 rounded-xl text-red-700 dark:text-red-400 text-xs flex items-center gap-2 transition-all"
    >
      <svg
        class="w-4.5 h-4.5 flex-shrink-0"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2.5"
          d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
      {{ errorMsg }}
    </div>
    <div
      v-if="successMsg"
      class="p-4 bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/20 rounded-xl text-emerald-700 dark:text-emerald-450 text-xs flex items-center gap-2 transition-all"
    >
      <svg
        class="w-4.5 h-4.5 flex-shrink-0"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2.5"
          d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
      {{ successMsg }}
    </div>

    <!-- Action Card -->
    <div
      class="bg-white dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800/80 rounded-2xl p-6 shadow-sm relative overflow-hidden transition-all duration-200"
    >
      <div
        class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6"
      >
        <div>
          <h3 class="text-sm font-bold text-slate-800 dark:text-slate-200 transition-colors">
            Klasifikasikan Dataset
          </h3>
          <p class="text-xs text-slate-400 dark:text-slate-500 transition-colors">
            Memprediksi polaritas (Positif, Netral, Negatif) dari dataset aktif.
          </p>
        </div>

        <button
          @click="handleLabeling"
          :disabled="isLoading || !store.sessionId"
          class="flex items-center justify-center px-6 py-2.5 bg-emerald-600 hover:bg-emerald-500 dark:bg-emerald-500 dark:hover:bg-emerald-400 text-white text-xs font-semibold rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
        >
          <svg
            v-if="isLoading"
            class="animate-spin -ml-1 mr-2 h-4 w-4"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              class="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              stroke-width="4"
            ></circle>
            <path
              class="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            ></path>
          </svg>
          <span>{{ isLoading ? "Mengklasifikasi..." : "Prediksi Sentimen" }}</span>
        </button>
      </div>

      <!-- Preview Section -->
      <div
        v-if="chartData && !isLoading"
        class="grid grid-cols-1 lg:grid-cols-3 gap-6"
      >
        <!-- Bar Chart Container -->
        <div
          class="lg:col-span-1 h-72 bg-slate-50 dark:bg-slate-800/20 rounded-xl p-4 border border-slate-200 dark:border-slate-800"
        >
          <h4 class="text-xs font-bold text-slate-500 dark:text-slate-400 mb-4 text-center uppercase tracking-wider">
            Distribusi Sentimen
          </h4>
          <div class="h-52">
            <Bar :data="chartData" :options="chartOptions" />
          </div>
        </div>

        <!-- Preview Table -->
        <div
          class="lg:col-span-2 overflow-auto max-h-72 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800"
        >
          <table class="w-full text-left text-xs text-slate-650 dark:text-slate-400">
            <thead class="text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase bg-slate-50 dark:bg-slate-850 border-b border-slate-200 dark:border-slate-800 sticky top-0 z-10">
              <tr>
                <th class="px-5 py-3">Ulasan Bersih (Clean Text)</th>
                <th class="px-5 py-3 w-28 text-center">Hasil Klasifikasi</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(row, idx) in previewData"
                :key="idx"
                class="border-b border-slate-200 dark:border-slate-800/60 hover:bg-slate-50 dark:hover:bg-slate-800/30 text-[11px]"
              >
                <td class="px-5 py-3 max-w-[200px] truncate" :title="row.clean">
                  {{ row.clean }}
                </td>

                <td class="px-5 py-3 text-center font-bold">
                  <span
                    v-if="row.sentiment_label === 2"
                    class="text-emerald-600 dark:text-emerald-400"
                    >Positif</span
                  >
                  <span
                    v-else-if="row.sentiment_label === 0"
                    class="text-red-650 dark:text-red-400"
                    >Negatif</span
                  >
                  <span v-else class="text-slate-500 dark:text-slate-400">Netral</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    <PipelineNav :current="5" />
  </div>
</template>
