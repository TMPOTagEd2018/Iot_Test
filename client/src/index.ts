import App from "@component/app/app.vue";
import Acrylic from "@component/control/acrylic/acrylic.vue";
import Autocomplete from "@component/control/autocomplete/autocomplete.vue";
import BadgeCloud from "@component/control/badge-cloud/badge-cloud.vue";
import Permission from "@component/control/permission/permission";
import Search from "@component/control/search/search.vue";
import SeeMore from "@component/control/see-more/see-more.vue";
import SiteNav from "@component/control/site-nav/site-nav.vue";
import * as Api from "@lib/api";
import store from "@lib/state";
import PageActions from "@page/page-actions.vue";
import PageLayout from "@page/page-layout.vue";
import axios from "axios";
import moment from "moment";
import Vue from "vue";
import VueRouter from "vue-router";
import Vuebar from "vuebar";

if (process.env.ssl_redirect) {
    console.log("e");
    if (location.protocol !== 'https:') {
        location.href = `https:${window.location.href.substring(window.location.protocol.length)}`;
    }
}

axios.defaults.headers["Accept"] = "application/json";

Vue.use(Vuebar);
Vue.use(VueRouter);

Vue.component("rl-acrylic", Acrylic);

Vue.component("rl-search", Search);
Vue.component("rl-autocomplete", Autocomplete);

Vue.component("rl-permission", Permission);
Vue.component("rl-see-more", SeeMore);
Vue.component("rl-badge-cloud", BadgeCloud);

Vue.component("rl-page-layout", PageLayout);
Vue.component("rl-page-actions", PageActions);
Vue.component("rl-nav", SiteNav);

type Name = string | { first: string; last: string };
const nameFormatter = (value: Name) => {
    if (!value) return "";

    if (typeof value === "string") return value;
    else return `${value.first} ${value.last}`;
};
Vue.filter("name", nameFormatter);
Vue.filter("name-list", (names: Name[]) => names.map(nameFormatter).join(", "));
Vue.filter("list", (f: any[]) =>
    f.map(g => g.toString()).join(", "));

Vue.filter("status", (value: Api.Permission[]) => {
    if (value.indexOf("user") === -1) return "Author";
    if (value.indexOf("admin") !== -1) return "Administrator";
    if (value.indexOf("check_out") !== -1) return "Librarian";
    return "User";
});

Vue.filter("segment", (value: string, spacer: string = " ", ...segments: number[]) => {
    if (segments.length === 0)
        segments = [4];

    let str = "";
    let index = 0;

    while (index < value.length) {
        for (const l of segments) {
            str += value.substr(index, l) + spacer;
            index += l;
        }
    }

    return str;
});

Vue.filter("relative-time", (time: string | Date | moment.Moment) => {
    if (!time) return "";

    return moment(time).fromNow(true);
});

Vue.filter("relative-time-verbose", (time: string | Date | moment.Moment) => {
    if (!time) return "";

    return moment(time).fromNow(false);
});

Vue.filter("time", (time: string | Date) => {
    if (!time) return "";

    return moment(time).toLocaleString();
});

Vue.filter("moment", moment);
Vue.filter("humanize", (m: moment.Duration, suffix?: boolean) => m.humanize(suffix));

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
        require("@lib/ui").vueInit(this);
        require("@lib/auth").vueInit(this);
    }
});

// if ("serviceWorker" in navigator) {
//     window.addEventListener("load", () => {
//         navigator.serviceWorker
//             .register("/sw.js")
//             .then(registration => {
//                 console.log("SW registered: ", registration);
//             })
//             .catch(registrationError => {
//                 console.log("SW registration failed: ", registrationError);
//             });
//     });
// }
