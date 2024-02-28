import { createRouter, createWebHistory, RouteRecordRaw } from "vue-router";
import HelloWorld from "../src/components/HelloWorld.vue";
import Login from "../src/components/Login.vue";

const routes: RouteRecordRaw[] = [
  { path: "/", component: Login },
  { path: "/HelloWorld", component: HelloWorld },
  // Add other routes as needed
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
