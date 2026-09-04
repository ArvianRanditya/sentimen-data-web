<script setup>
import { ref, onMounted, computed } from "vue";
import api from "../utils/api";
import { useAppStore } from "../store";
import { useRouter } from "vue-router";
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
const router = useRouter();

const isLoading = ref(false);
const errorMsg = ref("");
const successMsg = ref("");
const notClustered = ref(false);
const topicsData = ref(null); // { clusterId: { words: [{word, score}], chartData } }
const clusterSummary = ref(null);

const clusterColors = [
  "rgba(16, 185, 129, 0.85)",
  "rgba(59, 130, 246, 0.85)",
  "rgba(245, 158, 11, 0.85)",
  "rgba(239, 68, 68, 0.85)",
  "rgba(168, 85, 247, 0.85)",
  "rgba(236, 72, 153, 0.85)",
];
const getColor = (id) => clusterColors[parseInt(id) % clusterColors.length];

const isDark = computed(() => store.theme === "dark");

const barOptions = computed(() => ({
  indexAxis: "y",
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
      callbacks: { label: (ctx) => ` TF-IDF: ${ctx.raw.toFixed(4)}` },
    },
  },
  scales: {
    x: { 
      ticks: { color: isDark.value ? "#94a3b8" : "#475569" }, 
      grid: { color: isDark.value ? "#334155" : "#e2e8f0" } 
    },
    y: {
      ticks: { color: isDark.value ? "#e2e8f0" : "#334155", font: { size: 11 } },
      grid: { display: false },
    },
  },
}));

const loadTopics = async () => {
  if (!store.sessionId) {
    errorMsg.value = "Sesi tidak ditemukan.";
    return;
  }
  isLoading.value = true;
  errorMsg.value = "";
  successMsg.value = "";
  notClustered.value = false;

  try {
    const res = await api.post("/api/cluster/topic", {
      session_id: store.sessionId,
    });
    const formatted = {};

    for (const [clusterId, words] of Object.entries(res.data.topics)) {
      formatted[clusterId] = {
        words,
        chartData: {
          labels: words.map((w) => w.word),
          datasets: [
            {
              label: "TF-IDF",
              backgroundColor: getColor(clusterId),
              data: words.map((w) => parseFloat(w.score.toFixed(4))),
              borderRadius: 4,
            },
          ],
        },
      };
    }
    topicsData.value = formatted;
    const numClusters = Object.keys(formatted).length;
    successMsg.value = `Topik berhasil dimuat untuk ${numClusters} cluster.`;

    // Build summary
    const ids = Object.keys(formatted).map(Number);
    clusterSummary.value = {
      total: ids.length,
    };
  } catch (err) {
    if (err.response?.status === 404) {
      notClustered.value = true;
    } else {
      errorMsg.value =
        "Gagal memuat topik: " + (err.response?.data?.detail || err.message);
    }
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  loadTopics();
});
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between mb-2">
      <div>
        <h1 class="text-2xl font-bold text-slate-800 dark:text-white mb-1 transition-colors">Topik Tiap Cluster</h1>
        <p class="text-slate-500 dark:text-slate-400 text-xs transition-colors">
          Analisis TF-IDF untuk mengekstraksi kata kunci yang paling dominan di setiap kelompok cluster.
        </p>
      </div>
      <button
        @click="loadTopics"
        class="flex items-center gap-1.5 px-4 py-2 text-xs font-semibold border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800/80 rounded-xl transition-colors cursor-pointer"
      >
        <svg
          class="w-3.5 h-3.5"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2.5"
            d="M4 4v5h.582m15.356 2A8.001 8.001 0 1121.21 7.89"
          />
        </svg>
        Refresh
      </button>
    </div>

    <!-- Not clustered warning -->
    <div
      v-if="notClustered"
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
      <h3 class="text-sm font-bold text-amber-800 dark:text-amber-400 mb-1">
        Clustering Belum Dieksekusi
      </h3>
      <p class="text-xs text-slate-500 dark:text-slate-450 mb-4">
        Lakukan proses pengelompokan ulasan terlebih dahulu di menu <strong>Clustering</strong>.
      </p>
      <button
        @click="router.push('/clustering')"
        class="inline-flex items-center px-4 py-2 bg-amber-600 hover:bg-amber-500 dark:bg-amber-500 dark:hover:bg-amber-400 text-white text-xs font-semibold rounded-lg shadow-sm transition-all cursor-pointer"
      >
        ← Kembali ke Clustering
      </button>
    </div>

    <!-- Error/Success Feedbacks -->
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
      class="p-4 bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/20 rounded-xl text-emerald-700 dark:text-emerald-455 text-xs flex items-center gap-2 transition-all"
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

    <!-- Loading screen -->
    <div
      v-if="isLoading"
      class="py-12 flex justify-center items-center text-emerald-600 dark:text-emerald-500"
    >
      <svg
        class="animate-spin h-8 w-8"
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
        />
        <path
          class="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
        />
      </svg>
      <span class="ml-3 text-sm font-semibold">Mengekstrak topik kata kunci...</span>
    </div>

    <!-- Global Insight Summary -->
    <div
      v-if="clusterSummary && !isLoading && !notClustered"
      class="p-4 bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-250/50 dark:border-emerald-500/20 rounded-2xl flex flex-wrap gap-6 text-xs transition-colors"
    >
      <div>
        <p class="text-slate-500 dark:text-slate-400 mb-0.5">Total Cluster Aktif</p>
        <p class="text-lg font-bold text-emerald-700 dark:text-emerald-400">
          {{ clusterSummary.total }}
        </p>
      </div>
    </div>

    <!-- Clusters loop list -->
    <div
      v-if="topicsData && !isLoading && !notClustered"
      class="space-y-6"
    >
      <div
        v-for="(data, clusterId) in topicsData"
        :key="clusterId"
        class="bg-white dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm"
      >
        <h3 class="text-sm font-bold text-slate-800 dark:text-white mb-4 flex items-center transition-colors">
          <span
            class="inline-block w-2.5 h-2.5 rounded-full mr-2"
            :style="{ backgroundColor: getColor(clusterId) }"
          ></span>
          Cluster {{ clusterId }}
        </h3>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Word Table -->
          <div
            class="max-h-[300px] overflow-auto rounded-xl border border-slate-200 dark:border-slate-800/60 bg-white dark:bg-slate-900"
          >
            <table class="w-full text-left text-xs text-slate-650 dark:text-slate-400">
              <thead
                class="sticky top-0 z-10 text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase bg-slate-50 dark:bg-slate-850 border-b border-slate-200 dark:border-slate-800"
              >
                <tr>
                  <th class="px-4 py-3 w-12">#</th>
                  <th class="px-4 py-3">Kata Kunci</th>
                  <th class="px-4 py-3">Skor TF-IDF</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(w, idx) in data.words"
                  :key="idx"
                  class="border-b border-slate-200 dark:border-slate-800/60 hover:bg-slate-55 dark:hover:bg-slate-800/30 text-[11px]"
                >
                  <td class="px-4 py-2 text-slate-400">{{ idx + 1 }}</td>
                  <td class="px-4 py-2 text-slate-700 dark:text-slate-200 font-semibold">
                    {{ w.word }}
                  </td>
                  <td class="px-4 py-2 text-emerald-600 dark:text-emerald-400 font-mono">
                    {{ w.score.toFixed(4) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Bar Chart -->
          <div class="h-72">
            <Bar :data="data.chartData" :options="barOptions" />
          </div>
        </div>

        <!-- CSS Word Cloud -->
        <div
          class="mt-5 p-4 bg-slate-50 dark:bg-slate-800/20 rounded-xl border border-slate-200 dark:border-slate-800 transition-colors"
        >
          <p class="text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-3">
            Word Cloud (Bobot Proporsional)
          </p>
          <div class="flex flex-wrap gap-2.5 items-center justify-center p-2">
            <span
              v-for="w in data.words"
              :key="w.word"
              class="px-2.5 py-0.5 rounded-full font-semibold transition-all hover:scale-105 cursor-default text-xs"
              :style="{
                fontSize: `${Math.max(
                  10,
                  Math.min(
                    22,
                    10 +
                      (w.score / Math.max(...data.words.map((x) => x.score))) *
                        12
                  )
                )}px`,
                opacity:
                  0.55 +
                  (w.score / Math.max(...data.words.map((x) => x.score))) * 0.45,
                backgroundColor: getColor(clusterId).replace('0.85', '0.08'),
                color: getColor(clusterId).replace('0.85', '1'),
              }"
            >
              {{ w.word }}
            </span>
          </div>
        </div>
      </div>
    </div>
    <PipelineNav :current="7" />
  </div>
</template>
