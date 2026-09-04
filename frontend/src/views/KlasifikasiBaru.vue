<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useAppStore } from "../store";
import api from "../utils/api";
import PipelineNav from "../components/PipelineNav.vue";

const router = useRouter();
const store = useAppStore();
const textInput = ref("");
const isPredicting = ref(false);
const isProcessingFile = ref(false);
const result = ref(null);
const errorMsg = ref("");
const mode = ref("manual"); // 'manual' or 'file'
const uploadedFile = ref(null);
const batchResults = ref(null);

onMounted(() => {
  if (!store.sessionId) {
    alert("Silakan lakukan proses analisis terlebih dahulu.");
    router.replace("/input-data");
  }
});

const sentimentName = (id) =>
  ({ 0: "Negatif", 1: "Netral", 2: "Positif" }[id] || "Unknown");

const sentimentColorClass = (id) =>
  ({
    0: "text-red-700 dark:text-red-400 bg-red-500/5 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20",
    1: "text-slate-600 dark:text-slate-400 bg-slate-500/5 dark:bg-slate-500/10 border border-slate-200 dark:border-slate-800",
    2: "text-emerald-700 dark:text-emerald-400 bg-emerald-500/5 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/20",
  }[id] || "text-slate-500 bg-slate-100 border-slate-200");

const handlePredict = async () => {
  if (!textInput.value.trim()) {
    errorMsg.value = "Teks tidak boleh kosong.";
    return;
  }
  isPredicting.value = true;
  errorMsg.value = "";
  result.value = null;
  try {
    const res = await api.post("/api/model/predict", {
      text: textInput.value,
    });
    result.value = res.data;
  } catch (err) {
    errorMsg.value =
      "Gagal memprediksi: " + (err.response?.data?.detail || err.message);
  } finally {
    isPredicting.value = false;
  }
};

const onFileChange = (e) => {
  uploadedFile.value = e.target.files[0];
};

const handleBatchPredict = async () => {
  if (!uploadedFile.value) {
    errorMsg.value = "Pilih file terlebih dahulu.";
    return;
  }
  const formData = new FormData();
  formData.append("file", uploadedFile.value);
  isProcessingFile.value = true;
  errorMsg.value = "";
  batchResults.value = null;
  try {
    const res = await api.post(
      "/api/model/predict_batch",
      formData
    );
    batchResults.value = res.data;
  } catch (err) {
    errorMsg.value =
      "Gagal memproses file: " + (err.response?.data?.detail || err.message);
  } finally {
    isProcessingFile.value = false;
  }
};

const downloadBatchCSV = () => {
  if (!batchResults.value?.predictions) return;
  const data = batchResults.value.predictions;
  const keys = Object.keys(data[0]);
  const csv = [
    keys.join(","),
    ...data.map((r) =>
      keys.map((k) => `"${String(r[k] ?? "").replace(/"/g, '""')}"`).join(",")
    ),
  ].join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "prediksi_batch.csv";
  a.click();
  URL.revokeObjectURL(url);
};
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div
      class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4"
    >
      <div>
        <h1 class="text-2xl font-bold text-slate-800 dark:text-white mb-1 transition-colors">Klasifikasi Baru</h1>
        <p class="text-slate-500 dark:text-slate-400 text-xs transition-colors">
          Prediksi orientasi sentimen &amp; topik kelompok ulasan baru menggunakan model yang sudah dilatih.
        </p>
      </div>

      <!-- Mode controller toggle buttons -->
      <div
        class="bg-slate-100 dark:bg-slate-800/80 p-1 rounded-xl inline-flex border border-slate-200 dark:border-slate-800 transition-colors"
      >
        <button
          @click="
            mode = 'manual';
            errorMsg = '';
            result = null;
            batchResults = null;
          "
          class="px-4 py-2 rounded-lg text-xs font-semibold transition-all duration-150 cursor-pointer"
          :class="
            mode === 'manual'
              ? 'bg-emerald-600 dark:bg-emerald-500 text-white shadow-sm'
              : 'text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200'
          "
        >
          Prediksi Manual
        </button>
        <button
          @click="
            mode = 'file';
            errorMsg = '';
            result = null;
            batchResults = null;
          "
          class="px-4 py-2 rounded-lg text-xs font-semibold transition-all duration-150 cursor-pointer"
          :class="
            mode === 'file'
              ? 'bg-emerald-600 dark:bg-emerald-500 text-white shadow-sm'
              : 'text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200'
          "
        >
          Prediksi Batch (File)
        </button>
      </div>
    </div>

    <!-- Error Banner -->
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

    <!-- === MANUAL MODE === -->
    <div
      v-if="mode === 'manual'"
      class="grid grid-cols-1 lg:grid-cols-2 gap-6 animate-fade-in"
    >
      <!-- Input Panel -->
      <div
        class="bg-white dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm relative transition-all"
      >
        <h3 class="text-sm font-bold text-slate-800 dark:text-white mb-4 transition-colors">Tulis Ulasan Baru</h3>
        <textarea
          v-model="textInput"
          rows="5"
          class="w-full bg-slate-50 focus:bg-white dark:bg-slate-950/40 border border-slate-200 dark:border-slate-800 rounded-xl p-4 text-slate-800 dark:text-slate-200 placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/15 focus:border-emerald-500/50 transition-all mb-4 text-xs"
          placeholder="Ketik ulasan atau review pelanggan di sini..."
        >
        </textarea>
        <button
          @click="handlePredict"
          :disabled="isPredicting"
          class="w-full flex items-center justify-center px-6 py-2.5 bg-emerald-600 hover:bg-emerald-500 dark:bg-emerald-500 dark:hover:bg-emerald-400 text-white text-xs font-bold rounded-xl shadow-sm transition-all disabled:opacity-50 cursor-pointer"
        >
          <svg
            v-if="isPredicting"
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
            />
            <path
              class="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
            />
          </svg>
          <span>{{ isPredicting ? "Menganalisis..." : "Proses Prediksi" }}</span>
        </button>
      </div>

      <!-- Result Panel -->
      <div
        class="bg-white dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm flex flex-col items-center justify-center min-h-[250px] transition-all"
      >
        <!-- Initial / Empty state -->
        <div v-if="!result && !isPredicting" class="text-slate-400 dark:text-slate-500 text-center text-xs">
          <svg
            class="w-12 h-12 mx-auto mb-3 opacity-30"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="1.5"
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <p>Hasil analisis prediksi manual akan ditampilkan di sini.</p>
        </div>
        
        <!-- Loading state -->
        <div v-if="isPredicting" class="text-emerald-600 dark:text-emerald-500 text-center text-xs">
          <svg
            class="animate-spin h-10 w-10 mx-auto mb-4"
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
          <p class="font-semibold">Menguraikan teks ulasan...</p>
        </div>

        <!-- Result content -->
        <div v-if="result && !isPredicting" class="w-full space-y-4 animate-fade-in">
          <div class="text-center pb-2 border-b border-slate-100 dark:border-slate-800">
            <p class="text-slate-400 dark:text-slate-500 text-[10px] uppercase font-bold tracking-wide mb-1">Teks Masukan</p>
            <p class="text-slate-700 dark:text-slate-200 italic text-xs px-2 line-clamp-3" :title="result.text">
              "{{ result.text }}"
            </p>
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <!-- Sentiment -->
            <div
              class="border rounded-xl p-4 text-center"
              :class="sentimentColorClass(result.sentiment)"
            >
              <p class="text-[9px] uppercase tracking-wider font-bold mb-1 opacity-70">
                Prediksi Sentimen
              </p>
              <h2 class="text-xl font-bold">
                {{ sentimentName(result.sentiment) }}
              </h2>
            </div>
            
            <!-- Topic -->
            <div
              class="border border-emerald-200 dark:border-emerald-500/20 bg-emerald-50 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 rounded-xl p-4 text-center"
            >
              <p class="text-[9px] uppercase tracking-wider font-bold mb-1 opacity-70">
                Prediksi Topik
              </p>
              <h2 class="text-xl font-bold">{{ result.topic }}</h2>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- === FILE MODE (BATCH PREDICTION) === -->
    <div v-if="mode === 'file'" class="space-y-6 animate-fade-in">
      
      <!-- Upload area -->
      <div class="bg-white dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm">
        <h3 class="text-sm font-bold text-slate-800 dark:text-white mb-2 transition-colors">
          Unggah Berkas CSV / Excel
        </h3>
        <p class="text-xs text-slate-500 dark:text-slate-400 mb-4 transition-colors leading-relaxed">
          Berkas ulasan harus menyertakan header kolom bernama <strong>Review</strong>. Sistem akan memprediksi orientasi sentimen serta topik di masing-masing baris secara batch.
        </p>
        
        <label class="block cursor-pointer">
          <div
            class="border-2 border-dashed border-slate-300 dark:border-slate-800 hover:border-emerald-500 dark:hover:border-emerald-500/60 rounded-xl p-8 text-center transition-colors duration-200"
          >
            <div class="w-10 h-10 mx-auto mb-3 bg-slate-100 dark:bg-slate-800 flex items-center justify-center rounded-lg">
              <svg
                class="w-5.5 h-5.5 text-slate-400 dark:text-slate-550"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2.5"
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                />
              </svg>
            </div>
            <p class="text-slate-700 dark:text-slate-200 text-xs font-semibold">
              {{ uploadedFile ? uploadedFile.name : "Klik untuk memilih berkas ulasan" }}
            </p>
            <p class="text-[10px] text-slate-400 dark:text-slate-500 mt-1">Mendukung file ekstensi .csv dan .xlsx</p>
          </div>
          <input
            type="file"
            class="hidden"
            accept=".csv,.xlsx"
            @change="onFileChange"
          />
        </label>
        
        <!-- Execute batch button -->
        <div
          v-if="uploadedFile"
          class="mt-4 flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-800/30 border border-slate-200 dark:border-slate-800 rounded-xl transition-all"
        >
          <span class="text-slate-700 dark:text-slate-350 text-xs font-semibold">{{ uploadedFile.name }}</span>
          <button
            @click="handleBatchPredict"
            :disabled="isProcessingFile"
            class="flex items-center px-4 py-2 bg-emerald-600 hover:bg-emerald-500 dark:bg-emerald-500 dark:hover:bg-emerald-400 text-white text-xs font-bold rounded-lg shadow-sm transition-all disabled:opacity-50 cursor-pointer"
          >
            <svg
              v-if="isProcessingFile"
              class="animate-spin mr-1.5 h-3.5 w-3.5 text-white"
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
            {{ isProcessingFile ? "Mengklasifikasi..." : "Jalankan Prediksi Batch" }}
          </button>
        </div>
      </div>

      <!-- Batch Results Table -->
      <div
        v-if="batchResults"
        class="bg-white dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm"
      >
        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-4">
          <div>
            <h3 class="text-sm font-bold text-slate-800 dark:text-white">Hasil Prediksi Batch</h3>
            <p class="text-[11px] text-slate-500 dark:text-slate-400">
              Total {{ batchResults.total }} baris ulasan dianalisis. Terbagi dalam {{ batchResults.unique_clusters }} topik cluster.
            </p>
          </div>
          <button
            @click="downloadBatchCSV"
            class="flex items-center px-4 py-2 bg-slate-50 hover:bg-slate-100 dark:bg-slate-800/80 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-350 text-xs font-semibold rounded-lg transition-all cursor-pointer"
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
            Download CSV Laporan
          </button>
        </div>

        <div
          class="max-h-[350px] overflow-auto rounded-xl border border-slate-200 dark:border-slate-800/60 bg-white dark:bg-slate-900"
        >
          <table class="w-full text-left text-xs text-slate-650 dark:text-slate-400">
            <thead
              class="sticky top-0 z-10 text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase bg-slate-50 dark:bg-slate-850 border-b border-slate-200 dark:border-slate-800"
            >
              <tr>
                <th class="px-5 py-3 w-12">#</th>
                <th class="px-5 py-3">Ulasan Asli</th>
                <th class="px-5 py-3">Hasil Sentimen</th>
                <th class="px-5 py-3">Topik Cluster</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(row, idx) in batchResults.predictions"
                :key="idx"
                class="border-b border-slate-200 dark:border-slate-800/60 hover:bg-slate-50 dark:hover:bg-slate-800/30 text-[11px]"
              >
                <td class="px-5 py-3 text-slate-400">{{ idx + 1 }}</td>
                <td class="px-5 py-3 max-w-xs truncate" :title="row.Review">
                  {{ row.Review }}
                </td>
                <td class="px-5 py-3">
                  <span
                    class="px-2 py-0.5 rounded-full text-[10px] font-bold border"
                    :class="sentimentColorClass(row.sentiment_label)"
                    >{{ sentimentName(row.sentiment_label) }}</span
                  >
                </td>
                <td class="px-5 py-3 text-emerald-700 dark:text-emerald-400 font-semibold truncate max-w-[120px]" :title="row.topic">
                  {{ row.topic }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    <PipelineNav :current="9" />
  </div>
</template>
