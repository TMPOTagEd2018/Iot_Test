import axios from "axios";

export enum SensorType {
    Contact = "Contact Sensor",
    Accelerometer = "Accelerometer",
    Imu = "Inertial Measurement Sensor",
    Lux = "Lux Sensor",
    Microphone = "Microphone",
    PIR = "Passive Infrared Sensor"
}

export type SensorData = {
    timestamp: number;
    value: number;
};

export type ThreatData = {
    timestamp: number;
    node: string | null;
    threat: string | null;
    old_level: number;
    new_level: number;
};

export class Sensor {
    // Display name
    public name: string;

    // Internal name
    public sensorName: string;

    public threatLevel: number = 0;
    public data: SensorData | null = null;
    public type: SensorType;

    constructor(name: string, sensorName: string, type: SensorType) {
        this.name = name;
        this.type = type;
        this.sensorName = sensorName;
    }

    public async update(node: Node) {
        try {
            const response = await axios.get(`/api/sensor/${node.nodeName}/${this.sensorName}/`);
            if (response.status === 200) {
                this.data = response.data[0];
            }
        } catch {

        }
    }
}

export class Node {
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