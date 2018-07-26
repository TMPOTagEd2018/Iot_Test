import axios from "axios";

export enum SensorType {
    Contact = "Contact Sensor",
    Accelerometer = "Accelerometer",
    Imu = "Inertial Measurement Sensor",
    Lux = "Lux Sensor",
    Microphone = "Microphone",
    PIR = "Passive Infrared Sensor"
}

export type Data = {
    timestamp: number;
    value: number;
};


export class Sensor {
    // Display name
    public name: string;

    // Internal name
    public sensorName: string;

    // Units and such
    public format: string | ((value: string) => string);

    public data: Data | null = null;

    public type: SensorType;

    constructor(name: string, sensorName: string, type: SensorType) {
        this.name = name;
        this.type = type;
        this.sensorName = sensorName;

        switch (type) {
            case SensorType.Accelerometer: this.format = "{} m/s²"; break;
            case SensorType.Imu: this.format = "{} deg/s"; break;
            case SensorType.Lux: this.format = "{} lux"; break;
            case SensorType.Microphone: this.format = "{} dB"; break;
            case SensorType.PIR: this.format = (v) => v ? "Motion not detected" : "Motion detected"; break;
            case SensorType.Contact: this.format = (v) => !v ? "Contact active" : "Contact broken"; break;
            default: this.format = "{}";
        }
    }

    public async update(node: Node) {
        try {
            const response = await axios.get(`/api/sensor/${node.nodeName}/${this.sensorName}`);
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

    public heartbeat: number | null = null;

    public sensors: Sensor[] = [];

    constructor(name: string, nodeName: string) {
        this.name = name;
        this.nodeName = nodeName;
    }

    public async update() {
        this.sensors.forEach(s => s.update(this));

        try {
            const response = await axios.get(`/api/sensor/${this.nodeName}/heartbeat`);
            if (response.status === 200) {
                this.heartbeat = response.data;
            }
        } catch { }
    }
}