import * as Koa from "koa";
import * as KoaRouter from "koa-router";
import * as fs from "fs-extra";
import * as path from "path";

export default (basePath: string) => {
    async function handler(ctx: Koa.Context) {
        const POINTER_SIZE = 4;
        const RECORD_SIZE = 9;
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
        const position = buf.readInt32LE(0);
        const start = (position - limit + RECORD_COUNT) % RECORD_COUNT;
        const records = [];
        
        for(let current = start; current != position; current = (current + 1) % RECORD_SIZE) {
            await fs.read(handle, buf, 0, RECORD_SIZE, POINTER_SIZE + current * RECORD_SIZE);
            const timestamp = buf.readDoubleLE(0);
            const value = buf[8];

            if(timestamp === 0) continue;
            if(since && timestamp < since) continue;

            records.unshift({ timestamp, value });
        }

        await fs.close(handle);

        ctx.response.body = records;
    }

    return new KoaRouter()
        .get("/:node([A-Za-z0-9]+)/:sensor([A-Za-z0-9]+)", handler)
        .get("/:node([A-Za-z0-9]+)/:sensor([A-Za-z0-9]+)/limit::limit(\\d+)", handler)
        .get("/:node([A-Za-z0-9]+)/:sensor([A-Za-z0-9]+)/since::since(\\d+)", handler)
        .get("/:node([A-Za-z0-9]+)/:sensor([A-Za-z0-9]+)/since::since(\\d+)/limit::limit(\\d+)", handler);
};