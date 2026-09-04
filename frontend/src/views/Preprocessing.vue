<script setup>
import { ref } from "vue";
import api, { baseURL } from "../utils/api";
import { useAppStore } from "../store";
import PipelineNav from "../components/PipelineNav.vue";

const store = useAppStore();

const isProcessing = ref(false);
const isResetting = ref(false);
const errorMsg = ref("");
const successMsg = ref("");
const processedData = ref(null);
const totalRows = ref(0);

const clearMessages = () => {
  errorMsg.value = "";
  successMsg.value = "";
};

const handlePreprocess = async () => {
  if (!store.sessionId) {
    errorMsg.value =
      "Sesi tidak ditemukan. Lakukan Input Data terlebih dahulu.";
    return;
  }
  clearMessages();
  isProcessing.value = true;
  try {
    const response = await api.post(
      "/api/process/preprocess",
      { session_id: store.sessionId }
    );
    processedData.value = response.data.preview;
    totalRows.value = response.data.total_rows;
    successMsg.value = `Preprocessing selesai! Total ${response.data.total_rows} ulasan berhasil diproses.`;
  } catch (error) {
    errorMsg.value =
      "Gagal preprocessing: " + (error.response?.data?.detail || error.message);
  } finally {
    isProcessing.value = false;
  }
};

const handleReset = async () => {
  if (!store.sessionId) return;
  clearMessages();
  isResetting.value = true;
  processedData.value = null;
  setTimeout(() => {
    isResetting.value = false;
    successMsg.value =
      "Reset berhasil. Anda bisa menjalankan preprocessing ulang.";
  }, 500);
};

const downloadPreprocessed = () => {
  if (!store.sessionId) return;
  window.open(
    `${baseURL}/api/preprocess/download/${store.sessionId}`,
    "_blank"
  );
};
</script>

<template>
  <div class="space-y-6">
    <!-- Title -->
    <div>
      <h1 class="text-2xl font-bold text-slate-800 dark:text-white mb-1 transition-colors">Preprocessing Data</h1>
      <p class="text-slate-500 dark:text-slate-400 text-xs transition-colors">
        Pembersihan Teks NLP: Case Folding, Tokenization, Normalisasi Slang, Stopword Removal, dan Stemming Sastrawi.
      </p>
    </div>

    <!-- Messages -->
    <div
      v-if="successMsg"
      class="p-4 bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/20 rounded-xl text-emerald-700 dark:text-emerald-400 text-xs flex items-center transition-all"
    >
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
        ></path>
      </svg>
      {{ successMsg }}
    </div>
    <div
      v-if="errorMsg"
      class="p-4 bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20 rounded-xl text-red-700 dark:text-red-400 text-xs flex items-center transition-all"
    >
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
          d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
      {{ errorMsg }}
    </div>

    <!-- Action Card -->
    <div
      class="bg-white dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800/80 rounded-2xl p-6 shadow-sm relative overflow-hidden transition-all duration-200"
    >
      <!-- Warning (No session) -->
      <div
        v-if="!store.sessionId"
        class="p-4 bg-amber-50 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-500/20 rounded-xl text-amber-700 dark:text-amber-400 text-xs mb-4 flex items-center"
      >
        <svg
          class="w-4.5 h-4.5 mr-2"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          ></path>
        </svg>
        Data belum diinput. Silakan ke halaman
        <strong class="mx-1 text-slate-800 dark:text-white">Input Data</strong> terlebih dahulu.
      </div>

      <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h3 class="text-sm font-bold text-slate-800 dark:text-slate-200 transition-colors">
            Jalankan NLP Preprocessing
          </h3>
          <p class="text-xs text-slate-400 dark:text-slate-500 transition-colors">
            Mengolah data mentah menjadi teks bersih siap latih (lowercase → hapus tanda baca → slang → stopword → stemming).
          </p>
        </div>
        <div class="flex gap-2 flex-shrink-0 w-full sm:w-auto">
          <button
            @click="handleReset"
            :disabled="isResetting || !processedData"
            class="flex-1 sm:flex-none flex items-center justify-center px-4 py-2 border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-55 dark:hover:bg-slate-800/80 rounded-xl text-xs font-semibold transition-all disabled:opacity-40 cursor-pointer"
          >
            <svg
              class="w-3.5 h-3.5 mr-1.5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2.5"
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
              />
            </svg>
            Reset
          </button>
          <button
            @click="handlePreprocess"
            :disabled="isProcessing || !store.sessionId"
            class="flex-1 sm:flex-none flex items-center justify-center px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 dark:bg-emerald-500 dark:hover:bg-emerald-400 text-white text-xs font-semibold rounded-xl shadow-sm transition-all disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
          >
            <svg
              v-if="isProcessing"
              class="animate-spin -ml-1 mr-1.5 h-3.5 w-3.5"
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
            <svg
              v-else
              class="w-3.5 h-3.5 mr-1.5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2.5"
                d="M13 10V3L4 14h7v7l9-11h-7z"
              />
            </svg>
            {{ isProcessing ? "Memproses..." : "Mulai Preprocessing" }}
          </button>
        </div>
      </div>
    </div>

    <!-- Results Preview -->
    <div
      v-if="processedData && processedData.length > 0"
      class="space-y-4"
    >
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-sm font-bold text-slate-800 dark:text-slate-200">Preview Data Hasil NLP</h3>
          <p class="text-[11px] text-slate-400 dark:text-slate-500">
            Total {{ totalRows }} ulasan diproses (menampilkan 10 baris pertama).
          </p>
        </div>
        <button
          @click="downloadPreprocessed"
          class="flex items-center px-4 py-2 bg-slate-50 hover:bg-slate-100 dark:bg-slate-800/80 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 text-xs font-semibold rounded-lg transition-all cursor-pointer"
        >
          <svg
            class="w-3.5 h-3.5 mr-1.5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2.5"
              d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
            />
          </svg>
          Download CSV
        </button>
      </div>

      <div
        class="overflow-x-auto rounded-xl border border-slate-200 dark:border-slate-800/60 bg-white dark:bg-slate-900"
      >
        <table class="w-full text-left text-xs text-slate-650 dark:text-slate-400">
          <thead
            class="sticky top-0 z-10 text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase bg-slate-50 dark:bg-slate-850/80 border-b border-slate-200 dark:border-slate-800/80"
          >
            <tr>
              <th class="px-6 py-4 border-b border-slate-200 dark:border-slate-800/80 w-16">#</th>
              <th class="px-6 py-4 border-b border-slate-200 dark:border-slate-800/80">
                Ulasan Asli (Review)
              </th>
              <th class="px-6 py-4 border-b border-slate-200 dark:border-slate-800/80">
                Teks Bersih (Clean)
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(row, idx) in processedData"
              :key="idx"
              class="border-b border-slate-200 dark:border-slate-800/60 hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors text-[11px]"
            >
              <td class="px-6 py-4 text-slate-400">{{ idx + 1 }}</td>
              <td class="px-6 py-4 max-w-xs">
                <p class="truncate" :title="row.Review">{{ row.Review }}</p>
              </td>
              <td class="px-6 py-4 max-w-xs">
                <p class="text-emerald-600 dark:text-emerald-400 font-medium truncate" :title="row.clean">
                  {{ row.clean }}
                </p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <PipelineNav :current="2" />
  </div>
</template>
