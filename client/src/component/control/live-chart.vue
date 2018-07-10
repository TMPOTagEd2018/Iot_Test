<template>
  <canvas ref="canvas" />
</template>

<script lang="ts">
import axios from "axios";
import * as vue from "av-ts";
import Vue from "vue";
import { Chart } from "chart.js";

type DataPoint = { label: string; value: number };

@vue.Component
export default class LiveChart extends Vue {
  public data: DataPoint[] = [];

  private chart!: Chart;

  @vue.Watch("data")
  private dataChanged(newVal: DataPoint[], oldVal: DataPoint[]) {
    this.chart.data.labels = newVal.map(d => d.label);

    if (this.chart.data.datasets)
      this.chart.data.datasets[0].data = newVal.map(d => d.value);

    this.chart.update();
  }

  @vue.Lifecycle
  public mounted() {
    const canvas = this.$refs.canvas as HTMLCanvasElement;
    const ctx = canvas.getContext("2d");
    const chart = new Chart(ctx as CanvasRenderingContext2D, {
      type: "line",
      data: {
        labels: this.data.map(d => d.label),
        datasets: [
          {
            data: this.data.map(d => d.value),
            borderWidth: 1
          }
        ]
      }
    });
    chart.update();

    this.chart = chart;
  }
}
</script>

<style>
</style>