<script setup>
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import api from "../utils/api";

const route = useRoute();
const emit = defineEmits(["close"]);

const apiOnline = ref(true);

const checkApi = async () => {
  try {
    await api.get("/", { timeout: 3000 });
    apiOnline.value = true;
  } catch {
    apiOnline.value = false;
  }
};

onMounted(checkApi);

const menuItems = [
  {
    name: "Beranda",
    label: "Dashboard",
    icon: "M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6",
  },
  {
    name: "DataInput",
    label: "01. Input Data",
    icon: "M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12",
  },
  {
    name: "Preprocessing",
    label: "02. Preprocessing",
    icon: "M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10",
  },
  {
    name: "Training",
    label: "03. Training Model",
    icon: "M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z",
  },
  {
    name: "Evaluasi",
    label: "04. Evaluasi Model",
    icon: "M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z",
  },
  {
    name: "Labeling",
    label: "05. Analisis Sentimen",
    icon: "M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z",
  },
  {
    name: "Clustering",
    label: "06. Clustering",
    icon: "M13 10V3L4 14h7v7l9-11h-7z",
  },
  {
    name: "TopikCluster",
    label: "07. Topik Cluster",
    icon: "M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z",
  },
  {
    name: "Insight",
    label: "08. Insight & Laporan",
    icon: "M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z",
  },
  {
    name: "KlasifikasiBaru",
    label: "09. Klasifikasi Baru",
    icon: "M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z",
  },
];
</script>

<template>
  <aside
    class="w-64 h-screen bg-white dark:bg-[#0d1527] border-r border-slate-200 dark:border-slate-800/80 text-slate-600 dark:text-slate-400 flex flex-col shadow-sm relative z-20 transition-all duration-200"
  >
    <!-- Logo & Title -->
    <div
      class="h-16 flex items-center justify-between px-6 border-b border-slate-200 dark:border-slate-800/80"
    >
      <router-link to="/" class="flex items-center" @click="emit('close')">
        <div
          class="w-7 h-7 rounded-lg bg-emerald-600 dark:bg-emerald-500 flex items-center justify-center mr-2.5 shadow-sm"
        >
          <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2.5"
              d="M13 10V3L4 14h7v7l9-11h-7z"
            />
          </svg>
        </div>
        <span
          class="text-[14px] font-bold text-slate-800 dark:text-slate-100 tracking-wide transition-colors"
          >SentimenAI</span
        >
      </router-link>

      <!-- Mobile Close Trigger -->
      <button
        @click="emit('close')"
        class="md:hidden p-1 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-400 hover:text-slate-600 transition-colors"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2.5"
            d="M6 18L18 6M6 6l12 12"
          />
        </svg>
      </button>
    </div>

    <!-- Navigation Items -->
    <nav class="flex-1 px-3 py-4 space-y-1 overflow-y-auto scrollbar-thin">
      <router-link
        v-for="item in menuItems"
        :key="item.name"
        :to="{ name: item.name }"
        @click="emit('close')"
        class="flex items-center px-4 py-2.5 rounded-xl transition-all duration-150 group relative"
        :class="
          route.name === item.name
            ? 'bg-emerald-500/5 dark:bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 font-semibold'
            : 'hover:bg-slate-100 dark:hover:bg-slate-800/40 text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200'
        "
      >
        <!-- Active indicator line -->
        <div
          v-if="route.name === item.name"
          class="absolute left-0 w-1 h-5 bg-emerald-600 dark:bg-emerald-400 rounded-r-full"
        ></div>

        <!-- Icon -->
        <svg
          class="w-4 h-4 mr-3"
          :class="
            route.name === item.name
              ? 'text-emerald-600 dark:text-emerald-400'
              : 'text-slate-400 dark:text-slate-500 group-hover:text-emerald-500'
          "
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            :d="item.icon"
          />
        </svg>
        <span class="text-[13px]">{{ item.label }}</span>
      </router-link>
    </nav>

    <!-- API Status Footer -->
    <div class="p-4 border-t border-slate-200 dark:border-slate-800/80">
      <div
        class="bg-slate-50 dark:bg-slate-800/30 p-3 rounded-xl border border-slate-200 dark:border-slate-800/80"
      >
        <p class="text-[10px] text-slate-400 dark:text-slate-500 font-medium mb-1.5 uppercase tracking-wider">
          Status API
        </p>
        <div class="flex items-center">
          <span class="relative flex h-2 w-2 mr-2">
            <span
              v-if="apiOnline"
              class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"
            ></span>
            <span
              class="relative inline-flex rounded-full h-2 w-2"
              :class="apiOnline ? 'bg-emerald-500' : 'bg-red-500'"
            ></span>
          </span>
          <span class="text-[12px] font-semibold text-slate-700 dark:text-slate-300">
            {{ apiOnline ? "Terhubung" : "Terputus" }}
          </span>
        </div>
      </div>
    </div>
  </aside>
</template>
