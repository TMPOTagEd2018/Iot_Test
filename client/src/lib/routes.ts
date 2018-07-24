import store from "@lib/state";
import VueRouter from "vue-router";

const router = new VueRouter({
    routes: [
        { path: "/", component: () => import("@page/dashboard/dashboard.vue") }
    ],
    mode: process.env.NODE_ENV === "development" ? "hash" : "history"
});


export default router;
