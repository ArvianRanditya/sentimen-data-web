import { createRouter, createWebHistory } from "vue-router";

const routes = [
  {
    path: "/",
    name: "Beranda",
    component: () => import("../views/Beranda.vue"),
  },
  {
    path: "/input-data",
    name: "DataInput",
    component: () => import("../views/DataInput.vue"),
  },
  {
    path: "/preprocessing",
    name: "Preprocessing",
    component: () => import("../views/Preprocessing.vue"),
  },
  {
    path: "/clustering",
    name: "Clustering",
    component: () => import("../views/Clustering.vue"),
  },
  {
    path: "/topik-cluster",
    name: "TopikCluster",
    component: () => import("../views/TopikCluster.vue"),
  },
  {
    path: "/labeling",
    name: "Labeling",
    component: () => import("../views/Labeling.vue"),
  },
  {
    path: "/training",
    name: "Training",
    component: () => import("../views/Training.vue"),
  },
  {
    path: "/evaluasi",
    name: "Evaluasi",
    component: () => import("../views/Evaluasi.vue"),
  },
  {
    path: "/insight",
    name: "Insight",
    component: () => import("../views/Insight.vue"),
  },
  {
    path: "/klasifikasi-baru",
    name: "KlasifikasiBaru",
    component: () => import("../views/KlasifikasiBaru.vue"),
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0, behavior: "smooth" }),
});

export default router;
