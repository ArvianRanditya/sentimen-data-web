<script setup>
import { ref } from "vue";
import api, { baseURL } from "../utils/api";
import { useAppStore } from "../store";
import { useRouter } from "vue-router";
import AppIcon from "../components/AppIcon.vue";
import PipelineNav from "../components/PipelineNav.vue";

const store = useAppStore();
const router = useRouter();

const inputMode = ref("upload");
const urls = ref("");
const maxReviews = ref(50);
const isScraping = ref(false);
const isUploading = ref(false);
const isCleaning = ref(false);

const successMsg = ref("");
const errorMsg = ref("");
const uploadedFile = ref(null);

const rawPreview = ref(null);
const cleanPreview = ref(null);
const totalRaw = ref(0);
const totalClean = ref(0);

const clearMessages = () => {
  successMsg.value = "";
  errorMsg.value = "";
};

const handleScrape = async () => {
  if (!urls.value.trim()) {
    errorMsg.value = "URL tidak boleh kosong.";
    return;
  }
  clearMessages();
  rawPreview.value = null;
  cleanPreview.value = null;
  isScraping.value = true;
  try {
    const response = await api.post("/api/data/scrape", {
      urls: urls.value,
      max_reviews: maxReviews.value,
    });
    store.setSessionId(response.data.session_id);
    rawPreview.value = response.data.preview;
    totalRaw.value = response.data.total_rows;
    successMsg.value = "Scraping berhasil!";
  } catch (error) {
    errorMsg.value =
      "Gagal scraping: " + (error.response?.data?.detail || error.message);
  } finally {
    isScraping.value = false;
  }
};

const onFileChange = (event) => {
  const f = event.target.files[0];
  if (f) {
    uploadedFile.value = f;
    clearMessages();
  }
};

const handleFileUpload = async () => {
  if (!uploadedFile.value) {
    errorMsg.value = "Pilih file terlebih dahulu.";
    return;
  }
  const formData = new FormData();
  formData.append("file", uploadedFile.value);
  clearMessages();
  rawPreview.value = null;
  cleanPreview.value = null;
  isUploading.value = true;
  try {
    const response = await api.post(
      "/api/data/upload",
      formData
    );
    store.setSessionId(response.data.session_id);
    rawPreview.value = response.data.preview;
    totalRaw.value = response.data.total_rows;
    successMsg.value = `File berhasil diupload! Total ${response.data.total_rows} baris.`;
  } catch (error) {
    errorMsg.value =
      "Gagal upload: " + (error.response?.data?.detail || error.message);
  } finally {
    isUploading.value = false;
  }
};

const handleClean = async () => {
  if (!store.sessionId) return;
  clearMessages();
  isCleaning.value = true;
  try {
    const response = await api.post("/api/data/clean", {
      session_id: store.sessionId,
    });
    cleanPreview.value = response.data.preview;
    totalClean.value = response.data.clean_rows;
    successMsg.value = `Cleaning selesai! Tersisa ${response.data.clean_rows} dari ${response.data.original_rows} ulasan.`;
  } catch (error) {
    errorMsg.value =
      "Gagal cleaning: " + (error.response?.data?.detail || error.message);
  } finally {
    isCleaning.value = false;
  }
};

const downloadRawData = () => {
  if (!store.sessionId) {
    alert("Session tidak ditemukan");
    return;
  }
  window.open(
    `${baseURL}/api/data/download/${store.sessionId}`,
    "_blank"
  );
};
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div
      class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4"
    >
      <div>
        <h1 class="text-2xl font-bold text-slate-800 dark:text-white mb-1 transition-colors">Input Data</h1>
        <p class="text-slate-500 dark:text-slate-400 text-xs transition-colors">
          Impor ulasan Google Maps melalui Scraping URL atau unggah berkas CSV/Excel.
        </p>
      </div>
      <div
        class="bg-slate-100 dark:bg-slate-800/80 p-1 rounded-xl inline-flex border border-slate-200 dark:border-slate-800 transition-colors"
      >
        <button
          @click="
            inputMode = 'scraping';
            clearMessages();
          "
          class="px-4 py-2 rounded-lg text-xs font-semibold transition-all duration-150 cursor-pointer"
          :class="
            inputMode === 'scraping'
              ? 'bg-emerald-600 dark:bg-emerald-500 text-white shadow-sm'
              : 'text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200'
          "
        >
          Scraping Maps
        </button>
        <button
          @click="
            inputMode = 'upload';
            clearMessages();
          "
          class="px-4 py-2 rounded-lg text-xs font-semibold transition-all duration-150 cursor-pointer"
          :class="
            inputMode === 'upload'
              ? 'bg-emerald-600 dark:bg-emerald-500 text-white shadow-sm'
              : 'text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200'
          "
        >
          Upload File
        </button>
      </div>
    </div>

    <!-- Messages -->
    <div
      v-if="successMsg"
      class="p-4 bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/20 rounded-xl text-emerald-700 dark:text-emerald-400 text-xs flex items-center transition-all"
    >
      <AppIcon name="check" class="w-4.5 h-4.5 mr-2 flex-shrink-0" />
      {{ successMsg }}
    </div>
    <div
      v-if="errorMsg"
      class="p-4 bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20 rounded-xl text-red-700 dark:text-red-400 text-xs flex items-center transition-all"
    >
      <AppIcon name="error" class="w-4.5 h-4.5 mr-2 flex-shrink-0" />
      {{ errorMsg }}
    </div>

    <!-- Main Card -->
    <div
      class="bg-white dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800/80 rounded-2xl p-6 shadow-sm relative overflow-hidden transition-all duration-200"
    >
      <!-- Scraping Form -->
      <div v-if="inputMode === 'scraping'" class="space-y-5">
        <div>
          <label class="block text-xs font-bold text-slate-500 dark:text-slate-400 mb-2 uppercase tracking-wide"
            >URLs Google Maps</label
          >
          <textarea
            v-model="urls"
            rows="4"
            class="w-full bg-slate-50 focus:bg-white dark:bg-slate-950/40 border border-slate-200 dark:border-slate-800 rounded-xl p-4 text-slate-800 dark:text-slate-200 placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/15 focus:border-emerald-500/50 transition-all text-xs"
            placeholder="Masukkan URL tempat Google Maps (1 link per baris)"
          ></textarea>
        </div>
        <div class="max-w-xs">
          <label class="block text-xs font-bold text-slate-500 dark:text-slate-400 mb-2 uppercase tracking-wide"
            >Maksimal Ulasan per URL</label
          >
          <input
            type="number"
            v-model="maxReviews"
            min="1"
            max="1000"
            class="w-full bg-slate-50 focus:bg-white dark:bg-slate-950/40 border border-slate-200 dark:border-slate-800 rounded-xl p-3 text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500/15 focus:border-emerald-500/50 transition-all text-xs font-medium"
          />
        </div>
        <button
          @click="handleScrape"
          :disabled="isScraping"
          class="flex items-center px-6 py-3 bg-emerald-600 hover:bg-emerald-500 dark:bg-emerald-500 dark:hover:bg-emerald-400 text-white text-xs font-semibold rounded-xl transition-all disabled:opacity-50 shadow-sm shadow-emerald-500/10 cursor-pointer"
        >
          <AppIcon v-if="!isScraping" name="play" class="w-4 h-4 mr-2" />
          <AppIcon v-else name="spinner" class="animate-spin w-4 h-4 mr-2" />
          {{ isScraping ? "Scraping..." : "Mulai Scraping" }}
        </button>
      </div>

      <!-- Upload Form -->
      <div v-else class="space-y-5">
        <label class="block cursor-pointer">
          <div
            class="border-2 border-dashed border-slate-350 dark:border-slate-800 hover:border-emerald-500 dark:hover:border-emerald-500/60 rounded-2xl p-10 text-center transition-colors duration-200"
          >
            <div
              class="mx-auto w-12 h-12 rounded-xl bg-slate-100 dark:bg-slate-800/80 flex items-center justify-center mb-4 transition-colors"
            >
              <AppIcon name="upload" class="w-6 h-6 text-slate-400 dark:text-slate-500" />
            </div>
            <h3 class="text-sm font-semibold text-slate-700 dark:text-slate-200 mb-1 transition-colors">
              {{ uploadedFile ? uploadedFile.name : "Klik untuk memilih berkas ulasan" }}
            </h3>
            <p class="text-[11px] text-slate-400 dark:text-slate-500 transition-colors">
              Format yang didukung: <strong>.csv</strong> atau <strong>.xlsx</strong>
            </p>
            <p class="text-[10px] text-slate-400/80 dark:text-slate-550 mt-1">
              Berkas wajib memiliki kolom bernama <strong>Review</strong> (R kapital)
            </p>
          </div>
          <input
            type="file"
            class="hidden"
            accept=".csv,.xlsx,.xls"
            @change="onFileChange"
          />
        </label>

        <div
          v-if="uploadedFile"
          class="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-800/30 border border-slate-250/60 dark:border-slate-800 rounded-xl transition-colors"
        >
          <div class="flex items-center">
            <AppIcon name="document" class="w-6 h-6 text-emerald-600 dark:text-emerald-400 mr-3" />
            <div>
              <p class="text-slate-700 dark:text-slate-200 text-xs font-semibold">
                {{ uploadedFile.name }}
              </p>
              <p class="text-slate-400 dark:text-slate-500 text-[10px]">
                {{ (uploadedFile.size / 1024).toFixed(1) }} KB
              </p>
            </div>
          </div>
          <button
            @click="handleFileUpload"
            :disabled="isUploading"
            class="flex items-center px-4 py-2 bg-emerald-600 hover:bg-emerald-500 dark:bg-emerald-500 dark:hover:bg-emerald-400 text-white text-xs font-semibold rounded-lg shadow-sm transition-all disabled:opacity-50 cursor-pointer"
          >
            <AppIcon
              v-if="isUploading"
              name="spinner"
              class="animate-spin w-3.5 h-3.5 mr-2"
            />
            {{ isUploading ? "Mengunggah..." : "Unggah Sekarang" }}
          </button>
        </div>
      </div>
    </div>

    <!-- Raw Preview -->
    <div
      v-if="rawPreview"
      class="bg-white dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800/80 rounded-2xl p-6 shadow-sm transition-all duration-200"
    >
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-4">
        <div class="flex items-center gap-3">
          <div
            class="w-9 h-9 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center"
          >
            <AppIcon name="table" class="w-4.5 h-4.5 text-slate-500 dark:text-slate-400" />
          </div>
          <div>
            <h3 class="text-sm font-bold text-slate-800 dark:text-slate-200">
              Preview Data Mentah (Raw)
            </h3>
            <p class="text-[11px] text-slate-500 dark:text-slate-400">
              Total {{ totalRaw }} baris ulasan ditemukan (menampilkan maks 5 ulasan)
            </p>
          </div>
        </div>
        <button
          @click="handleClean"
          :disabled="isCleaning"
          class="flex items-center px-4 py-2 bg-slate-50 hover:bg-slate-100 dark:bg-slate-800/80 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-700/85 text-slate-700 dark:text-slate-300 text-xs font-semibold rounded-lg transition-all disabled:opacity-50 cursor-pointer"
        >
          <AppIcon
            v-if="isCleaning"
            name="spinner"
            class="animate-spin w-3.5 h-3.5 mr-2"
          />
          <AppIcon v-else name="trash" class="w-3.5 h-3.5 mr-2" />
          Hapus Duplikat &amp; Kosong
        </button>
      </div>
      
      <!-- Table content -->
      <div
        class="max-h-[300px] overflow-auto rounded-xl border border-slate-200 dark:border-slate-800/60"
      >
        <table class="w-full text-left text-xs text-slate-600 dark:text-slate-400">
          <thead
            class="sticky top-0 z-10 text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase bg-slate-50 dark:bg-slate-850/80 border-b border-slate-200 dark:border-slate-800/80"
          >
            <tr>
              <th
                v-for="key in Object.keys(rawPreview[0])"
                :key="key"
                class="px-5 py-3 border-b border-slate-200 dark:border-slate-800/80"
              >
                {{ key }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(row, idx) in rawPreview"
              :key="idx"
              class="border-b border-slate-200 dark:border-slate-800/60 hover:bg-slate-50 dark:hover:bg-slate-800/30"
            >
              <td
                v-for="(val, key) in row"
                :key="key"
                class="px-5 py-3 truncate max-w-xs text-[11px]"
              >
                {{ val }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div class="flex justify-end mt-4">
        <button
          @click="downloadRawData"
          class="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 dark:bg-emerald-500 dark:hover:bg-emerald-400 text-white text-xs font-semibold shadow-sm transition cursor-pointer"
        >
          Download Data Mentah
        </button>
      </div>
    </div>

    <!-- Clean Preview -->
    <div
      v-if="cleanPreview"
      class="bg-white dark:bg-slate-900/50 border border-emerald-500/20 dark:border-emerald-500/10 rounded-2xl p-6 border-l-4 border-l-emerald-600 dark:border-l-emerald-500 shadow-sm"
    >
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-4">
        <div class="flex items-center gap-3">
          <div
            class="w-9 h-9 rounded-lg bg-emerald-500/5 dark:bg-emerald-500/10 flex items-center justify-center"
          >
            <AppIcon name="check" class="w-4.5 h-4.5 text-emerald-600 dark:text-emerald-400" />
          </div>
          <div>
            <h3 class="text-sm font-bold text-emerald-600 dark:text-emerald-400">
              Hasil Pembersihan Data (Clean)
            </h3>
            <p class="text-[11px] text-slate-500 dark:text-slate-400">
              Ulasan kosong &amp; duplikat telah dibersihkan. Tersisa {{ totalClean }} ulasan valid.
            </p>
          </div>
        </div>
        <button
          @click="router.push('/preprocessing')"
          class="flex items-center px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 dark:bg-emerald-500 dark:hover:bg-emerald-400 text-white text-xs font-bold rounded-lg shadow-sm transition-all cursor-pointer"
        >
          Lanjut ke Preprocessing
          <AppIcon name="arrow_right" class="w-3.5 h-3.5 ml-2" />
        </button>
      </div>

      <div
        class="max-h-[300px] overflow-auto rounded-xl border border-slate-200 dark:border-slate-800/60"
      >
        <table class="w-full text-left text-xs text-slate-600 dark:text-slate-400">
          <thead
            class="sticky top-0 z-10 text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase bg-slate-50 dark:bg-slate-850/80 border-b border-slate-200 dark:border-slate-800/80"
          >
            <tr>
              <th
                v-for="key in Object.keys(cleanPreview[0])"
                :key="key"
                class="px-5 py-3 border-b border-slate-200 dark:border-slate-800/80"
              >
                {{ key }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(row, idx) in cleanPreview"
              :key="idx"
              class="border-b border-slate-200 dark:border-slate-800/60 hover:bg-slate-50 dark:hover:bg-slate-800/30"
            >
              <td
                v-for="(val, key) in row"
                :key="key"
                class="px-5 py-3 truncate max-w-xs text-[11px]"
              >
                {{ val }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <PipelineNav :current="1" />
  </div>
</template>
