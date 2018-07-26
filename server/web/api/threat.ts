import * as Koa from "koa";
import * as KoaRouter from "koa-router";
import * as sqlite from "sqlite3";
import * as winston from "winston";
import { performance } from "perf_hooks";

interface ThreatRow {
    timestamp: number;
    node: string | null;
    threat: string | null;
    old_level: number;
    new_level: number;
};

export default (logger: winston.Logger, db: sqlite.Database) => {

    function getOne(query: string): Promise<ThreatRow> {
        return new Promise((res, rej) => db.get(query, (err, row) => err ? rej(err) : res(row)));
    }

    function getMany(query: string): Promise<ThreatRow[]> {
        return new Promise((res, rej) => db.all(query, (err, row) => err ? rej(err) : res(row)));
    }

    async function handler(ctx: Koa.Context) {
        const t0 = performance.now();

        const limit = Math.min(500, ctx.params.limit || 500);
        const { since, minLevel, maxLevel } = ctx.params;

        let condition = "";
        if (since) condition += `timestamp >= ${since}`;
        if (minLevel) condition += `new_level >= ${minLevel}`;
        if (maxLevel) condition += `new_level <= ${maxLevel}`;

        ctx.response.body = await getMany(`SELECT * FROM threats ${condition ? 'WHERE ' + condition : ''} ORDER BY timestamp DESC LIMIT ${limit}`);

        const t1 = performance.now();

        if (t1 - t0 > 1000)
            logger.warning(`database query took ${t1 - t0}ms`);
    }

    return new KoaRouter()
        .get("/", async ctx => {
            ctx.response.body = await getOne("SELECT * FROM threats ORDER BY timestamp DESC");
        })
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