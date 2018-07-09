import 'bootstrap';

import Vue from "vue";
import VueRouter from "vue-router";

import App from "@component/app/app.vue";
import store from "@lib/state";

Vue.use(VueRouter);

if (module.hot) {
    module.hot.accept(["./lib/state"], () => {
        const newStore = require("./lib/state");
        // swap in the new actions and mutationsa
        store.hotUpdate({
            modules: newStore.modules
        });
    });

    module.hot.accept();
}

const v = new Vue({
    el: "#app",
    router: require("@lib/routes").default,
    template: "<App />",
    store,
    components: {
        App
    },
    created: function created(this: Vue) {
        // require("@lib/auth").vueInit(this);
    }
});