<template>
    <div class="container">
        <live-chart :data="[3, 4, 3]" ref="threatChart" />

        <div class="alert alert-danger" v-if="threatLevel < threatLevelMax">
            Activity was detected earlier.
            <a href="#">Review the logs.</a>
        </div>

        <h1 class="display-2 text-success text-center" v-if="threatLevel == 0">
            You're safe and sound.
        </h1>

        <h1 class="display-2 text-info text-center" v-else-if="threatLevel < 3">
            Potential activity detected.
        </h1>

        <h1 class="display-2 text-warning text-center" v-else-if="threatLevel < 6">
            Suspicious activity detected.
        </h1>

        <h1 class="display-2 text-danger text-center" v-else>
            Critical activity detected.
        </h1>

        <p class="text-center font-weight-bold">
            Level {{ threatLevel }}
        </p>

        <div class="card-columns">
            <div class="card" v-for="(node, $index) in nodes" :key="$index">
                <h5 class="card-header">{{ node.name }}</h5>

                <ul class="list-group list-group-flush">
                    <li class="list-group-item" v-for="(sensor, $index) in node.sensors" :key="$index">
                        <h6>{{ sensor.name }}</h6>
                        <p class="text-muted">{{ sensor.type }}</p>
                        <p>{{ sensor.value }}</p>
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

import { setInterval } from "timers";

enum SensorType {
  Contact = "Contact Sensor",
  Accelerometer = "Accelerometer",
  Imu = "Inertial Measurement Sensor",
  Lux = "Lux Sensor",
  Microphone = "Microphone", 
  PIR = "Passive Infrared Sensor"
}

type ThreatData = { timestamp: number, node: string | null, threat: string | null, old_level: number, new_level: number };

class Sensor {
  // Display name
  public name: string;

  // Internal name
  public sensorName: string;

  public threatLevel: number = 0;
  public value: number = 0;
  public type: SensorType;

  constructor(name: string, sensorName: string, type: SensorType) {
    this.name = name;
    this.type = type;
    this.sensorName = sensorName;
  }

  public async update(node: Node) {
    const response = await axios.get(`/api/sensor/${node.nodeName}/${this.sensorName}/`);
    this.value = response.data;
  }
}

class Node {
  // Display name
  public name: string;

  // Internal name
  public nodeName: string;

  public sensors: Sensor[] = [];

  constructor(name: string, nodeName: string) {
    this.name = name;
    this.nodeName = nodeName;
  }

  public async update() {
    this.sensors.forEach(s => s.update(this));
  }
}

@vue.Component({ components: { LiveChart }})
export default class Dashboard extends Vue {
  public nodes: Node[] = [];
  public threatLevel: number = 0;
  public threatLevelMax: number = 0;

  @vue.Lifecycle
  public created() {
    // this is a simple project, so let's hard code the nodes

    const room = new Node("Room", "room"),
      box = new Node("Box", "box"),
      door = new Node("Door", "door");

    room.sensors = [
      new Sensor("Microphone 1", "mic", SensorType.Microphone), 
      new Sensor("Light 1", "lux", SensorType.Lux)
    ];

    box.sensors = [
      new Sensor("IMU 1", "imu", SensorType.Imu), 
      new Sensor("Contact 1", "contact", SensorType.Contact)
    ];
    
    door.sensors = [
      new Sensor("IMU 1", "imu", SensorType.Accelerometer), 
      new Sensor("Contact 1", "contact", SensorType.Contact)
    ];

    this.nodes.push(room, box, door);

    setInterval(async () => {
      this.nodes.forEach(n => n.update());

      const time = (+new Date()) / 1000;
      
      const res = await axios.get(`/api/threat/since:${Math.floor(time) - 3600}/limit:1000`);
      const data: ThreatData[] = res.data;

      this.threatLevel = data[0].new_level;
      this.threatLevelMax = Math.max(this.threatLevel, this.threatLevelMax);

      const chart: any = this.$refs.threatChart as LiveChart;
      
      chart.data = data.map(d => { return { label: d.timestamp.toString(), value: d.new_level }});
    }, 1000);
  }
}
</script>

<style>
</style>
