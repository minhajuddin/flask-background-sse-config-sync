from flask import Flask, jsonify
import gevent
import urllib3
import io
import json


app = Flask(__name__)
sync_state = dict(status="init", sync=True, config_status="uninitialized")


def stop_sync():
    print("STOPPING SYNC")
    sync_state.update(sync=False)


def sync_config():
    print("starting to sync")
    http = urllib3.PoolManager()
    resp = http.request(
        method="GET",
        url="https://chai.hyperngn.com/config-sse/pypy?env=prod&retailer=fdl",
        headers={"Accept": "text/event-stream"},
        preload_content=False,
    )
    reader = io.BufferedReader(resp, 8)
    while sync_state["sync"]:
        sync_state.update(status="running")
        print("syncing ...")
        line = reader.readline().decode()
        if line.startswith("data: "):
            config = json.loads(line[6:].strip())
            if (
                sync_state["config_status"] == "uninitialized"
                or sync_state["config"]["content_hash"] != config["content_hash"]
            ):
                print("updating config")
                sync_state.update(config_status="initialized", config=config)
                print(sync_state["config"])


sync_state.update(status="spawning")
gevent.spawn(sync_config)


@app.route("/")
def hello():
    return f"Hello World! sync_state: {sync_state['status']}"


@app.route("/config")
def config():
    return jsonify(sync_state["config"])


if __name__ == "__main__":
    app.run()

import atexit

atexit.register(stop_sync)
