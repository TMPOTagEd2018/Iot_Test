<template>
    <div id="app-root">
        <div id="scroll-root">
            <div>
                <transition name="page">
                    <router-view/>
                </transition>
            </div>
        </div>
    </div>
</template>

<script lang="ts">
import * as vue from "av-ts";
import Vue from "vue";

@vue.Component
export default class App extends Vue {
}
</script>

<style src="./app.scss" lang="scss">

</style>
