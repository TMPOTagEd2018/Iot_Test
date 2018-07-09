"use strict";
exports.__esModule = true;
var state_1 = require("@lib/state");
var vue_1 = require("vue");
var vue_router_1 = require("vue-router");
var vuebar_1 = require("vuebar");
var app_vue_1 = require("./component/app/app.vue");
vue_1["default"].use(vuebar_1["default"]);
vue_1["default"].use(vue_router_1["default"]);
if (module.hot) {
    module.hot.accept(["./lib/state"], function () {
        var newStore = require("./lib/state");
        // swap in the new actions and mutations
        state_1["default"].hotUpdate({
            modules: newStore.modules
        });
    });
    module.hot.accept();
}
new vue_1["default"]({
    el: "#app",
    router: new vue_router_1["default"]({ routes: require("./routes").routes }),
    template: "<div><App /></div>",
    store: state_1["default"],
    components: {
        App: app_vue_1["default"]
    }
});
