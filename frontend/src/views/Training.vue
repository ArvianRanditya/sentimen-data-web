<script setup>
import { ref } from "vue";
import api from "../utils/api";
import { useAppStore } from "../store";
import { useRouter } from "vue-router";
import PipelineNav from "../components/PipelineNav.vue";

const store = useAppStore();
const router = useRouter();

const isTraining = ref(false);
const errorMsg = ref("");
const successMsg = ref("");

const testSize = ref(20);

const handleTrain = async () => {
  if (!store.sessionId) {
    errorMsg.value = "Sesi tidak ditemukan. Pastikan Anda sudah mengupload berkas ulasan.";
    return;
  }
  isTraining.value = true;
  errorMsg.value = "";
  successMsg.value = "";
  try {
    const response = await api.post("/api/model/train", {
      session_id: store.sessionId,
      max_features: 500,
      test_size: testSize.value / 100,
    });
    store.setTrainingResults({
      report: response.data.classification_report,
      cm: response.data.confusion_matrix,
      cmLabels: response.data.confusion_matrix_labels,
      testAcc: response.data.test_accuracy,
      trainAcc: response.data.train_accuracy,
    });
    successMsg.value = `Model berhasil dilatih! Akurasi: ${(
      response.data.test_accuracy * 100
    ).toFixed(1)}%`;
    
    // Auto navigate to Evaluation step
    router.push("/evaluasi");
  } catch (error) {
    errorMsg.value =
      "Gagal melatih model: " + (error.response?.data?.detail || error.message);
  } finally {
    isTraining.value = false;
  }
};
</script>

<template>
  <div class="space-y-6">
    <!-- Title -->
    <div>
      <h1 class="text-2xl font-bold text-slate-800 dark:text-white mb-1 transition-colors">
        Latihan Model Klasifikasi
      </h1>
      <p class="text-slate-500 dark:text-slate-400 text-xs transition-colors">
        Melatih algoritma Random Forest menggunakan dataset berlabel (data_training.xlsx) berbasis pembobotan TF-IDF.
      </p>
    </div>

    <!-- Messages -->
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
      class="p-4 bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/20 rounded-xl text-emerald-700 dark:text-emerald-400 text-xs flex items-center gap-2 transition-all"
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

    <!-- Training Config -->
    <div
      class="bg-white dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800/80 rounded-2xl p-6 shadow-sm transition-all duration-200"
    >
      <h3 class="text-sm font-bold text-slate-800 dark:text-slate-200 mb-5 transition-colors">
        Parameter TF-IDF &amp; Training
      </h3>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <!-- Feature parameter -->
        <div>
          <label class="block text-xs font-bold text-slate-500 dark:text-slate-400 mb-2 uppercase tracking-wide">
            Max Features (TF-IDF)
          </label>
          <div
            class="p-3 rounded-xl bg-slate-50 dark:bg-slate-950/40 border border-slate-200 dark:border-slate-800 text-emerald-600 dark:text-emerald-400 font-bold text-center text-xs transition-colors"
          >
            500 (Optimal Configuration)
          </div>
          <div class="flex justify-between text-[10px] text-slate-400 dark:text-slate-500 mt-1.5 transition-colors">
            <span>500</span>
            <span>5000</span>
          </div>
        </div>

        <!-- Train/Test size parameter -->
        <div>
          <label class="block text-xs font-bold text-slate-500 dark:text-slate-400 mb-2 uppercase tracking-wide"
            >Ukuran Data Uji (Test Size):
            <span class="text-emerald-600 dark:text-emerald-400 font-bold ml-1"
              >{{ testSize }}%</span
            ></label
          >
          <input
            type="range"
            min="10"
            max="40"
            step="5"
            v-model="testSize"
            class="w-full accent-emerald-600 dark:accent-emerald-500 h-2 bg-slate-200 dark:bg-slate-800 rounded-lg appearance-none cursor-pointer"
          />
          <div class="flex justify-between text-[10px] text-slate-400 dark:text-slate-500 mt-1.5 transition-colors">
            <span>10%</span>
            <span>40%</span>
          </div>
        </div>
      </div>

      <div class="flex flex-col items-center pt-5 border-t border-slate-200 dark:border-slate-800/80 transition-colors">
        <p class="text-slate-500 dark:text-slate-400 text-xs text-center mb-4 leading-relaxed transition-colors">
          Model Random Forest dilatih dengan 150 pohon keputusan (estimators) serta fitur penyeimbang kelas ulasan otomatis (class_weight="balanced").
        </p>
        <button
          @click="handleTrain"
          :disabled="isTraining || !store.sessionId"
          class="flex items-center justify-center w-full max-w-sm px-6 py-3 bg-emerald-600 hover:bg-emerald-500 dark:bg-emerald-500 dark:hover:bg-emerald-400 text-white text-xs font-bold rounded-xl shadow-sm transition-all disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
        >
          <svg
            v-if="isTraining"
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
          <span>{{ isTraining ? "Melatih model..." : "Latih Model Random Forest" }}</span>
        </button>
        <p v-if="store.evaluationReport" class="mt-3 text-xs text-emerald-600 dark:text-emerald-450 font-medium transition-colors">
          ✓ Model sudah siap. Lihat visualisasi hasil di halaman Evaluasi.
        </p>
      </div>
    </div>
    <PipelineNav :current="3" />
  </div>
</template>
