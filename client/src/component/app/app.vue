<template>
    <div id="app-root">
        <transition :duration="1500" name="fade">
            <div class="background" :style="{ 'background-image': backgroundUrls.back }" v-show="backgroundFace === 'back'">
            </div>
        </transition>

        <transition :duration="1500" name="fade">
            <div class="background" :style="{ 'background-image': backgroundUrls.front }" v-show="backgroundFace === 'front'">
            </div>
        </transition>

        <div id="scroll-root" v-bar>
            <div>
                <transition name="page">
                    <router-view/>
                </transition>
            </div>
        </div>

        <div class="overlay" v-show="$store.state.ui.loading">
            <img :src="require('@res/img/indeterminate.svg')" />
        </div>
    </div>
</template>

<script lang="ts">
import * as vue from "av-ts";
import Vue from "vue";

@vue.Component
export default class App extends Vue {
    get background(): string {
        return this.$store.getters["ui/background/css-url"];
    }

    public backgroundUrls: { front: string | null; back: string | null } = {
        front: null,
        back: null
    };
    public backgroundFace: "front" | "back" = "front";

    @vue.Watch("background")
    public backgroundChanged(current: string, old: string) {
        this.backgroundFace = "front";
        this.backgroundUrls.front = old;
        this.backgroundUrls.back = current;
        this.backgroundFace = "back";
    }

    @vue.Lifecycle
    public created() {
        this.backgroundUrls = { front: this.background, back: null };

        setTimeout(() => this.$store.dispatch("ui/background/refresh"), 0);
    }
}
</script>

<style src="./app.scss" lang="scss">

</style>
