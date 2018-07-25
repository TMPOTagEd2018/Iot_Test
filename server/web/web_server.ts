import * as path from "path";
import * as http from "http";
import * as http2 from "http2";
import * as https from "https";
import * as fs from "fs-extra";

import * as Koa from "koa";
import * as KoaRouter from "koa-router";
import * as KoaStatic from "koa-static";

import * as winston from "winston";

import ThreatApi from "./api/threat";
import SensorApi from "./api/sensor";

import * as sqlite from "sqlite3";
import { Server } from "net";

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
            level: process.env.NODE_ENV === "development" ? "debug" : "info",
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
        logger.error(`error at ${ctx.method} ${ctx.href}: ${e}`);
    }
});

app.on("error", (err, ctx) => {
    logger.error(err);
});

app.use(router.routes());
app.use(KoaStatic(clientPath, { gzip: true }));

type HttpCallback = (req: http.IncomingMessage | http2.Http2ServerRequest, res: http.ServerResponse | http2.Http2ServerResponse) => void;
type ServerFactory = (callback: HttpCallback) => Server;
let serverFactory: ServerFactory;

let flags: { [flag: string]: boolean } = {};

flags.dev = process.env.NODE_ENV === "development";
if (process.argv.includes("--production")) flags.dev = false;
if (process.argv.includes("--dev")) flags.dev = true;

if (flags.dev) {
    logger.info("Running in development mode.");
} else {
    logger.info("Running in production mode.");
}

flags.ssl = !flags.dev;
if (process.argv.includes("--ssl")) flags.ssl = true;

flags.http2 = false;
if (process.argv.includes("--http2")) flags.http2 = true;

if (flags.ssl) {
    logger.info("Using SSL.");

    if (flags.http2) {
        logger.info("Using HTTP2.");
        serverFactory = (cb) => http2.createSecureServer({
            cert: fs.readFileSync(path.join(basePath, "certs/http/cert.pem")),
            key: fs.readFileSync(path.join(basePath, "certs/http/key.pem"))
        }, cb);
    } else {
        serverFactory = (cb) => https.createServer({
            cert: fs.readFileSync(path.join(basePath, "certs/http/cert.pem")),
            key: fs.readFileSync(path.join(basePath, "certs/http/key.pem"))
        }, cb);
    }
} else {
    if (flags.http2) {
        logger.info("Using HTTP2.");
        serverFactory = http2.createServer;
    } else {
        serverFactory = http.createServer;
    }
}

const server = serverFactory(app.callback());
const port = process.env.PORT || 8000;
server.listen(port);

logger.info(`Server is running on port ${port}`);