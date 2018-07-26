import * as Koa from "koa";
import * as KoaRouter from "koa-router";
import * as winston from "winston";
import * as path from "path";
import * as fs from "fs-extra";
import { performance } from "perf_hooks";

export default (logger: winston.Logger, basePath: string) => {
    async function handler(ctx: Koa.Context) {
        const t0 = performance.now();

        let position = 0, current = 0, start = 0, total = 0;

        const POINTER_SIZE = 4;
        const RECORD_SIZE = 12;
        const RECORD_COUNT = 2400;

        const limit = Math.min(RECORD_COUNT, ctx.params.limit || 1);
        const { since, minLevel, maxLevel } = ctx.params;

        const fn = path.join(basePath, "cache/threat");

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
                logger.warning(`reading sensor data on threat cache read only ${result.bytesRead} bytes, expecting ${RECORD_SIZE}`);
            }

            const timestamp = buf.readDoubleLE(0);
            const value = buf.readFloatLE(8);

            if(value < minLevel) continue;
            if(value > maxLevel) continue;

            total++;

            if (++current >= RECORD_COUNT) {
                current = 0;
            }

            if (timestamp === 0) continue;
            if (since && timestamp < since) continue;

            records.unshift({ timestamp, value });
        }


        await fs.close(handle);

        ctx.response.body = records;

        const t1 = performance.now();

        if (t1 - t0 > 1000)
            logger.warning(`threat cache query took ${t1 - t0}ms`);
    }

    return new KoaRouter()
        .get("/", handler)
        .get("/limit::limit(\\d+)", handler)
        .get("/since::since(\\d+)", handler)
        .get("/since::since(\\d+)/limit::limit(\\d+)", handler)
        .get("/minlevel::minLevel(\\d+)", handler)
        .get("/maxlevel::maxLevel(\\d+)", handler)
        .get("/minlevel::minLevel(\\d+)/limit::limit(\\d+)", handler)
        .get("/minlevel::maxLevel(\\d+)/limit::limit(\\d+)", handler)
        .get("/maxlevel::minLevel(\\d+)/since::since(\\d+)", handler)
        .get("/maxlevel::maxLevel(\\d+)/since::since(\\d+)", handler)
        .get("/minlevel::minLevel(\\d+)/maxlevel::maxLevel(\\d+)", handler)
        .get("/minlevel::minLevel(\\d+)/maxlevel::maxLevel(\\d+)/limit::limit(\\d+)", handler)
        .get("/minlevel::minLevel(\\d+)/maxlevel::maxLevel(\\d+)/since::since(\\d+)", handler);
};