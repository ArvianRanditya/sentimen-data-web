<script setup>
import { ref, onMounted, computed } from "vue";
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
const insightData = ref(null);
const clusterNotes = ref({});

const isNlgLoading = ref(false);
const nlgError = ref("");
const nlgMode = ref("local"); // 'local' or 'gemini'

const chartCluster = ref(null);
const chartSentiment = ref(null);

const isDark = computed(() => store.theme === "dark");

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

const sentimentName = (id) =>
  ({ 0: "Negatif", 1: "Netral", 2: "Positif" }[id] || `Label ${id}`);
const sentimentColor = (id) =>
  ({
    0: "rgba(239, 68, 68, 0.8)",
    1: "rgba(100, 116, 139, 0.8)",
    2: "rgba(16, 185, 129, 0.8)",
  }[id] || "rgba(100, 116, 139, 0.8)");

const loadInsight = async () => {
  if (!store.sessionId) {
    errorMsg.value = "Sesi tidak ditemukan.";
    return;
  }
  isLoading.value = true;
  try {
    const res = await api.post("/api/insight", {
      session_id: store.sessionId,
    });
    insightData.value = res.data;
    successMsg.value = `Insight berhasil dimuat! Total ${res.data.total_data} ulasan dianalisis.`;

    // Build cluster chart
    if (
      res.data.cluster_distribution &&
      Object.keys(res.data.cluster_distribution).length > 0
    ) {
      const cd = res.data.cluster_distribution;
      const colors = [
        "#10b981",
        "#3b82f6",
        "#f59e0b",
        "#ef4444",
        "#a855f7",
        "#ec4899",
      ];
      chartCluster.value = {
        labels: Object.keys(cd).map((k) => `Cluster ${k}`),
        datasets: [
          {
            label: "Jumlah Data",
            backgroundColor: Object.keys(cd).map((k, idx) => colors[idx % colors.length]),
            data: Object.values(cd),
            borderRadius: 6,
          },
        ],
      };
    }

    // Build sentiment chart
    if (
      res.data.sentiment_distribution &&
      Object.keys(res.data.sentiment_distribution).length > 0
    ) {
      const sd = res.data.sentiment_distribution;
      chartSentiment.value = {
        labels: Object.keys(sd).map((k) => sentimentName(Number(k))),
        datasets: [
          {
            label: "Jumlah Data",
            backgroundColor: Object.keys(sd).map((k) =>
              sentimentColor(Number(k))
            ),
            data: Object.values(sd),
            borderRadius: 6,
          },
        ],
      };
    }
  } catch (err) {
    errorMsg.value =
      "Gagal memuat insight: " + (err.response?.data?.detail || err.message);
  } finally {
    isLoading.value = false;
  }
};

const generateNlgRecommendations = async () => {
  if (!store.sessionId) {
    nlgError.value = "Sesi tidak ditemukan.";
    return;
  }
  isNlgLoading.value = true;
  nlgError.value = "";
  try {
    const res = await api.post("/api/nlg/recommend", {
      session_id: store.sessionId,
      mode: nlgMode.value,
    });
    if (insightData.value) {
      insightData.value.nlg_recommendations = res.data.nlg_recommendations;
    }
  } catch (err) {
    nlgError.value = "Gagal membuat rekomendasi NLG: " + (err.response?.data?.detail || err.message);
  } finally {
    isNlgLoading.value = false;
  }
};

const dominantSentiment = () => {
  if (!insightData.value?.sentiment_distribution) return null;
  const sd = insightData.value.sentiment_distribution;
  const maxKey = Object.keys(sd).reduce((a, b) => (sd[a] > sd[b] ? a : b));
  return sentimentName(Number(maxKey));
};

const downloadAnalysis = async () => {
  if (!store.sessionId) {
    alert("Session tidak ditemukan");
    return;
  }

  try {
    const response = await api.post(
      "/api/download-analysis",
      {
        session_id: store.sessionId,
        notes: clusterNotes.value,
      },
      {
        responseType: "arraybuffer",
      }
    );

    const blob = new Blob([response.data], {
      type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    });

    const url = window.URL.createObjectURL(blob);

    const link = document.createElement("a");
    link.href = url;
    link.download = "hasil_analisis.xlsx";

    document.body.appendChild(link);
    link.click();

    window.URL.revokeObjectURL(url);
    link.remove();
  } catch (err) {
    alert("Gagal mengunduh file laporan");
  }
};

onMounted(() => {
  if (store.sessionId) loadInsight();
});
</script>

<template>
  <div class="space-y-6">
    <!-- Title -->
    <div>
      <h1 class="text-2xl font-bold text-slate-800 dark:text-white mb-1 transition-colors">Insight Global</h1>
      <p class="text-slate-500 dark:text-slate-400 text-xs transition-colors">
        Laporan ringkasan analisis sentimen global, sebaran kelompok cluster ulasan, dan asisten naratif NLG.
      </p>
    </div>

    <!-- Feedbacks -->
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
      <span class="ml-3 text-sm font-semibold">Memproses Insight Global...</span>
    </div>

    <!-- Main View Section -->
    <div v-if="insightData && !isLoading" class="space-y-6 animate-fade-in">
      
      <!-- Summary metrics cards -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div
          class="bg-white dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 text-center shadow-sm"
        >
          <p class="text-slate-400 dark:text-slate-500 text-xs mb-1 font-medium uppercase tracking-wide">Total Dataset</p>
          <p class="text-3xl font-black text-slate-800 dark:text-white transition-colors">
            {{ insightData.total_data }}
          </p>
        </div>
        <div
          class="bg-white dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 text-center shadow-sm"
        >
          <p class="text-slate-400 dark:text-slate-500 text-xs mb-1 font-medium uppercase tracking-wide">Total Cluster</p>
          <p class="text-3xl font-black text-slate-800 dark:text-white transition-colors">
            {{ insightData.total_clusters ?? "-" }}
          </p>
        </div>
      </div>

      <!-- Charts grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Cluster distribution -->
        <div
          v-if="chartCluster"
          class="bg-white dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm"
        >
          <h3 class="text-sm font-bold text-slate-800 dark:text-slate-200 mb-4 transition-colors">Sebaran Data per Cluster</h3>
          <div class="h-52">
            <Bar :data="chartCluster" :options="barOptions" />
          </div>
          <div class="mt-5 space-y-2 text-xs">
            <div
              v-for="(count, cid) in insightData.cluster_distribution"
              :key="cid"
              class="flex justify-between items-center py-1 border-b border-slate-100 dark:border-slate-800 last:border-0"
            >
              <span class="text-slate-500 dark:text-slate-400 font-medium">Cluster {{ cid }}</span>
              <span class="text-slate-700 dark:text-slate-200 font-bold font-mono">{{ count }} ulasan</span>
            </div>
          </div>
        </div>

        <!-- Sentiment distribution -->
        <div
          v-if="chartSentiment"
          class="bg-white dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm"
        >
          <h3 class="text-sm font-bold text-slate-800 dark:text-slate-200 mb-1 transition-colors">Sebaran Sentimen Global</h3>
          <div v-if="dominantSentiment()" class="text-[11px] text-emerald-600 dark:text-emerald-450 font-semibold mb-4">
            Orientasi Terbanyak: {{ dominantSentiment() }}
          </div>
          <div class="h-52">
            <Bar :data="chartSentiment" :options="barOptions" />
          </div>
          <div class="mt-5 space-y-2 text-xs">
            <div
              v-for="(count, sid) in insightData.sentiment_distribution"
              :key="sid"
              class="flex justify-between items-center py-1 border-b border-slate-100 dark:border-slate-800 last:border-0"
            >
              <span class="text-slate-500 dark:text-slate-400 font-medium">{{ sentimentName(Number(sid)) }}</span>
              <span
                class="font-bold font-mono"
                :class="{
                  'text-emerald-600 dark:text-emerald-400': Number(sid) === 2,
                  'text-red-650 dark:text-red-400': Number(sid) === 0,
                  'text-slate-500 dark:text-slate-400': Number(sid) === 1,
                }"
              >
                {{ count }} ulasan
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- NLG Recommendation Assistant Banner -->
      <div 
        v-if="insightData.cluster_distribution_detail && insightData.cluster_topics"
        class="p-6 bg-emerald-50/40 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-800/80 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-6 shadow-sm"
      >
        <div>
          <h4 class="text-sm font-bold text-slate-800 dark:text-white flex items-center gap-1.5 transition-colors">
            <span>✨</span> Asisten NLG (Natural Language Generation)
          </h4>
          <p class="text-slate-500 dark:text-slate-400 text-xs mt-1 max-w-xl transition-colors leading-relaxed">
            Asisten AI akan menganalisis kata kunci TF-IDF dan orientasi sentimen di setiap cluster untuk menyusun ringkasan naratif otomatis serta rekomendasi praktis.
          </p>
        </div>
        <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
          <!-- Mode Switcher -->
          <div class="flex items-center bg-white/80 dark:bg-slate-800 p-1 rounded-xl border border-slate-200 dark:border-slate-700 shadow-xs">
            <button
              type="button"
              @click="nlgMode = 'local'"
              :class="[
                'px-3 py-2 rounded-lg text-xs font-semibold transition-all cursor-pointer flex items-center gap-1.5',
                nlgMode === 'local'
                  ? 'bg-emerald-600 text-white shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-200'
              ]"
            >
              <span>💻</span>
              <span>Sistem Lokal (Offline)</span>
            </button>
            <button
              type="button"
              @click="nlgMode = 'gemini'"
              :class="[
                'px-3 py-2 rounded-lg text-xs font-semibold transition-all cursor-pointer flex items-center gap-1.5',
                nlgMode === 'gemini'
                  ? 'bg-blue-600 text-white shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-200'
              ]"
            >
              <span>✨</span>
              <span>Gemini API (Cloud)</span>
            </button>
          </div>

          <!-- Generate Button -->
          <button
            @click="generateNlgRecommendations"
            :disabled="isNlgLoading"
            class="flex-shrink-0 px-5 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 dark:bg-emerald-500 dark:hover:bg-emerald-400 text-white text-xs font-bold transition-all disabled:opacity-50 flex items-center justify-center gap-1.5 shadow-sm shadow-emerald-500/10 cursor-pointer"
          >
            <svg v-if="isNlgLoading" class="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
            </svg>
            <svg v-else class="w-4.5 h-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            {{ isNlgLoading ? "Menganalisis..." : `Generasikan (${nlgMode === 'local' ? 'Lokal' : 'Gemini'})` }}
          </button>
        </div>
      </div>

      <!-- NLG Error -->
      <div v-if="nlgError" class="p-4 bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20 rounded-xl text-red-700 dark:text-red-400 text-xs flex items-center gap-2">
        <svg class="w-4.5 h-4.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        {{ nlgError }}
      </div>

      <!-- Detail list of clusters with keywords, sentiment distribution, and user notes -->
      <div
        v-if="
          insightData.cluster_distribution_detail && insightData.cluster_topics
        "
        class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
      >
        <div
          v-for="cluster in insightData.cluster_distribution_detail"
          :key="cluster.cluster"
          class="bg-white dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm flex flex-col justify-between"
        >
          <div>
            <!-- Cluster Title -->
            <h3 class="text-sm font-bold text-slate-800 dark:text-white mb-4 transition-colors">
              {{
                insightData.cluster_topics[cluster.cluster]?.name ||
                `Cluster ${cluster.cluster}`
              }}
            </h3>

            <!-- Dominant Keywords -->
            <div class="mb-5">
              <p class="text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-2.5">Kata Dominan</p>
              <div class="flex flex-wrap gap-2">
                <span
                  v-for="word in insightData.cluster_topics[cluster.cluster]?.keywords"
                  :key="word"
                  class="px-2.5 py-0.5 rounded-full bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-250/60 dark:border-emerald-500/20 text-emerald-700 dark:text-emerald-400 text-xs font-semibold"
                >
                  {{ word }}
                </span>
              </div>
            </div>

            <!-- Smart recommendations from NLG -->
            <div class="mb-5 p-4 rounded-xl bg-slate-50 dark:bg-slate-800/30 border border-slate-200 dark:border-slate-800/60">
              <div class="flex items-center justify-between mb-2 text-xs font-bold text-emerald-700 dark:text-emerald-400">
                <div class="flex items-center gap-1.5">
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  Rekomendasi Pintar (NLG)
                </div>
                <span
                  v-if="insightData.nlg_recommendations && insightData.nlg_recommendations[cluster.cluster]?.mode"
                  class="text-[9px] px-2 py-0.5 rounded-full font-medium"
                  :class="insightData.nlg_recommendations[cluster.cluster].mode === 'gemini' ? 'bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300' : 'bg-emerald-100 dark:bg-emerald-900/40 text-emerald-700 dark:text-emerald-300'"
                >
                  {{ insightData.nlg_recommendations[cluster.cluster].mode === 'gemini' ? '✨ Gemini AI' : '💻 Sistem Lokal' }}
                </span>
              </div>
              
              <div v-if="insightData.nlg_recommendations && insightData.nlg_recommendations[cluster.cluster]" class="text-[11px] text-slate-600 dark:text-slate-300 leading-relaxed whitespace-pre-line">
                {{ insightData.nlg_recommendations[cluster.cluster].recommendation }}
              </div>
              <div v-else class="text-[11px] text-slate-400 dark:text-slate-500 italic">
                Rekomendasi belum dibuat. Klik tombol di atas untuk membuat.
              </div>
            </div>

            <!-- Sentiment Bars inside cluster -->
            <div class="space-y-4">
              <p class="text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wide">Distribusi Sentimen</p>

              <!-- Positive -->
              <div class="text-[11px]">
                <div class="flex justify-between mb-1 text-slate-600 dark:text-slate-400">
                  <span class="text-emerald-700 dark:text-emerald-400 font-semibold">Positif</span>
                  <span class="text-slate-800 dark:text-slate-100 font-bold font-mono">
                    {{ cluster.positif }}
                  </span>
                </div>
                <div class="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-1.5">
                  <div
                    class="bg-emerald-500 h-1.5 rounded-full"
                    :style="{
                      width:
                        (cluster.positif /
                          (cluster.positif +
                            cluster.netral +
                            cluster.negatif)) *
                          100 +
                        '%',
                    }"
                  ></div>
                </div>
              </div>

              <!-- Neutral -->
              <div class="text-[11px]">
                <div class="flex justify-between mb-1 text-slate-600 dark:text-slate-400">
                  <span class="text-slate-550 dark:text-slate-450 font-semibold">Netral</span>
                  <span class="text-slate-800 dark:text-slate-100 font-bold font-mono">
                    {{ cluster.netral }}
                  </span>
                </div>
                <div class="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-1.5">
                  <div
                    class="bg-slate-400 h-1.5 rounded-full"
                    :style="{
                      width:
                        (cluster.netral /
                          (cluster.positif +
                            cluster.netral +
                            cluster.negatif)) *
                          100 +
                        '%',
                    }"
                  ></div>
                </div>
              </div>

              <!-- Negative -->
              <div class="text-[11px]">
                <div class="flex justify-between mb-1 text-slate-600 dark:text-slate-400">
                  <span class="text-red-700 dark:text-red-400 font-semibold">Negatif</span>
                  <span class="text-slate-800 dark:text-slate-100 font-bold font-mono">
                    {{ cluster.negatif }}
                  </span>
                </div>
                <div class="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-1.5">
                  <div
                    class="bg-red-500 h-1.5 rounded-full"
                    :style="{
                      width:
                        (cluster.negatif /
                          (cluster.positif +
                            cluster.netral +
                            cluster.negatif)) *
                          100 +
                        '%',
                    }"
                  ></div>
                </div>
              </div>
            </div>
          </div>

          <!-- Catatan Analisis input area -->
          <div class="mt-6 border-t border-slate-150 dark:border-slate-800/80 pt-4">
            <label class="block text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-2">
              Catatan Analisis Manual
            </label>
            <textarea
              v-model="clusterNotes[cluster.cluster]"
              rows="3"
              placeholder="Tulis kesimpulan atau catatan tambahan untuk cluster ini..."
              class="w-full bg-slate-50 focus:bg-white dark:bg-slate-950/40 border border-slate-200 dark:border-slate-800 rounded-xl p-3 text-slate-800 dark:text-slate-200 text-xs focus:outline-none focus:ring-2 focus:ring-emerald-500/15 focus:border-emerald-500/50 transition-all resize-none"
            ></textarea>
          </div>
        </div>
      </div>

      <!-- Export excel area -->
      <div class="flex justify-end pt-4">
        <button
          @click="downloadAnalysis"
          class="flex items-center px-6 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 dark:bg-emerald-500 dark:hover:bg-emerald-400 text-white text-xs font-bold shadow-sm transition-all cursor-pointer"
        >
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          Unduh Hasil Laporan Excel
        </button>
      </div>
    </div>
    <PipelineNav :current="8" />
  </div>
</template>
