import gevent
import urllib3
import io
import json
import os
import logging
from flask import current_app

state = dict(
    sync=True,
    config=dict(),
    config_initialized=False,
)

# ```
# # Provides a boolean value for the given key.
# new_signup = { rollout: 90 }
#  ```


def percentage_rollout(config_name: str, user_id: int) -> bool:
    # we default to 0% rollout if key is absent
    config = get_config(config_name, dict(rollout=0))
    if isinstance(config["rollout"], int) and isinstance(user_id, int):
        mod_100 = user_id % 100
        return mod_100 < config["rollout"]
    else:
        logging.warn(
            f"rollout or user_id is not an int, user_id: {user_id} {config_name}: {config}, defaulting to false"
        )
        return False


def get_config(key, default):
    return state["config"]["configs"].get(key, default)


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
    start_sync_loop()

    @app.before_first_request
    def wait_till_config_ready():
        while not state["config_initialized"]:
            logging.warn("twiddling thumbs till config is loaded")
            gevent.sleep(1)
        logging.info("config ready")
