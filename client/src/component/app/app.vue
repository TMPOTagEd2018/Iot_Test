<template>
    <div id="container">
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary shadow mb-4">
            <a class="navbar-brand" href="#">PI-STAR</a>
            <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>

            <div class="collapse navbar-collapse" id="navbarSupportedContent">
                <ul class="navbar-nav mr-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="#" :class="{ 'active': $route.path === '/' }">Dashboard</a>
                    </li>
                </ul>
            </div>
        </nav>
        <div id="row">
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
export default class App extends Vue {}
</script>

<style src="./app.scss" lang="scss">
</style>
