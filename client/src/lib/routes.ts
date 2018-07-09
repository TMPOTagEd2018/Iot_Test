import store from "@lib/state";
import VueRouter from "vue-router";

const router = new VueRouter({
    routes: [
    ],
    mode: process.env.NODE_ENV === "development" ? "hash" : "history"
});

// router.afterEach((to, from) => {
//     store.commit("ui/setLoading", false);
// });

// router.beforeResolve((to, from, next) => {
//     store.commit("ui/setLoading", true);
//     next();
// });

// router.beforeEach(async (to, from, next) => {
//     if (!to.meta.permissions) {
//         next();
//         return;
//     }

//     const state = store.state as any;

//     if (!state.auth.initialized)
//         await new Promise((resolve, reject) => {
//             const handle = store.watch(
//                 s => (s as any).auth.user,
//                 (val, old) => {
//                     resolve(val);
//                     handle();
//                 }
//             );
//         });

//     to.meta.permissions.every((p: Permission) => hasPermission(state.auth.user as Person, p)) ? next() : next("/");
// });

export default router;
