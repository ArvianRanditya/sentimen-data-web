<script setup>
import { ref, onMounted, watch } from "vue";
import { useAppStore } from "../store";
import Sidebar from "./Sidebar.vue";
import Header from "./Header.vue";
import ChatWidget from "./ChatWidget.vue";

const store = useAppStore();
const mobileSidebarOpen = ref(false);

const applyTheme = (theme) => {
  if (theme === "dark") {
    document.documentElement.classList.add("dark");
  } else {
    document.documentElement.classList.remove("dark");
  }
};

// Initialize theme on mount
onMounted(() => {
  applyTheme(store.theme);
});

// Watch theme changes
watch(
  () => store.theme,
  (newTheme) => {
    applyTheme(newTheme);
  }
);
</script>

<template>
  <div
    class="min-h-screen bg-slate-50 dark:bg-[#090d16] font-sans text-slate-700 dark:text-slate-300 flex overflow-hidden transition-colors duration-200"
  >
    <!-- Permanent Sidebar (Desktop) -->
    <Sidebar class="hidden md:flex flex-shrink-0" />

    <!-- Mobile Sidebar overlay (Drawer/Slide-over) -->
    <transition name="drawer">
      <div v-if="mobileSidebarOpen" class="fixed inset-0 z-40 md:hidden flex">
        <!-- Backdrop -->
        <div
          class="fixed inset-0 bg-black/40 backdrop-blur-sm"
          @click="mobileSidebarOpen = false"
        ></div>

        <!-- Drawer Content -->
        <Sidebar
          class="relative z-50 flex shadow-2xl animate-slide-in"
          @close="mobileSidebarOpen = false"
        />
      </div>
    </transition>

    <!-- Main Workspace -->
    <div class="flex-1 flex flex-col min-w-0 h-screen overflow-hidden">
      <!-- Header -->
      <Header
        :sidebarOpen="mobileSidebarOpen"
        @toggle-sidebar="mobileSidebarOpen = !mobileSidebarOpen"
      />

      <!-- Scrollable Content Area -->
      <main class="flex-1 overflow-y-auto px-6 md:px-10 py-8 relative z-10 scrollbar-thin">
        <div class="max-w-5xl mx-auto pb-16">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </div>
      </main>
    </div>

    <!-- AI Chatbot Widget -->
    <ChatWidget />
  </div>
</template>

<style>
/* Transition Fade for Page Component Change */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(4px);
}

/* Slide-in & Drawer Animation for Mobile Sidebar */
.drawer-enter-active,
.drawer-leave-active {
  transition: opacity 0.2s ease;
}
.drawer-enter-from,
.drawer-leave-to {
  opacity: 0;
}

.drawer-enter-active .animate-slide-in {
  animation: slide-in 0.25s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
.drawer-leave-active .animate-slide-in {
  animation: slide-out 0.2s ease-in forwards;
}

@keyframes slide-in {
  from {
    transform: translateX(-100%);
  }
  to {
    transform: translateX(0);
  }
}

@keyframes slide-out {
  from {
    transform: translateX(0);
  }
  to {
    transform: translateX(-100%);
  }
}
</style>
