import gevent
import urllib3
import io
import json
import os
import logging

state = dict(
    sync=True,
    config=dict(),
    config_initialized=False,
)


def get_config(key, default):
    return state["config"].get(key, default)


# set it up via gunicorn
def stop_sync_loop():
    logging.info("stopping sync")
    state.update(sync=False)


def sync_loop():
    logging.info("starting sync_loop")
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
    resp_buffered_reader = io.BufferedReader(resp, 8)

    while state["sync"]:
        resp_line = resp_buffered_reader.readline().decode()
        if resp_line.startswith("data: "):
            config = json.loads(resp_line[6:].strip())
            if (not state["config_initialized"]) or (
                state["config"]["content_hash"] != config["content_hash"]
            ):
                logging.info("updating config")
                state.update(config_initialized=True, config=config)
                logging.debug(config)


def start_sync_loop():
    logging.debug(state)
    logging.info("starting sync_loop")
    gevent.spawn(sync_loop)
    state.update(sync=True)


def flask_setup(app):
    @app.before_first_request
    def wait_till_config_ready():
        while not state["config_initialized"]:
            logging.warn("twiddling thumbs till config is loaded")
            gevent.sleep(1)
        logging.info("config ready")
