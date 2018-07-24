import argparse as ap
import subprocess as sp
import os.path as path
import os
import sys
import colorama as cr
from threading import Thread
from queue import Queue, Empty
from time import sleep

cr.init(autoreset=True)


def which(program):
    import os

    def is_exe(fpath):
        return path.isfile(fpath) and os.access(fpath, os.X_OK)

    if is_exe(program):
        return path.abspath(program)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for p in os.environ["PATH"].split(os.pathsep):
            exe_file = path.join(p, program)
            if is_exe(exe_file) or is_exe(exe_file + ".exe"):
                return exe_file

    return None


LEVEL_ERROR = 0
LEVEL_WARNING = 1
LEVEL_INFO = 2

file_dir = path.dirname(path.abspath(__file__))


def log(message, level=LEVEL_INFO, src="pi-star"):
    style = cr.Fore.RESET

    if level == LEVEL_ERROR:
        style = cr.Fore.RED

    if level == LEVEL_WARNING:
        style = cr.Fore.YELLOW

    tag = ""

    if src == "pi-star":
        tag = cr.Fore.BLUE

    if src == "web-server":
        tag = cr.Fore.CYAN

    if src == "mqtt-server":
        tag = cr.Fore.MAGENTA

    if src == "npm":
        tag = cr.Fore.GREEN

    if src == "webpack":
        tag = cr.Fore.LIGHTBLUE_EX

    print(f"{tag}[{src}] {style}{message}")


def getmtime_directory(directory, filter=None):
    return max(path.getmtime(root) for root, _, _ in os.walk(directory) if filter is None or filter(root))


def start_web_server():
    web_path = path.join(file_dir, "web")
    web_file = path.join(web_path, "web_server")

    if which("node") is None:
        log("node js not found; please install node js; exiting", LEVEL_ERROR)
        sys.exit(-1)

    if getmtime_directory(web_path, lambda f: "node_modules" not in f) > path.getmtime(web_file + ".js"):
        log("new typescript files detected; running tsc.", LEVEL_INFO)

        if which("tsc") is None:
            log("tsc not found; installing tsc", LEVEL_INFO)
            tsc_install = sp.run(["npm", "i", "-g", "typescript"], shell=True)

            if tsc_install.returncode == 0:
                log("tsc installed.", LEVEL_INFO)
            else:
                log(f"tsc install failed with error code {tsc_install.returncode}", LEVEL_WARNING)

                for line in tsc_install.stdout:
                    log(line.decode(), src="npm")

        tsc = sp.Popen("tsc", cwd=web_path, stdout=sp.PIPE, shell=True)

        while tsc.poll() is None:
            outs, errs = tsc.communicate()

            if errs is not None:
                for line in errs:
                    log(line.decode(), src="tsc", level=LEVEL_ERROR)

        if tsc.poll() == 0:
            log("tsc succeeded.", LEVEL_INFO)
        else:
            log(f"tsc failed with error code {tsc.returncode}", LEVEL_WARNING)

    client_path = path.join(path.dirname(file_dir), "client")
    dist_path = path.join(client_path, "dist")

    if not path.exists(dist_path) or \
            getmtime_directory(client_path, lambda f: "node_modules" not in f) > getmtime_directory(dist_path):
        log("new client files detected, running webpack")

        if which("webpack") is None:
            log("webpack not found; installing webpack", LEVEL_INFO)
            webpack_install = sp.run(["npm", "i", "-g", "webpack-cli"], shell=True)

            if webpack_install.returncode == 0:
                log("webpack installed.", LEVEL_INFO)
            else:
                log(f"webpack install failed with error code {webpack_install.returncode}", LEVEL_WARNING)

                for line in webpack_install.stdout:
                    log(line.decode(), src="npm")

        webpack = sp.Popen(["webpack", "--config", "webpack.prod.js"], cwd=client_path, stdout=sp.PIPE, shell=True)

        output = []
        while webpack.poll() is None:
            outs, errs = webpack.communicate()

            if outs is not None:
                output += [(LEVEL_INFO, line.decode()) for line in outs]
            if errs is not None:
                output += [(LEVEL_ERROR, line.decode()) for line in errs]

        if webpack.poll() == 0:
            log("webpack succeeded.", LEVEL_INFO)
        else:
            log(f"webpack failed with error code {webpack.returncode}", LEVEL_WARNING)
            for level, line in output:
                log(line, level=level, src="webpack")

    log("starting web server.", LEVEL_INFO)
    return sp.Popen(["node", "web_server.js"], cwd=web_path, stdout=sp.PIPE, stderr=sp.PIPE)


def start_mqtt_server(args: dict):
    mqtt_path = path.join(file_dir, "controller")

    log("starting MQTT server.", LEVEL_INFO)

    mqtt_args = [which("python3.6") or which("python"), "-u", "server.py"]

    if args.watch:
        mqtt_args.append("--watch")

    return sp.Popen(mqtt_args, cwd=mqtt_path, stdout=sp.PIPE, stderr=sp.PIPE)


def main():
    parser = ap.ArgumentParser(prog="pi-star")
    parser.add_argument("--no-web-server", help="Disables web server.", action="store_true")
    parser.add_argument("--no-mqtt-server", help="Disables MQTT server.", action="store_true")
    parser.add_argument("-w", "--watch", help="Starts MQTT server in watch mode.", action="store_true")
    parser.add_argument("-ar", "--auto-restart", help="Automatically restarts processes if they fail.", action="store_true", default=True)

    args = parser.parse_args()

    print(f"{cr.Fore.BLUE}{cr.Style.BRIGHT}[pi-star v0.3.0]")
    print(f"{cr.Fore.BLUE}[copyright 2018 ibiyemi abiodun, simon abrelat, grace pfohl, sidhesh desai]")

    web_proc = None
    if not args.no_web_server:
        web_proc = start_web_server()

    mqtt_proc = None
    if not args.no_mqtt_server:
        mqtt_proc = start_mqtt_server(args)

    def enqueue_output(out, queue):
        for line in iter(out.readline, b''):
            queue.put((LEVEL_INFO, line.decode().strip()))
        out.close()

    def enqueue_error(out, queue):
        for line in iter(out.readline, b''):
            queue.put((LEVEL_ERROR, line.decode().strip()))
        out.close()

    web_output = Queue()

    def make_web_daemons(queue):
        web_daemon = Thread(target=enqueue_output, args=(web_proc.stdout, queue))
        web_daemon.daemon = True  # thread dies with the program
        web_daemon.start()

        web_daemon_err = Thread(target=enqueue_error, args=(web_proc.stderr, queue))
        web_daemon_err.daemon = True  # thread dies with the program
        web_daemon_err.start()

    make_web_daemons(web_output)

    mqtt_output = Queue()

    def make_mqtt_daemons(queue):
        mqtt_daemon = Thread(target=enqueue_output, args=(mqtt_proc.stdout, queue))
        mqtt_daemon.daemon = True  # thread dies with the program
        mqtt_daemon.start()

        mqtt_daemon_err = Thread(target=enqueue_error, args=(mqtt_proc.stderr, queue))
        mqtt_daemon_err.daemon = True  # thread dies with the program
        mqtt_daemon_err.start()

    make_mqtt_daemons(mqtt_output)

    try:
        while True:
            if web_output.qsize() > 0:
                try:
                    level, msg = web_output.get_nowait()
                    log(msg, level=level, src="web-server")
                except Empty:
                    pass
            elif web_proc is not None and web_proc.poll() is not None:
                log(f"web-server has exited with code {web_proc.returncode}", LEVEL_WARNING)
                web_proc = None

                if args.auto_restart:
                    web_proc = start_web_server()
                    make_web_daemons(web_output)

            if mqtt_output.qsize() > 0:
                try:
                    level, msg = mqtt_output.get_nowait()
                    log(msg, level=level, src="mqtt-server")
                except Empty:
                    pass
            elif mqtt_proc is not None and mqtt_proc.poll() is not None:
                log(f"mqtt-server has exited with code {mqtt_proc.returncode}", LEVEL_WARNING)
                mqtt_proc = None

                if args.auto_restart:
                    mqtt_proc = start_mqtt_server(args)
                    make_mqtt_daemons(mqtt_output)

            sleep(0.1)
    except KeyboardInterrupt:
        log("ctrl-c pressed, exiting")
        if web_proc is not None:
            web_proc.kill()
        if mqtt_proc is not None:
            mqtt_proc.kill()


if __name__ == "__main__":
    main()
