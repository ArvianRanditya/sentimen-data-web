<script setup>
import { ref, onMounted, watch, nextTick } from "vue";
import { useAppStore } from "../store";
import api from "../utils/api";

const store = useAppStore();
const isOpen = ref(false);
const messageInput = ref("");
const isLoading = ref(false);
const chatContainer = ref(null);

const messages = ref([
  {
    role: "assistant",
    content: "Halo! Saya adalah Asisten AI Unwahas. Tanyakan apa saja tentang ulasan/review yang sudah Anda unggah.",
  },
]);

const scrollToBottom = async () => {
  await nextTick();
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
  }
};

const handleSendMessage = async () => {
  if (!messageInput.value.trim() || isLoading.value || !store.sessionId) return;

  const userText = messageInput.value.trim();
  messages.value.push({ role: "user", content: userText });
  messageInput.value = "";
  isLoading.value = true;
  await scrollToBottom();

  try {
    const historyPayload = messages.value.slice(1, -1).map((m) => ({
      role: m.role === "user" ? "user" : "assistant",
      content: m.content,
    }));

    const response = await api.post("/api/chat", {
      session_id: store.sessionId,
      message: userText,
      history: historyPayload,
    });

    messages.value.push({
      role: "assistant",
      content: response.data.answer,
    });
  } catch (error) {
    messages.value.push({
      role: "assistant",
      content: "Maaf, asisten AI gagal memproses pesan Anda. Pastikan API Key Gemini sudah terpasang di file `.env` backend Anda.",
    });
  } finally {
    isLoading.value = false;
    await scrollToBottom();
  }
};

const resetChat = () => {
  messages.value = [
    {
      role: "assistant",
      content: "Halo! Obrolan telah di-reset. Ada yang bisa saya bantu tentang ulasan Anda?",
    },
  ];
};

watch(isOpen, (newVal) => {
  if (newVal) {
    scrollToBottom();
  }
});
</script>

<template>
  <div class="fixed bottom-6 right-6 z-50 flex flex-col items-end font-sans">
    
    <!-- ── PANEL CHAT WIDGET ── -->
    <transition name="chat-panel">
      <div
        v-if="isOpen"
        class="w-[340px] sm:w-[380px] h-[500px] mb-4 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800/80 rounded-2xl shadow-xl flex flex-col overflow-hidden transition-all duration-200"
      >
        
        <!-- Header -->
        <div class="p-4 bg-slate-50 dark:bg-slate-800/40 border-b border-slate-200 dark:border-slate-800/80 flex items-center justify-between transition-colors duration-200">
          <div class="flex items-center gap-2.5">
            <!-- AI Avatar Status -->
            <div class="relative w-8 h-8 rounded-lg bg-emerald-600 dark:bg-emerald-500 flex items-center justify-center shadow-sm">
              <svg class="w-4.5 h-4.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
              <!-- Online status pulse -->
              <span class="absolute -bottom-0.5 -right-0.5 flex h-2 w-2">
                <span class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75" :class="store.sessionId ? 'bg-emerald-400' : 'bg-amber-400'"></span>
                <span class="relative inline-flex rounded-full h-2 w-2" :class="store.sessionId ? 'bg-emerald-500' : 'bg-amber-500'"></span>
              </span>
            </div>
            <div>
              <h3 class="text-xs font-bold text-slate-800 dark:text-slate-100 transition-colors">Asisten AI Unwahas</h3>
              <p class="text-[10px] tracking-wide" :class="store.sessionId ? 'text-emerald-600 dark:text-emerald-400 font-semibold' : 'text-slate-400 dark:text-slate-500'">
                {{ store.sessionId ? 'Data Sesi Terhubung' : 'Belum Ada Sesi Aktif' }}
              </p>
            </div>
          </div>
          
          <div class="flex items-center gap-1">
            <!-- Reset Button -->
            <button
              @click="resetChat"
              title="Reset Obrolan"
              class="p-1.5 rounded-lg text-slate-400 dark:text-slate-500 hover:text-slate-600 dark:hover:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 1121.21 7.89" />
              </svg>
            </button>
            <!-- Close Button -->
            <button
              @click="isOpen = false"
              class="p-1.5 rounded-lg text-slate-400 dark:text-slate-500 hover:text-slate-600 dark:hover:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Chat Messages Container -->
        <div
          ref="chatContainer"
          class="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50/50 dark:bg-slate-950/20 scrollbar-thin"
        >
          <div
            v-for="(msg, idx) in messages"
            :key="idx"
            class="flex flex-col"
            :class="msg.role === 'user' ? 'items-end' : 'items-start'"
          >
            <!-- Message Bubble -->
            <div
              class="max-w-[85%] rounded-2xl p-3 text-xs leading-relaxed border"
              :class="
                msg.role === 'user'
                  ? 'bg-emerald-500/5 dark:bg-emerald-500/10 border-emerald-500/20 text-emerald-700 dark:text-emerald-300 rounded-tr-none'
                  : 'bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-800/80 text-slate-600 dark:text-slate-300 rounded-tl-none'
              "
            >
              <div class="whitespace-pre-line">{{ msg.content }}</div>
            </div>
            <!-- Metadata label -->
            <span class="text-[9px] text-slate-400 dark:text-slate-500 mt-1 px-1">
              {{ msg.role === 'user' ? 'Anda' : 'Asisten AI' }}
            </span>
          </div>

          <!-- Loading state -->
          <div v-if="isLoading" class="flex flex-col items-start">
            <div class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-800 rounded-2xl rounded-tl-none p-3.5 flex items-center gap-2">
              <span class="flex h-2 w-2 relative">
                <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              <span class="text-[11px] text-slate-400 dark:text-slate-500 font-medium">Asisten sedang mengetik...</span>
            </div>
          </div>
        </div>

        <!-- Input Form Area -->
        <div class="p-3 bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800/80 transition-colors">
          <!-- Non-active session notice -->
          <div
            v-if="!store.sessionId"
            class="text-[10px] text-amber-600 dark:text-amber-500 text-center py-2 px-2 bg-amber-500/5 dark:bg-amber-500/10 border border-amber-500/20 rounded-xl"
          >
            ⚠️ Unggah data ulasan terlebih dahulu di menu <strong>Input Data</strong> untuk memulai obrolan.
          </div>

          <!-- Active Form -->
          <form v-else @submit.prevent="handleSendMessage" class="flex gap-2 items-center">
            <input
              type="text"
              v-model="messageInput"
              :disabled="isLoading"
              placeholder="Tanyakan sesuatu tentang ulasan..."
              class="flex-1 text-xs bg-slate-50 dark:bg-slate-950/40 border border-slate-200 dark:border-slate-800 rounded-xl px-3 py-2.5 text-slate-800 dark:text-slate-200 placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:border-emerald-500/50 focus:ring-2 focus:ring-emerald-500/10 transition-all disabled:opacity-50"
            />
            <button
              type="submit"
              :disabled="!messageInput.trim() || isLoading"
              class="w-9 h-9 rounded-xl bg-emerald-600 dark:bg-emerald-500 hover:bg-emerald-500 dark:hover:bg-emerald-400 text-white flex items-center justify-center flex-shrink-0 disabled:opacity-40 disabled:cursor-not-allowed transition-all shadow-sm shadow-emerald-500/10"
            >
              <svg class="w-4 h-4 transform rotate-90" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </form>
        </div>

      </div>
    </transition>

    <!-- ── LAUNCH BUTTON WIDGET ── -->
    <button
      @click="isOpen = !isOpen"
      class="w-12 h-12 rounded-full bg-emerald-600 dark:bg-emerald-500 hover:bg-emerald-500 dark:hover:bg-emerald-400 flex items-center justify-center shadow-md shadow-emerald-500/15 hover:scale-105 active:scale-95 transition-all duration-150 cursor-pointer"
      title="Buka Asisten AI"
    >
      <svg v-if="!isOpen" class="w-5.5 h-5.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
      </svg>
      <svg v-else class="w-5.5 h-5.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 9l-7 7-7-7" />
      </svg>
    </button>

  </div>
</template>

<style scoped>
/* Slide fade animation for chat panel */
.chat-panel-enter-active {
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}
.chat-panel-leave-active {
  transition: all 0.15s ease-in;
}
.chat-panel-enter-from {
  opacity: 0;
  transform: translateY(12px) scale(0.97);
}
.chat-panel-leave-to {
  opacity: 0;
  transform: translateY(8px) scale(0.98);
}
</style>
