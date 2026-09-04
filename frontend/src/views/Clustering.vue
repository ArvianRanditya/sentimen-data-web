<script setup>
import { ref, onMounted, computed } from "vue";
import api from "../utils/api";
import { useAppStore } from "../store";
import { useRouter } from "vue-router";
import AppIcon from "../components/AppIcon.vue";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from "chart.js";
import { Line, Bar } from "vue-chartjs";
import PipelineNav from "../components/PipelineNav.vue";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const store = useAppStore();
const router = useRouter();

const isLoading = ref(false);
const isApplying = ref(false);
const errorMsg = ref("");
const successMsg = ref("");
const clusteringApplied = ref(false);
const clusterResult = ref(null); // distribution after apply

const evaluationData = ref(null);
const bestK = ref(3);

const chartCalinski = ref(null);
const chartDistribution = ref(null);

const isDark = computed(() => store.theme === "dark");

const lineOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: { 
    legend: { labels: { color: isDark.value ? "#cbd5e1" : "#334155" } },
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
      grid: { color: isDark.value ? "#334155" : "#e2e8f0" } 
    },
    y: { 
      ticks: { color: isDark.value ? "#94a3b8" : "#475569" }, 
      grid: { color: isDark.value ? "#334155" : "#e2e8f0" } 
    },
  },
}));

const barOptions = computed(() => ({
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

const loadEvaluation = async () => {
  if (!store.sessionId) {
    errorMsg.value =
      "Sesi tidak ditemukan. Lakukan input data dan preprocessing terlebih dahulu.";
    return;
  }
  isLoading.value = true;
  errorMsg.value = "";
  try {
    const res = await api.post("/api/cluster/evaluate", {
      session_id: store.sessionId,
      max_k: 10,
    });
    evaluationData.value = res.data.evaluation;
    const labels = evaluationData.value.map((d) => `K=${d.k}`);
    const calinskis = evaluationData.value.map((d) => d.calinski);
    const bestIdx = calinskis.indexOf(Math.max(...calinskis));
    bestK.value = evaluationData.value[bestIdx].k;

    chartCalinski.value = {
      labels,
      datasets: [
        {
          label: "Calinski-Harabasz Index",
          backgroundColor: isDark.value ? "rgba(245,158,11,0.06)" : "rgba(217,119,6,0.06)",
          borderColor: isDark.value ? "#f59e0b" : "#d97706",
          pointBackgroundColor: isDark.value ? "#f59e0b" : "#d97706",
          data: calinskis,
          tension: 0.3,
          fill: true,
        },
      ],
    };
  } catch (err) {
    errorMsg.value =
      "Gagal evaluasi: " + (err.response?.data?.detail || err.message);
  } finally {
    isLoading.value = false;
  }
};

const applyClustering = async () => {
  isApplying.value = true;
  try {
    const res = await api.post("/api/cluster/apply", {
      session_id: store.sessionId,
      k: bestK.value,
    });
    clusterResult.value = res.data;
    clusteringApplied.value = true;
    successMsg.value = `Clustering K=${bestK.value} berhasil! Data terbagi ke ${
      Object.keys(res.data.distribution).length
    } cluster.`;
    
    // Build distribution chart
    const dist = res.data.distribution;
    // Flat clean colors
    const colors = [
      "#10b981",
      "#3b82f6",
      "#f59e0b",
      "#ef4444",
      "#a855f7",
      "#ec4899",
    ];
    chartDistribution.value = {
      labels: Object.keys(dist).map((k) => `Cluster ${k}`),
      datasets: [
        {
          label: "Jumlah Ulasan",
          backgroundColor: Object.keys(dist).map((k, idx) => colors[idx % colors.length]),
          data: Object.values(dist),
          borderRadius: 6,
        },
      ],
    };
  } catch (err) {
    errorMsg.value =
      "Gagal clustering: " + (err.response?.data?.detail || err.message);
  } finally {
    isApplying.value = false;
  }
};

onMounted(async () => {
  if (!store.sessionId) return;

  try {
    // Jalankan sentiment prediction dulu untuk memastikan file labeled tersedia
    await api.post("/api/sentiment/predict", {
      session_id: store.sessionId,
    });

    // Baru evaluasi clustering
    await loadEvaluation();
  } catch (err) {
    errorMsg.value =
      "Gagal melakukan klasifikasi sentimen awal: " +
      (err.response?.data?.detail || err.message);
  }
});
</script>

<template>
  <div class="space-y-6">
    <!-- Title -->
    <div>
      <h1 class="text-2xl font-bold text-slate-800 dark:text-white mb-1 transition-colors">Clustering K-Means</h1>
      <p class="text-slate-500 dark:text-slate-400 text-xs transition-colors">
        Kelompokkan data ulasan berdasarkan kemiripan kata kunci teks, dievaluasi menggunakan Calinski-Harabasz Index.
      </p>
    </div>

    <!-- Error Banner -->
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

    <!-- Loading State -->
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
      <span class="ml-3 text-sm font-semibold">Mengevaluasi K=2 sampai K=10...</span>
    </div>

    <div v-if="chartCalinski && !isLoading" class="space-y-6">
      <!-- Success/Redirect Banner -->
      <div
        v-if="clusteringApplied"
        class="p-4 bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/20 rounded-xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 transition-all"
      >
        <div class="flex items-center text-emerald-700 dark:text-emerald-400 text-xs">
          <svg
            class="w-4.5 h-4.5 mr-2 flex-shrink-0"
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
          <span>
            Clustering berhasil diterapkan! Terbentuk <strong class="mx-0.5">{{ bestK }} cluster</strong> pada data ulasan Anda.
          </span>
        </div>
        <button
          @click="router.push('/topik-cluster')"
          class="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 dark:bg-emerald-500 dark:hover:bg-emerald-400 text-white text-xs font-semibold rounded-lg shadow-sm transition-colors flex items-center cursor-pointer"
        >
          <span>Lihat Topik Cluster</span>
          <svg
            class="w-3.5 h-3.5 ml-1.5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2.5"
              d="M9 5l7 7-7 7"
            />
          </svg>
        </button>
      </div>

      <!-- Table + Line chart metric evaluation -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Metric Table -->
        <div class="bg-white dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm">
          <h3 class="text-sm font-bold text-slate-800 dark:text-slate-200 mb-4 transition-colors">
            Tabel Indeks Calinski-Harabasz
          </h3>

          <div
            class="max-h-[360px] overflow-auto rounded-xl border border-slate-200 dark:border-slate-800/60 bg-white dark:bg-slate-900"
          >
            <table class="w-full text-left text-xs text-slate-650 dark:text-slate-400">
              <thead
                class="sticky top-0 z-10 text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase bg-slate-50 dark:bg-slate-850/80 border-b border-slate-200 dark:border-slate-800/80"
              >
                <tr>
                  <th class="px-5 py-3">Jumlah Cluster (K)</th>
                  <th class="px-5 py-3">Skor Calinski-Harabasz</th>
                </tr>
              </thead>

              <tbody>
                <tr
                  v-for="row in evaluationData"
                  :key="row.k"
                  class="border-b border-slate-200 dark:border-slate-800/60 transition-colors text-[11px]"
                  :class="
                    row.k === bestK
                      ? 'bg-emerald-50/50 dark:bg-emerald-500/5 font-semibold text-emerald-700 dark:text-emerald-400'
                      : 'hover:bg-slate-50 dark:hover:bg-slate-800/30'
                  "
                >
                  <td class="px-5 py-3 flex items-center gap-2">
                    <span>{{ row.k }}</span>
                    <span
                      v-if="row.k === bestK"
                      class="text-[9px] bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400 px-1.5 py-0.5 rounded-full uppercase tracking-wider font-bold"
                    >
                      rekomendasi
                    </span>
                  </td>

                  <td class="px-5 py-3 font-mono">
                    {{ row.calinski.toFixed(2) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Evaluation Chart -->
        <div
          class="bg-white dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 relative shadow-sm"
        >
          <h3 class="text-sm font-bold text-slate-800 dark:text-slate-200 mb-4 text-center transition-colors">
            Grafik Calinski-Harabasz Index
          </h3>

          <div style="height: 300px">
            <Line :data="chartCalinski" :options="lineOptions" />
          </div>
        </div>
      </div>
    </div>

    <!-- Apply Action Controller -->
    <div
      v-if="chartCalinski && !isLoading"
      class="bg-white dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm"
    >
      <div class="flex flex-col md:flex-row md:items-end gap-6">
        <!-- K parameter slider -->
        <div class="flex-1">
          <div class="flex justify-between items-center mb-2.5">
            <label class="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wide">Pilih Jumlah K</label>
            <span
              class="text-[10px] font-bold text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-500/10 px-2 py-0.5 rounded-full"
              >Rekomendasi Optimal: K={{ bestK }}</span
            >
          </div>
          <input
            type="range"
            min="2"
            max="10"
            v-model="bestK"
            class="w-full accent-emerald-600 dark:accent-emerald-500 h-2 bg-slate-200 dark:bg-slate-800 rounded-lg appearance-none cursor-pointer"
          />
          <div class="flex justify-between text-[10px] text-slate-400 dark:text-slate-500 mt-2 transition-colors font-medium">
            <span>K=2</span>
            <span class="text-emerald-700 dark:text-emerald-400 font-bold text-xs"
              >Pilihan: K = {{ bestK }}</span
            >
            <span>K=10</span>
          </div>
        </div>
        
        <!-- Execute button -->
        <div class="flex flex-col w-full md:w-auto flex-shrink-0">
          <button
            @click="applyClustering"
            :disabled="isApplying"
            class="w-full md:w-auto flex items-center justify-center px-6 py-2.5 bg-emerald-600 hover:bg-emerald-500 dark:bg-emerald-500 dark:hover:bg-emerald-400 text-white text-xs font-bold rounded-xl shadow-sm transition-all disabled:opacity-50 cursor-pointer"
          >
            <span v-if="!isApplying" class="flex items-center">
              <AppIcon name="play" class="w-4 h-4 mr-1.5" />
              Terapkan Clustering
            </span>
            <span v-else class="flex items-center">
              <svg
                class="animate-spin mr-1.5 h-3.5 w-3.5"
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
              Memproses...
            </span>
          </button>
          <p class="text-[10px] text-slate-400 dark:text-slate-500 mt-1.5 text-center transition-colors">
            * Wajib diklik sebelum lanjut ke analisis topik ulasan.
          </p>
        </div>
      </div>
    </div>

    <!-- Cluster Result & Distribution -->
    <div
      v-if="clusterResult && chartDistribution && !isLoading"
      class="grid grid-cols-1 lg:grid-cols-2 gap-6 animate-fade-in"
    >
      <!-- Chart Distribution -->
      <div class="bg-white dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm">
        <h3 class="text-sm font-bold text-slate-800 dark:text-slate-200 mb-4 transition-colors">
          Grafik Sebaran Cluster
        </h3>
        <div style="height: 200px">
          <Bar :data="chartDistribution" :options="barOptions" />
        </div>
      </div>

      <!-- Numerical Summary -->
      <div class="bg-white dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm">
        <h3 class="text-sm font-bold text-slate-800 dark:text-slate-200 mb-4 transition-colors">
          Ringkasan Statistik Cluster
        </h3>
        <ul class="space-y-3 text-xs">
          <li
            class="flex justify-between items-center border-b border-slate-200 dark:border-slate-800 pb-2.5 transition-colors"
          >
            <span class="text-slate-500 dark:text-slate-400">Total Baris Valid</span>
            <span class="text-slate-800 dark:text-slate-100 font-bold">{{
              clusterResult.preview?.length
                ? `${clusterResult.preview.length}+`
                : "-"
            }}</span>
          </li>
          <li
            class="flex justify-between items-center border-b border-slate-200 dark:border-slate-800 pb-2.5 transition-colors"
          >
            <span class="text-slate-500 dark:text-slate-400">Jumlah Kelompok (K)</span>
            <span class="text-emerald-600 dark:text-emerald-400 font-bold">{{ bestK }}</span>
          </li>
          <li
            v-for="(count, cid) in clusterResult.distribution"
            :key="cid"
            class="flex justify-between items-center"
          >
            <span class="text-slate-500 dark:text-slate-450">Cluster {{ cid }}</span>
            <span
              class="bg-slate-50 dark:bg-slate-800 px-3 py-1 rounded-full text-slate-700 dark:text-slate-200 font-mono text-[11px] border border-slate-100 dark:border-slate-800"
              >{{ count }} ulasan</span
            >
          </li>
        </ul>
      </div>
    </div>
    <PipelineNav :current="6" />
  </div>
</template>
