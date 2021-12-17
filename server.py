from flask import Flask, jsonify, request
from logging.config import dictConfig
import chai

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


chai.flask_setup(app)


@app.route("/")
def hello():
    app_name = chai.get_config("app_name", dict(value="CONFIG NOT FOUND"))["value"]
    user_id = request.args.get("user_id", -1, type=int)
    one_user_enabled = chai.percentage_rollout(
        config_name="one_user_enabled", user_id=user_id
    )
    return f"<!doctype html><pre>app name: {app_name}\none_user_enabled: {one_user_enabled}</pre>"


@app.route("/config")
def config():
    return jsonify(chai.get_config("connect_client", dict(error="CONFIG NOT FOUND")))


if __name__ == "__main__":
    app.run()
