import * as Koa from "koa";
import * as KoaRouter from "koa-router";
import * as winston from "winston";
import * as fs from "fs-extra";
import * as path from "path";

export default (logger: winston.Logger, basePath: string) => {
    async function handler(ctx: Koa.Context) {
        let position = 0, current = 0, start = 0;

        const POINTER_SIZE = 4;
        const RECORD_SIZE = 13;
        const RECORD_COUNT = 2400;

        const limit = Math.min(RECORD_COUNT, ctx.params.limit || 1);
        const { since, node, sensor } = ctx.params;

        const fn = path.join(basePath, "cache", node, sensor);
        if (!await fs.pathExists(fn)) {
            ctx.response.status = 404;
            return;
        }

        const handle = await fs.open(fn, "r");
        const buf = Buffer.alloc(RECORD_SIZE);
        await fs.read(handle, buf, 0, POINTER_SIZE, 0);
        position = buf.readInt32LE(0);
        start = (position - limit + RECORD_COUNT) % RECORD_COUNT;
        const records = [];

        current = start;

        while (current != position) {
            const result = await fs.read(handle, buf, 0, RECORD_SIZE, POINTER_SIZE + current * RECORD_SIZE);
            if (result.bytesRead !== RECORD_SIZE) {
                logger.warning(`Reading sensor data on ${node}/${sensor} read only ${result.bytesRead} bytes, expecting ${RECORD_SIZE}`);
            }

            const timestamp = buf.readDoubleLE(0);
            const isFloat = buf[8] == 1;
            const value = isFloat ? buf.readFloatLE(9) : buf.readInt32LE(9);

            if (timestamp === 0) continue;
            if (since && timestamp < since) continue;

            records.unshift({ timestamp, value });

            if (++current >= RECORD_COUNT) {
                current = 0;
            }
        }

        await fs.close(handle);

        ctx.response.body = records;
    }

    return new KoaRouter()
        .get("/:node([A-Za-z0-9]+)/heartbeat", async (ctx) => {
            const { node } = ctx.params;

            const fn = path.join(basePath, "cache", node, "heartbeat");
            if (!await fs.pathExists(fn)) {
                ctx.response.status = 404;
                return;
            }

            ctx.response.body = await fs.readFile(fn, "utf8");
        })
        .get("/:node([A-Za-z0-9]+)/:sensor([A-Za-z0-9]+)", handler)
        .get("/:node([A-Za-z0-9]+)/:sensor([A-Za-z0-9]+)/limit::limit(\\d+)", handler)
        .get("/:node([A-Za-z0-9]+)/:sensor([A-Za-z0-9]+)/since::since(\\d+)", handler)
        .get("/:node([A-Za-z0-9]+)/:sensor([A-Za-z0-9]+)/since::since(\\d+)/limit::limit(\\d+)", handler);
};