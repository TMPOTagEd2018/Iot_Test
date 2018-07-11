<template>
    <canvas ref="canvas" />
</template>

<script lang="ts">
import axios from "axios";
import moment from "moment";

import * as vue from "av-ts";
import Vue from "vue";
import { Chart, ChartPoint } from "chart.js";

type Range = { min: number; max: number; };

@vue.Component
export default class LiveChart extends Vue {
    public data: ChartPoint[] = [];
    public label?: string;
    public yrange: Range = { min: 0, max: 10};
    public xrange: Range = { min: 0, max: 10};

    private chart!: Chart;

    @vue.Watch("label")
    private labelChanged(newVal: string, oldVal: string) {
        if (this.chart.data.datasets) this.chart.data.datasets[0].label = newVal;

        this.chart.update();
    }

    @vue.Watch("yrange")
    private yrangeChanged(newVal: Range, oldVal: Range) {
        if (
            this.chart.config.options &&
            this.chart.config.options.scales &&
            this.chart.config.options.scales.yAxes
        )
        {
            for(const axis of this.chart.config.options.scales.yAxes) {
                if(!axis.ticks) axis.ticks = {};
                axis.ticks.min = this.yrange.min;
                axis.ticks.max = this.yrange.max;
            }
        }

        this.chart.update();
    }

    @vue.Watch("xrange")
    private xrangeChanged(newVal: Range, oldVal: Range) {
        if (
            this.chart.config.options &&
            this.chart.config.options.scales &&
            this.chart.config.options.scales.xAxes
        )
        {
            for(const axis of this.chart.config.options.scales.xAxes) {
                if(!axis.ticks) axis.ticks = {};
                axis.ticks.min = this.xrange.min;
                axis.ticks.max = this.xrange.max;
            }
        }

        this.chart.update();
    }

    @vue.Lifecycle
    public mounted() {
        const canvas = this.$refs.canvas as HTMLCanvasElement;
        const ctx = canvas.getContext("2d") as CanvasRenderingContext2D;

        const grad = ctx.createLinearGradient(0, 100, 0, 0);
        grad.addColorStop(0, "rgba(0, 128, 0, 1)");
        grad.addColorStop(0.5, "rgba(128, 128, 0, 1)");
        grad.addColorStop(1, "rgba(128, 0, 0, 1)");

        const gradHalf = ctx.createLinearGradient(0, 100, 0, 0);
        gradHalf.addColorStop(0, "rgba(0, 128, 0, 0.5)");
        gradHalf.addColorStop(0.5, "rgba(128, 128, 0, 0.5)");
        gradHalf.addColorStop(1, "rgba(128, 0, 0, 0.5)");

        const chart = new Chart(ctx, {
            type: "line",
            data: {
                datasets: [
                    {
                        label: this.label || undefined,
                        // lineTension: 0,
                        cubicInterpolationMode: "monotone",
                        borderWidth: 2,
                        borderColor: "transparent",
                        pointBorderColor: "white",
                        pointBackgroundColor: "grey",
                        pointRadius: 0,
                        pointHoverRadius: 3,
                        pointHitRadius: 6,
                        backgroundColor: gradHalf,
                    }
                ]
            },
            options: {
                maintainAspectRatio: false,
                legend: { display: false },
                tooltips: { enabled: false },
                scales: {
                    xAxes: [
                        {
                            type: "linear",
                            // time: { minUnit: "second", unit: "minute", displayFormats:  },
                            ticks: {
                                maxTicksLimit: 1,
                                callback (value) {
                                    return moment(value).fromNow();
                                }
                            }
                        }
                    ],
                    yAxes: [
                        {
                            ticks: { suggestedMin: this.min, suggestedMax: this.max } as any
                        }
                    ]
                }
            }
        });
        chart.update();

        this.chart = chart;
    }

    public update() {
        this.chart.update();
    }

    public push(...data: ChartPoint[]) {
        if (this.chart.data.datasets) {
            for (const set of this.chart.data.datasets) {
                if (set.data) {
                    for (const datum of data) {
                        (set.data as ChartPoint[]).push(datum);
                    }

                }
            }
        }

        this.chart.update();
        this.data.push(...data);

    }

    public shift() {
        if (this.chart.data.datasets) {
            for (const set of this.chart.data.datasets) {
                if (set.data) (set.data as ChartPoint[]).shift();
            }
        }

        this.data.shift();

        this.chart.update();
    }

    public pop() {
        if (this.chart.data.datasets) {
            for (const set of this.chart.data.datasets) {
                if (set.data) (set.data as ChartPoint[]).pop();
            }
        }

        this.data.pop();

        this.chart.update();
    }
}
</script>

<style>
</style>