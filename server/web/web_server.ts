import * as path from "path";
import * as http from "http";

import * as Koa from "koa";
import * as KoaRouter from "koa-router";
import * as KoaStatic from "koa-static";

import * as winston from "winston";

import ThreatApi from "./api/threat";
import SensorApi from "./api/sensor";

import * as sqlite from "sqlite3";

const logger = winston.createLogger({
    transports: [
        new winston.transports.Console({
            format: winston.format.combine(
                winston.format.timestamp(),
                winston.format.splat(),
                winston.format.colorize(),
                winston.format.printf(info => {
                    return `${info.timestamp} | ${info.level}: ${info.message}`;
                })),
            level: "debug",
            handleExceptions: true
        })
    ],
    levels: winston.config.syslog.levels
});

const basePath = path.join(__dirname, "..");
const clientPath = path.join(basePath, "../client/dist");
const dbPath = path.join(basePath, "data.db");

logger.info(`Base path: ${basePath}`);
logger.info(`Database path: ${dbPath}`);

const db = new sqlite.Database(dbPath);

const app = new Koa();
const router = new KoaRouter();
const api = new KoaRouter();

api.use("/threat", ThreatApi(db).routes());
api.use("/sensor", SensorApi(logger, basePath).routes());

router.use("/api", api.routes());

app.use(async (ctx, next) => {
    logger.debug(`request: ${ctx.protocol} ${ctx.method} ${ctx.href}`);

    try {
        await next();
    } catch (e) {
        logger.error(e);
    }
});

app.on("error", (err, ctx) => {
    logger.error(err);
});

app.use(router.routes());
app.use(KoaStatic(clientPath, { gzip: true }));

const serverFactory = http.createServer;
const server = serverFactory(app.callback());
const port = process.env.PORT || 8000;
server.listen(port);

logger.info(`Server is running on port ${port}`);