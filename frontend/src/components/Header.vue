<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";
import { useAppStore } from "../store";

const route = useRoute();
const store = useAppStore();

defineProps({
  sidebarOpen: { type: Boolean, default: false }
});

const emit = defineEmits(["toggle-sidebar"]);

const titleMap = {
  Beranda: "Beranda / Dashboard",
  DataInput: "Langkah 01: Input & Pembersihan Data",
  Preprocessing: "Langkah 02: Preprocessing Teks (NLP)",
  Training: "Langkah 03: Pelatihan Model Random Forest",
  Evaluasi: "Langkah 04: Evaluasi Akurasi Model",
  Labeling: "Langkah 05: Prediksi Sentimen Dataset",
  Clustering: "Langkah 06: Pengelompokan K-Means",
  TopikCluster: "Langkah 07: Analisis Topik Kata Kunci",
  Insight: "Langkah 08: Ringkasan Analisis & NLG",
  KlasifikasiBaru: "Langkah 09: Pengujian Ulasan Baru",
};

const currentPageTitle = computed(() => {
  return titleMap[route.name] || "Analisis Sentimen";
});

const isDark = computed(() => store.theme === "dark");

const handleThemeToggle = () => {
  store.toggleTheme();
};
</script>

<template>
  <header
    class="h-[64px] border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-[#0d1527]/80 backdrop-blur-md px-6 flex items-center justify-between z-30 transition-colors duration-200"
  >
    <div class="flex items-center gap-3">
      <!-- Hamburger Menu Trigger (Mobile only) -->
      <button
        @click="emit('toggle-sidebar')"
        class="md:hidden p-2 rounded-xl text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
        title="Buka Menu"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M4 6h16M4 12h16M4 18h16"
          />
        </svg>
      </button>

      <!-- Page Title -->
      <h2 class="text-sm font-bold text-slate-800 dark:text-white tracking-wide transition-colors">
        {{ currentPageTitle }}
      </h2>
    </div>

    <div class="flex items-center gap-4">
      <!-- Session Badge -->
      <div
        v-if="store.sessionId"
        class="hidden sm:flex items-center gap-1.5 px-3 py-1 rounded-lg bg-emerald-500/5 dark:bg-emerald-500/10 border border-emerald-500/20 text-[11px] font-mono text-emerald-600 dark:text-emerald-400"
        title="Sesi Aktif"
      >
        <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
        ID: {{ store.sessionId.substring(0, 8) }}
      </div>

      <!-- Theme Switch Button -->
      <button
        @click="handleThemeToggle"
        class="p-2 rounded-xl text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-all active:scale-95 duration-200"
        :title="isDark ? 'Ganti ke Mode Terang' : 'Ganti ke Mode Gelap'"
      >
        <!-- Sun Icon (shows in dark mode to switch to light) -->
        <svg v-if="isDark" class="w-4.5 h-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
          />
        </svg>
        <!-- Moon Icon (shows in light mode to switch to dark) -->
        <svg v-else class="w-4.5 h-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646"
          />
        </svg>
      </button>
    </div>
  </header>
</template>
