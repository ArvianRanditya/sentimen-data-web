<script setup>
import { computed } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();

const props = defineProps({
  current: {
    type: [Number, String],
    required: true,
  },
});

const currentStep = computed(() => Number(props.current));

const steps = [
  { step: 1, label: "Input Data", path: "/input-data" },
  { step: 2, label: "Preprocessing", path: "/preprocessing" },
  { step: 3, label: "Training Model", path: "/training" },
  { step: 4, label: "Evaluasi Model", path: "/evaluasi" },
  { step: 5, label: "Analisis Sentimen", path: "/labeling" },
  { step: 6, label: "Clustering", path: "/clustering" },
  { step: 7, label: "Topik Cluster", path: "/topik-cluster" },
  { step: 8, label: "Insight", path: "/insight" },
  { step: 9, label: "Klasifikasi", path: "/klasifikasi-baru" },
];

const prev = computed(
  () => steps.find((s) => s.step === currentStep.value - 1) || null
);
const next = computed(
  () => steps.find((s) => s.step === currentStep.value + 1) || null
);
const current = computed(() => steps.find((s) => s.step === currentStep.value));
</script>

<template>
  <div class="mt-10 pt-6 border-t border-slate-700/50">
    <div class="flex items-center justify-between gap-4">
      <!-- ← Prev -->
      <button
        v-if="prev"
        @click="router.push(prev.path)"
        class="flex items-center gap-2 px-5 py-2.5 rounded-xl border border-slate-700 bg-slate-900/60 text-slate-400 hover:text-slate-100 hover:bg-slate-800 hover:border-slate-600 transition-all duration-200 text-sm font-medium group"
      >
        <svg
          class="w-4 h-4 group-hover:-translate-x-0.5 transition-transform duration-200"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M10 19l-7-7m0 0l7-7m-7 7h18"
          />
        </svg>
        <span>
          <span class="text-[10px] text-slate-600 block leading-none font-mono"
            >STEP {{ prev.step }}</span
          >
          {{ prev.label }}
        </span>
      </button>
      <div v-else class="w-32"></div>

      <!-- Step indicator dots -->
      <div class="hidden sm:flex items-center gap-1.5">
        <div
          v-for="s in steps"
          :key="s.step"
          class="rounded-full transition-all duration-300 cursor-pointer"
          :class="
            s.step === currentStep.valu
              ? 'w-6 h-2 bg-emerald-500'
              : s.step < currentStep.value
              ? 'w-2 h-2 bg-emerald-700/60 hover:bg-emerald-600'
              : 'w-2 h-2 bg-slate-700 hover:bg-slate-600'
          "
          :title="s.label"
          @click="router.push(s.path)"
        ></div>
      </div>

      <!-- Step counter (mobile) -->
      <div class="sm:hidden text-xs text-slate-500 font-mono">
        {{ currentStep.value }} / {{ steps.length }}
      </div>

      <!-- Next → -->
      <button
        v-if="next"
        @click="router.push(next.path)"
        class="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-green-500 hover:from-emerald-400 hover:to-green-400 text-white shadow-lg shadow-emerald-500/20 transition-all duration-200 text-sm font-semibold group hover:-translate-y-0.5"
      >
        <span class="text-right">
          <span
            class="text-[10px] text-emerald-200/70 block leading-none font-mono"
            >STEP {{ next.step }}</span
          >
          {{ next.label }}
        </span>
        <svg
          class="w-4 h-4 group-hover:translate-x-0.5 transition-transform duration-200"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M14 5l7 7m0 0l-7 7m7-7H3"
          />
        </svg>
      </button>

      <!-- Last step badge -->
      <div
        v-else
        class="flex items-center gap-2 px-5 py-2.5 rounded-xl border border-emerald-500/30 bg-emerald-500/10 text-emerald-400 text-sm font-semibold"
      >
        <svg
          class="w-4 h-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        Selesai
      </div>
    </div>
  </div>
</template>
