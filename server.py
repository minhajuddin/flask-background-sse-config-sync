from flask import Flask, jsonify
import gevent
import urllib3
import io
import json
import atexit
from logging.config import dictConfig
import os

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(process)d][%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            }
        },
        "root": {"level": "INFO", "handlers": ["wsgi"]},
    }
)


app = Flask(__name__)
sync_state = dict(status="init", sync=True, config_status="uninitialized")


def client_id():
    return


def sync_config():
    sync = (True,)
    app.logger.info("starting to sync")
    http = urllib3.PoolManager()
    resp = http.request(
        method="GET",
        url="https://chai.hyperngn.com/config-sse/pypy?env=prod&retailer=fdl",
        headers={
            "accept": "text/event-stream",
            "client-id": f"{os.uname().nodename}-{os.getpid()}",
            "client-version": f"{os.uname().release}{os.uname().version}",
        },
        preload_content=False,
    )
    reader = io.BufferedReader(resp, 8)

    def stop_sync():
        sync[0] = False
        app.logger.info("STOPPING SYNC")
        sync_state.update(sync=False)
        resp.release_conn()

    atexit.register(stop_sync)

    while sync_state["sync"]:
        sync_state.update(status="running")
        #  app.logger.info("syncing ...")
        line = reader.readline().decode()
        if line.startswith("data: "):
            config = json.loads(line[6:].strip())
            if (
                sync_state["config_status"] == "uninitialized"
                or sync_state["config"]["content_hash"] != config["content_hash"]
            ):
                app.logger.info("updating config")
                sync_state.update(config_status="initialized", config=config)
                app.logger.info(sync_state["config"])


sync_state.update(status="spawning")
gevent.spawn(sync_config)


@app.before_first_request
def wait_till_config_ready():
    while sync_state["config_status"] == "uninitialized":
        gevent.sleep(0.01)
    app.logger.info("CONFIG READY")


@app.route("/")
def hello():
    return f"Hello World! sync_state: {sync_state['status']}"


@app.route("/config")
def config():
    return jsonify(sync_state["config"])


if __name__ == "__main__":
    app.run()
