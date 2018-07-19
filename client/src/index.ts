import * as sformat from "string-format";

import Vue from "vue";
import VueRouter from "vue-router";

import moment from "moment";

import App from "@component/app/app.vue";
import store from "@lib/state";

Vue.use(VueRouter);

Vue.filter("ago", (value: string) => {
    const date = moment(value);
    return date.fromNow(true);
});

Vue.filter("format", (value: string, format: string | Function) => {
    if (typeof format === "string")
        return sformat(format, value);
    else
        return format(value);
});

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