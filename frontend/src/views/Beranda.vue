<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import { useAppStore } from "../store";
import api from "../utils/api";

const router = useRouter();
const store = useAppStore();
const apiOnline = ref(null); // null = checking

const checkApi = async () => {
  try {
    await api.get("/", { timeout: 3000 });
    apiOnline.value = true;
  } catch {
    apiOnline.value = false;
  }
};

const pipeline = [
  {
    step: "01",
    label: "Input Data",
    path: "/input-data",
    desc: "Unggah CSV/Excel atau scraping Google Maps",
    color: "bg-emerald-50 dark:bg-emerald-500/10 border-emerald-200 dark:border-emerald-500/20 text-emerald-600 dark:text-emerald-400",
    icon: "M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12",
  },
  {
    step: "02",
    label: "Preprocessing",
    path: "/preprocessing",
    desc: "Lowercase, stopword removal, stemming Sastrawi",
    color: "bg-cyan-50 dark:bg-cyan-500/10 border-cyan-200 dark:border-cyan-500/20 text-cyan-600 dark:text-cyan-400",
    icon: "M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10",
  },
  {
    step: "03",
    label: "Training Model",
    path: "/training",
    desc: "Latih Random Forest dengan ekstraksi TF-IDF",
    color: "bg-indigo-50 dark:bg-indigo-500/10 border-indigo-200 dark:border-indigo-500/20 text-indigo-600 dark:text-indigo-400",
    icon: "M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z",
  },
  {
    step: "04",
    label: "Evaluasi Model",
    path: "/evaluasi",
    desc: "Classification report & Confusion Matrix grafik",
    color: "bg-blue-50 dark:bg-blue-500/10 border-blue-200 dark:border-blue-500/20 text-blue-600 dark:text-blue-400",
    icon: "M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z",
  },
  {
    step: "05",
    label: "Analisis Sentimen",
    path: "/labeling",
    desc: "Prediksi sentimen otomatis via model ML terlatih",
    color: "bg-rose-50 dark:bg-rose-500/10 border-rose-200 dark:border-rose-500/20 text-rose-600 dark:text-rose-400",
    icon: "M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z",
  },
  {
    step: "06",
    label: "Clustering",
    path: "/clustering",
    desc: "K-Means + evaluasi Calinski Index otomatis",
    color: "bg-violet-50 dark:bg-violet-500/10 border-violet-200 dark:border-violet-500/20 text-violet-600 dark:text-violet-400",
    icon: "M13 10V3L4 14h7v7l9-11h-7z",
  },
  {
    step: "07",
    label: "Topik Cluster",
    path: "/topik-cluster",
    desc: "Analisis pembobotan kata kunci penting TF-IDF",
    color: "bg-amber-50 dark:bg-amber-500/10 border-amber-200 dark:border-amber-500/20 text-amber-600 dark:text-amber-400",
    icon: "M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z",
  },
  {
    step: "08",
    label: "Insight & Laporan",
    path: "/insight",
    desc: "Rangkuman distribusi sentimen, NLG, & export Excel",
    color: "bg-yellow-50 dark:bg-yellow-500/10 border-yellow-200 dark:border-yellow-500/20 text-yellow-600 dark:text-yellow-400",
    icon: "M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z",
  },
  {
    step: "09",
    label: "Klasifikasi Baru",
    path: "/klasifikasi-baru",
    desc: "Prediksi sentimen teks tunggal atau batch file",
    color: "bg-fuchsia-50 dark:bg-fuchsia-500/10 border-fuchsia-200 dark:border-fuchsia-500/20 text-fuchsia-600 dark:text-fuchsia-400",
    icon: "M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z",
  },
];

onMounted(() => {
  checkApi();
});
</script>

<template>
  <div class="space-y-12">
    <!-- ══════════ HERO SECTION ══════════ -->
    <section class="py-6 flex flex-col-reverse lg:flex-row items-center justify-between gap-10">
      
      <!-- Left Info -->
      <div class="lg:w-7/12 text-center lg:text-left flex flex-col items-center lg:items-start">
        <!-- Minimalist Badge -->
        <div
          class="inline-flex items-center gap-1.5 px-3 py-1 mb-5 rounded-full border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-400 text-[11px] font-semibold uppercase tracking-wider transition-colors shadow-sm"
        >
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
          Sistem Analisis Sentimen &amp; Clustering
        </div>

        <!-- Title -->
        <h1
          class="text-3xl md:text-4xl lg:text-5xl font-black text-slate-800 dark:text-white leading-tight mb-4 tracking-tight transition-colors"
        >
          Analisis Sentimen Berbasis
          <span class="text-emerald-600 dark:text-emerald-400">Cluster Ulasan</span>
        </h1>

        <!-- Subtitle description -->
        <p class="text-slate-500 dark:text-slate-400 text-sm md:text-base max-w-lg leading-relaxed mb-6 transition-colors">
          Kelompokkan ulasan pengguna secara otomatis menggunakan K-Means, lalu klasifikasikan orientasi sentimennya dengan model terlatih Random Forest.
        </p>

        <!-- Call to Action -->
        <div class="flex flex-wrap gap-3">
          <button
            @click="router.push('/input-data')"
            class="flex items-center gap-2 px-6 py-3 bg-emerald-600 hover:bg-emerald-500 dark:bg-emerald-500 dark:hover:bg-emerald-400 text-white text-sm font-semibold rounded-xl transition-all shadow-sm shadow-emerald-500/10 cursor-pointer"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            Mulai Analisis
          </button>
        </div>

        <!-- Connection status -->
        <div class="mt-4 text-xs text-slate-400 dark:text-slate-500 transition-colors">
          <span v-if="apiOnline === null">Memeriksa koneksi server API...</span>
          <span v-else-if="apiOnline" class="inline-flex items-center gap-1.5 text-emerald-600 dark:text-emerald-400 font-medium">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
            Server API Terhubung (Online)
          </span>
          <span v-else class="inline-flex items-center gap-1.5 text-red-500 font-medium">
            <span class="w-1.5 h-1.5 rounded-full bg-red-500"></span>
            Koneksi API Gagal — Jalankan <code class="font-mono bg-red-500/5 px-1 py-0.5 rounded border border-red-500/10 text-xs">uvicorn main:app</code> di backend
          </span>
        </div>
      </div>

      <!-- Hero Artwork (Right) -->
      <div class="lg:w-4/12 flex justify-center mt-6 lg:mt-0">
        <img
          src="/3d-ai-transparent.png"
          alt="Dashboard AI Mascot"
          class="w-[200px] md:w-[280px] object-contain transition-all duration-300"
        />
      </div>
    </section>

    <!-- ══════════ ACTIVE SESSION ALIGNMENT ══════════ -->
    <section
      v-if="store.sessionId"
      class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-5 rounded-2xl bg-white dark:bg-[#0d1527] border border-slate-200 dark:border-slate-800 shadow-sm transition-all"
    >
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 rounded-xl bg-emerald-500/5 dark:bg-emerald-500/10 border border-emerald-500/10 dark:border-emerald-500/20 flex items-center justify-center flex-shrink-0">
          <svg class="w-5 h-5 text-emerald-600 dark:text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div>
          <p class="text-xs font-semibold text-emerald-600 dark:text-emerald-400">
            Sesi Analisis Aktif Tersedia
          </p>
          <p class="text-[11px] text-slate-400 dark:text-slate-500 font-mono mt-0.5 truncate max-w-xs sm:max-w-md">
            ID: {{ store.sessionId }}
          </p>
        </div>
      </div>
      <div class="flex gap-2 flex-shrink-0">
        <button
          @click="router.push('/preprocessing')"
          class="px-4 py-2 text-xs font-semibold text-emerald-600 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800/80 bg-emerald-50 dark:bg-emerald-500/10 hover:bg-emerald-100 dark:hover:bg-emerald-500/20 rounded-lg transition-all cursor-pointer"
        >
          Lanjutkan Proses →
        </button>
        <button
          @click="store.clearSession()"
          class="px-4 py-2 text-xs font-semibold text-slate-500 dark:text-slate-400 border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-lg transition-all cursor-pointer"
        >
          Reset Sesi
        </button>
      </div>
    </section>

    <!-- ══════════ PIPELINE STEPS ══════════ -->
    <section class="space-y-4">
      <div>
        <h2 class="text-xl font-bold text-slate-800 dark:text-white mb-0.5 tracking-tight transition-colors">
          Alur Pipeline Analisis
        </h2>
        <p class="text-slate-400 dark:text-slate-500 text-xs">
          Silakan ikuti langkah-langkah di bawah ini secara berurutan.
        </p>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <button
          v-for="item in pipeline"
          :key="item.step"
          @click="router.push(item.path)"
          class="group relative flex items-center gap-4 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm hover:bg-slate-50 dark:hover:bg-slate-800/40 hover:border-slate-300 dark:hover:border-slate-700 transition-all duration-200 text-left cursor-pointer"
        >
          <!-- Left border highlight on hover -->
          <div class="absolute inset-y-0 left-0 w-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200 bg-emerald-600 dark:bg-emerald-400 rounded-l-2xl"></div>
          
          <!-- Icon box -->
          <div
            class="flex-shrink-0 w-10 h-10 rounded-xl border flex items-center justify-center transition-colors"
            :class="item.color"
          >
            <svg class="w-4.5 h-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="item.icon" />
            </svg>
          </div>
          <!-- Label & description -->
          <div class="flex-1 min-w-0">
            <div class="flex items-baseline gap-2">
              <span class="text-[10px] font-mono font-bold text-slate-400 dark:text-slate-600">{{ item.step }}</span>
              <span class="text-[13px] font-bold text-slate-700 dark:text-slate-200 group-hover:text-slate-900 dark:group-hover:text-white transition-colors">
                {{ item.label }}
              </span>
            </div>
            <p class="text-[11px] text-slate-400 dark:text-slate-500 mt-1 leading-tight truncate">
              {{ item.desc }}
            </p>
          </div>
          <!-- Arrow icon -->
          <svg
            class="w-4 h-4 text-slate-300 dark:text-slate-600 group-hover:text-slate-500 dark:group-hover:text-slate-400 group-hover:translate-x-0.5 transition-all flex-shrink-0"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>
    </section>

    <!-- ══════════ TECHNOLOGIES USED ══════════ -->
    <section class="space-y-4">
      <div>
        <h2 class="text-xl font-bold text-slate-800 dark:text-white mb-0.5 tracking-tight transition-colors">
          Teknologi Pendukung
        </h2>
        <p class="text-slate-400 dark:text-slate-500 text-xs">
          Dukungan pustaka NLP & Machine Learning untuk analisis teks.
        </p>
      </div>
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div
          v-for="feat in [
            {
              title: 'K-Means Clustering',
              borderTheme: 'border-emerald-200 dark:border-emerald-800/80',
              iconBg: 'bg-emerald-50 dark:bg-emerald-500/10 text-emerald-600 dark:text-emerald-400',
              icon: 'M13 10V3L4 14h7v7l9-11h-7z',
              desc: 'Metode pengelompokan tanpa pengawasan (unsupervised learning) yang dievaluasi dengan Calinski-Harabasz Index.',
            },
            {
              title: 'Random Forest',
              borderTheme: 'border-blue-200 dark:border-blue-800/80',
              iconBg: 'bg-blue-50 dark:bg-blue-500/10 text-blue-600 dark:text-blue-400',
              icon: 'M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z',
              desc: 'Algoritma klasifikasi handal (supervised learning) untuk memprediksi orientasi sentimen secara presisi.',
            },
            {
              title: 'NLP Preprocessing',
              borderTheme: 'border-indigo-200 dark:border-indigo-800/80',
              iconBg: 'bg-indigo-50 dark:bg-indigo-500/10 text-indigo-600 dark:text-indigo-400',
              icon: 'M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z',
              desc: 'Pipeline lengkap pembersihan teks meliputi case folding, filtering, normalisasi slang, stopword, dan stemming Sastrawi.',
            },
          ]"
          :key="feat.title"
          class="p-5 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm transition-all duration-200"
        >
          <div
            class="w-9 h-9 rounded-xl flex items-center justify-center mb-4 border"
            :class="[feat.iconBg, feat.borderTheme]"
          >
            <svg class="w-4.5 h-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="feat.icon" />
            </svg>
          </div>
          <h3 class="text-slate-800 dark:text-slate-100 font-bold text-[14px] mb-1.5 transition-colors">
            {{ feat.title }}
          </h3>
          <p class="text-slate-500 dark:text-slate-400 text-xs leading-relaxed transition-colors">
            {{ feat.desc }}
          </p>
        </div>
      </div>
    </section>
  </div>
</template>
