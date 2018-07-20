<template>
    <div class="container">
        <div class="alert alert-danger" v-if="threatLevel < threatLevelMax">
            Activity was detected earlier.
            <a href="#">Review the logs.</a>
        </div>

        <div class="alert alert-danger" v-for="(error, $index) in errors" :key="$index">
            {{ error }}
        </div>

        <div style="height: 150pt" class="rounded mb-2 border position-relative">
            <live-chart ref="threatChart" />

            <h1 class="threat-description display-3 text-success text-center" v-if="threatLevel < 0.5">
                You're safe and sound.
            </h1>

            <h1 class="threat-description display-3 text-info text-center" v-else-if="threatLevel < 3">
                Potential activity detected.
            </h1>

            <h1 class="threat-description display-3 text-warning text-center" v-else-if="threatLevel < 6">
                Suspicious activity detected.
            </h1>

            <h1 class="threat-description display-3 text-danger text-center" v-else>
                Critical activity detected.
            </h1>
        </div>

        <p class="text-center font-weight-bold">
            Level {{ threatLevel }}
        </p>

        <div class="card-columns">
            <div class="card" v-for="(node, $index) in nodes" :key="$index">
                <h5 class="card-header d-flex justify-content-between align-items-baseline">
                    <span>{{ node.name }}</span>
                    <span class="font-weight-bold text-warning small" v-if="node.heartbeat === null">Not connected</span>
                    <span class="font-weight-bold text-danger small" v-else-if="node.heartbeat < +new Date() / 1000 - 10">Offline</span>
                    <span class="text-muted small" v-else>Last seen {{ node.heartbeat * 1000 | ago }} ago</span>
                </h5>

                <ul class="list-group list-group-flush">
                    <li class="list-group-item" v-for="(sensor, $index) in node.sensors" :key="$index">
                        <h6>{{ sensor.name }}</h6>
                        <p class="text-muted">{{ sensor.type }}</p>
                        <template v-if="sensor.data">
                            <p class="m-0">
                                <span :class="{ 'text-dark': (+new Date() - sensor.data.timestamp * 1000) < 10000 }">{{ sensor.data.value | format(sensor.format) }}</span>
                                <span class="small">
                                    {{ sensor.data.timestamp * 1000 | ago }} ago
                                </span>
                            </p>
                        </template>
                        <template v-else>
                            <span class="text-muted font-italic">No data available.</span>
                        </template>
                    </li>
                </ul>
            </div>
        </div>
    </div>
</template>

<script lang="ts">
import axios from "axios";
import * as vue from "av-ts";
import Vue from "vue";

import LiveChart from "@control/live-chart.vue";
import { Node, Sensor, SensorType, ThreatData } from "./index";


@vue.Component({ components: { LiveChart } })
export default class Dashboard extends Vue {
    public errors: string[] = [];

    public nodes: Node[] = [];
    public threatLevel: number = 0;
    public threatLevelMax: number = 0;

    public window: number = 60 * 10;

    private lastUpdate: number = 0;

    @vue.Lifecycle
    public created() {
        // this is a simple project, so let's hard code the nodes

        const room = new Node("Room", "room"),
            box = new Node("Box", "box"),
            door = new Node("Door", "door");

        room.sensors = [
            new Sensor("Motion Sensor 1", "pir", SensorType.PIR),
            new Sensor("Light 1", "lux", SensorType.Lux)
        ];

        box.sensors = [
            new Sensor("Accelerometer 1", "accel", SensorType.Accelerometer),
            new Sensor("Contact 1", "contact", SensorType.Contact)
        ];

        door.sensors = [
            new Sensor("IMU 1", "imu", SensorType.Imu),
            new Sensor("Contact 1", "contact", SensorType.Contact)
        ];

        this.nodes.push(room, box, door);

        this.update()
            .then(() => setInterval(this.update, 1000))
            .catch(err => this.errors.push(`Failed to update. Please check your internet connection.`));
    }

    @vue.Lifecycle
    public mounted() {
        const chart: any = this.$refs.threatChart as LiveChart;

        chart.yrange = { min: 0, max: 10 };
        chart.window = this.window;
    }

    public async update() {
        this.nodes.forEach(n => n.update());

        try {
            const res = await axios.get("/api/threat/");
            const data: ThreatData = res.data;
            this.threatLevel = data.new_level;
            this.threatLevelMax = Math.max(this.threatLevel, this.threatLevelMax);
        } catch {
        }

        try {
            const time = +new Date() / 1000;

            const res = await axios.get(
                `/api/threat/since:${Math.floor(Math.min(this.lastUpdate, time - this.window))}/limit:200`
            );

            let data: ThreatData[] = res.data;

            const chart: any = this.$refs.threatChart as LiveChart;

            if (data.length === 0) {
                chart.push({ t: (time + 1) * 1000, y: this.threatLevel });
                return;
            }

            let points = data
                .filter(d => d.timestamp > this.lastUpdate)
                .map(d => { return { t: d.timestamp * 1000, y: d.new_level }; })
                .sort((a, b) => a.t < b.t ? -1 : 1);

            chart.push(...points);
            this.lastUpdate = time;
        } catch {
        }
    }
}
</script>

<style lang="scss">
.threat-description
{
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;

    display: flex;
    align-content: center;
    flex-direction: column;
    justify-content: center;

    margin: 0;

    transition-duration: 0.15s;
    transition-property: opacity;

    background: rgba(255, 255, 255, 0.5);

    opacity: 1;

    &:hover
    {
        opacity: 0.25;
    }
}

</style>
