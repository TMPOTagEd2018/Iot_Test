<template>
    <canvas ref="canvas" style="width:100%; height: 100%;" />
</template>

<script lang="ts">
import axios from "axios";
import moment from "moment";

import * as vue from "av-ts";
import Vue from "vue";

import * as smoothie from "smoothie";

type Range = { min: number; max: number; };

@vue.Component
export default class LiveChart extends Vue {
    public yrange: Range = { min: 0, max: 10 };
    public window: number = 10000;

    private chart!: smoothie.SmoothieChart;
    private series!: smoothie.TimeSeries;

    @vue.Watch("yrange")
    private yrangeChanged(newVal: Range, oldVal: Range) {
        this.chart.options.minValue = newVal.min;
        this.chart.options.maxValue = newVal.max;
    }

    @vue.Watch("window")
    private windowChanged(newVal: number, oldVal: number) {
    }

    @vue.Lifecycle
    public mounted() {
        const canvas = this.$refs.canvas as HTMLCanvasElement;
        const ctx = canvas.getContext("2d") as CanvasRenderingContext2D;

        const grad = ctx.createLinearGradient(0, 200, 0, 0);
        grad.addColorStop(0, "rgba(0, 128, 0, 1)");
        grad.addColorStop(0.5, "rgba(128, 128, 0, 1)");
        grad.addColorStop(1, "rgba(128, 0, 0, 1)");

        const gradHalf = ctx.createLinearGradient(0, 200, 0, 0);
        gradHalf.addColorStop(0, "rgba(0, 128, 0, 0.5)");
        gradHalf.addColorStop(0.5, "rgba(128, 128, 0, 0.5)");
        gradHalf.addColorStop(1, "rgba(128, 0, 0, 0.5)");

        const series = new smoothie.TimeSeries({});

        const chart = new smoothie.SmoothieChart({
            minValue: this.yrange.min,
            maxValue: this.yrange.max,
            maxValueScale: 1.1,
            minValueScale: 1.1,
            timestampFormatter: (d) => moment(d).fromNow(),
            grid: { fillStyle: "transparent", strokeStyle: "transparent", millisPerLine: 60 * 1000 },
            labels: {
                fillStyle: "black",
                fontFamily: "sans-serif",
                disabled: true, // only disables y axis
                showIntermediateLabels: false
            },            
            millisPerPixel: 250,
            responsive: true
        });

        chart.addTimeSeries(series, {});
        const options = chart.getTimeSeriesOptions(series);;
        options.fillStyle = gradHalf as any;
        options.strokeStyle = grad as any;
        options.lineWidth = 2;
        chart.streamTo(canvas, 500);

        this.chart = chart;
        this.series = series;
    }

    public push(...data: { t: number; y: number; }[]) {
        for (const point of data)
            this.series.append(point.t, point.y);
    }
}
</script>

<style>
</style>